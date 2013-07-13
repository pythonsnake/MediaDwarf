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

from urlparse import urlparse

from werkzeug.exceptions import NotFound
from werkzeug.routing import RequestRedirect
from werkzeug.utils import append_slash_redirect

from mediagoblin.db.models import MediaEntry, User
from mediagoblin.tools.response import render_404, append_slash_redirect
from mediagoblin.tools.request import validate_query_params, ParamsValidationError
from mediagoblin.plugins.api.tools import json_response, xml_response


REQUIRED_PARAMS = {"url": unicode}
EXTRA_PARAMS = {"maxheight": int, "maxwidth": int, "format": unicode}

def media_oembed(request):
    # Validate url params and strip the dict from None values
    args = dict((k, v) for (k, v) in request.args.iteritems() if v)
    try:
        params = validate_query_params(args, REQUIRED_PARAMS, EXTRA_PARAMS)
    except ParamsValidationError:
        return render_404(request)

    url = request.args['url']
    url = urlparse(url).path

    try:
        found_rule, matchdict = request.map_adapter.match(url, return_rule=True)
    except RequestRedirect:
        return append_slash_redirect(request, ['url'])
    else:
        if found_rule.endpoint != "mediagoblin.user_pages.media_home":
            return render_404(request)

    # Get the MediaEntry from the url's path
    user = User.query.filter_by(username=matchdict['user']).first()
    if not user:
        return render_404(request)

    media = None

    # might not be a slug, might be an id, but whatever
    media_slug = matchdict['media']

    # if it starts with id: it actually isn't a slug, it's an id.
    if media_slug.startswith(u'id:'):
        try:
            media = MediaEntry.query.filter_by(
                id=int(media_slug[3:]),
                state=u'processed',
                uploader=user.id).first()
        except ValueError:
            return render_404(request)
    else:
        # no magical id: stuff?  It's a slug!
        media = MediaEntry.query.filter_by(
            slug=media_slug,
            state=u'processed',
            uploader=user.id).first()

    if not media:
        # Didn't find anything?  Okay, 404.
        return render_404(request)

    oembed_func = media.media_manager.oembed_func

    if oembed_func:
        oembed_dict = oembed_func(request, params)
        if params.get("format") == "xml":
            return xml_response(oembed_dict)
        else:
            return json_response(oembed_dict)
    else:
        return render_404(request)
