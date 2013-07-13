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

from urlparse import urljoin

from werkzeug.utils import HTMLBuilder

from mediagoblin.media_types import MediaManagerBase
from mediagoblin.media_types.video.processing import process_video, \
    sniff_handler
from mediagoblin.plugins.api.tools import get_media_file_paths


class VideoMediaManager(MediaManagerBase):
    human_readable = "Video"
    processor = staticmethod(process_video)
    sniff_handler = staticmethod(sniff_handler)
    display_template = "mediagoblin/media_displays/video.html"
    embed_template = "mediagoblin/media_displays/video_embed.html"
    default_thumb = "images/media_thumbs/video.jpg"
    accepted_extensions = [
        "mp4", "mov", "webm", "avi", "3gp", "3gpp", "mkv", "ogv", "m4v"]

    # Used by the media_entry.get_display_media method
    media_fetch_order = [u'webm_640', u'original']
    default_webm_type = 'video/webm; codecs="vp8, vorbis"'

    def oembed_func(self, request, query_params):
        r_params = self.init_oembed(request, query_params)

        html = self.get_embed_html(request, r_params)

        r_params.update({
            'type': 'video', 
            'html': html,
            'url': get_media_file_paths(
                self.entry.media_files, request.urlgen)['webm_640']})

        return r_params



MEDIA_MANAGER = VideoMediaManager
