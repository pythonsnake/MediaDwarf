# GNU MediaGoblin -- federated, autonomous media hosting
# Copyright (C) 2011, 2012 MediaGoblin contributors.  See AUTHORS.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import pytz
import datetime

from werkzeug.datastructures import FileStorage

from .resources import GOOD_JPG
from mediagoblin.db.base import Session
from mediagoblin.media_types import sniff_media
from mediagoblin.submit.lib import new_upload_entry
from mediagoblin.submit.task import collect_garbage
from mediagoblin.db.models import User, MediaEntry, MediaComment
from mediagoblin.tests.tools import fixture_add_user, fixture_media_entry


def test_404_for_non_existent(test_app):
    res = test_app.get('/does-not-exist/', expect_errors=True)
    assert res.status_int == 404

def test_delete_comments(test_app):
    user_a = fixture_add_user(u"pikachu", password='123',
                              privileges=[u'active',u'uploader', u'commenter'])
    user_b = fixture_add_user(u"ditto", password='123',
                              privileges=[u'active',u'uploader', u'commenter'])
    user_c = fixture_add_user(u"mew", password='123',
                              privileges=[u'active',u'uploader', u'commenter', u'admin'])

    # Login
    test_app.post('/auth/login/', {
        'username': u'pikachu',
        'password': '123'})

    media_a = fixture_media_entry(uploader=user_a.id, save=False,
                                  expunge=False, fake_upload=False)
    Session.add(media_a)
    Session.flush()

    for u_id in (user_a.id, user_b.id):
        cmt = MediaComment()
        cmt.media_entry = media_a.id
        cmt.author = u_id
        cmt.content = u"I'm an awesome pokemon!"
        Session.add(cmt)
    Session.flush()

    # We have 2 comments from each user
    assert MediaComment.query.count() == 2

    # User can delete its own comment
    test_app.post('/c/1/confirm-delete/',
          {'confirm': 'y'})
    assert MediaComment.query.count() == 1

    # Others can't
    resp = test_app.get('/c/2/confirm-delete/',
                        expect_errors=True)
    assert resp.status_int == 403

    # But admin can
    test_app.get('/auth/logout/')
    test_app.post('/auth/login/', {
        'username': u'mew',
        'password': '123'})
    test_app.post('/c/2/confirm-delete/',
          {'confirm': 'y'})
    assert MediaComment.query.count() == 0

def test_deleting_user_deletes_comments(test_app):
    """Testing if deleting user deletes its comments too
    """
    user_a = fixture_add_user(u"chris_a")
    user_b = fixture_add_user(u"chris_b")

    media_a = fixture_media_entry(uploader=user_a.id, save=False,
                                  expunge=False, fake_upload=False)
    media_b = fixture_media_entry(uploader=user_b.id, save=False,
                                  expunge=False, fake_upload=False)
    Session.add(media_a)
    Session.add(media_b)
    Session.flush()

    # Create all 4 possible comments:
    for u_id in (user_a.id, user_b.id):
        for m_id in (media_a.id, media_b.id):
            cmt = MediaComment()
            cmt.media_entry = m_id
            cmt.author = u_id
            cmt.content = u"Some Comment"
            Session.add(cmt)

    Session.flush()

    usr_cnt1 = User.query.count()
    med_cnt1 = MediaEntry.query.count()
    cmt_cnt1 = MediaComment.query.count()

    User.query.get(user_a.id).delete(commit=False)

    usr_cnt2 = User.query.count()
    med_cnt2 = MediaEntry.query.count()
    cmt_cnt2 = MediaComment.query.count()

    # One user deleted
    assert usr_cnt2 == usr_cnt1 - 1
    # One media gone
    assert med_cnt2 == med_cnt1 - 1
    # Three of four comments gone.
    assert cmt_cnt2 == cmt_cnt1 - 3

    User.query.get(user_b.id).delete()

    usr_cnt2 = User.query.count()
    med_cnt2 = MediaEntry.query.count()
    cmt_cnt2 = MediaComment.query.count()

    # All users gone
    assert usr_cnt2 == usr_cnt1 - 2
    # All media gone
    assert med_cnt2 == med_cnt1 - 2
    # All comments gone
    assert cmt_cnt2 == cmt_cnt1 - 4


def test_media_deletes_broken_attachment(test_app):
    user_a = fixture_add_user(u"chris_a")

    media = fixture_media_entry(uploader=user_a.id, save=False, expunge=False)
    media.attachment_files.append(dict(
            name=u"some name",
            filepath=[u"does", u"not", u"exist"],
            ))
    Session.add(media)
    Session.flush()

    MediaEntry.query.get(media.id).delete()
    User.query.get(user_a.id).delete()

def test_garbage_collection_task(test_app):
    """ Test old media entry are removed by GC task """
    user = fixture_add_user()

    # Create a media entry that's unprocessed and over an hour old.
    entry_id = 72
    now = datetime.datetime.now(pytz.UTC)
    file_data = FileStorage(
        stream=open(GOOD_JPG, "rb"),
        filename="mah_test.jpg",
        content_type="image/jpeg"
    )

    # Find media manager
    media_type, media_manager = sniff_media(file_data, "mah_test.jpg")
    entry = new_upload_entry(user)
    entry.id = entry_id
    entry.title = "Mah Image"
    entry.slug = "slugy-slug-slug"
    entry.media_type = 'image'
    entry.created = now - datetime.timedelta(days=2)
    entry.save()

    # Validate the model exists
    assert MediaEntry.query.filter_by(id=entry_id).first() is not None

    # Call the garbage collection task
    collect_garbage()

    # Now validate the image has been deleted
    assert MediaEntry.query.filter_by(id=entry_id).first() is None
