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

import os

from mediagoblin.gmg_commands import util as commands_util
from mediagoblin.submit.lib import (
    submit_media,
    FileUploadLimit, UserUploadLimit, UserPastUploadLimit)

from mediagoblin import mg_globals


def parser_setup(subparser):
    subparser.add_argument(
        'username',
        help="Name of user this media entry belongs to")
    subparser.add_argument(
        'filename',
        help="Local file on filesystem")
    subparser.add_argument(
        "-d", "--description",
        help="Description for this media entry")
    subparser.add_argument(
        "-t", "--title",
        help="Title for this media entry")
    subparser.add_argument(
        "-l", "--license",
        help=(
            "License this media entry will be released under. "
            "Uses user defaults if unspecified."))
    subparser.add_argument(
        "-T", "--tags",
        help=(
            "Comma separated list of tags for this media entry."))
    subparser.add_argument(
        "-s", "--slug",
        help=(
            "Slug for this media entry. "
            "Will be autogenerated if unspecified."))

    subparser.add_argument(
        '--celery',
        action='store_true',
        help="Don't process eagerly, pass off to celery")


def addmedia(args):
    # Run eagerly unless explicetly set not to
    if not args.celery:
        os.environ['CELERY_ALWAYS_EAGER'] = 'true'

    app = commands_util.setup_app(args)

    # get the user
    user = app.db.User.query.filter_by(username=args.username.lower()).first()
    if user is None:
        print "Sorry, no user by username '%s'" % args.user
        return
    
    # check for the file, if it exists...
    filename = os.path.abspath(args.filename)
    if not os.path.exists(filename):
        print "Can't find a file by that filename?"
        return

    if user.upload_limit >= 0:
        upload_limit = user.upload_limit
    else:
        upload_limit = mg_globals.app_config.get('upload_limit', None)

    max_file_size = mg_globals.app_config.get('max_file_size', None)

    try:
        submit_media(
            mg_app=app,
            user=user,
            submitted_file=file(filename, 'r'), filename=filename,
            title=args.title, description=args.description,
            license=args.license, tags_string=args.tags or u'',
            upload_limit=upload_limit, max_file_size=max_file_size)
    except FileUploadLimit:
        print "This file is larger than the upload limits for this site."
    except UserUploadLimit:
        print "This file will put this user past their upload limits."
    except UserPastUploadLimit:
        print "This user is already past their upload limits."