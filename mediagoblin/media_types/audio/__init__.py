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

from mediagoblin.media_types import MediaManagerBase
from mediagoblin.media_types.audio.processing import process_audio, \
    sniff_handler
from mediagoblin.plugins.api.tools import get_media_file_paths


class AudioMediaManager(MediaManagerBase):
    human_readable = "Audio"
    processor = staticmethod(process_audio)
    sniff_handler = staticmethod(sniff_handler)
    display_template = "mediagoblin/media_displays/audio.html"
    embed_template = "mediagoblin/media_displays/audio_embed.html"
    accepted_extensions = ["mp3", "flac", "wav", "m4a"]

    def oembed_func(self, request, query_params):
        r_params = self.init_oembed(request, query_params)
        html = get_embed_html(request, query_params)

        r_params.update({
            'type': 'video',
            'html': html,
            'url': get_media_file_paths(
                self.entry.media_files, 
                request.urlgen)['webm_audio']})

        return r_params


MEDIA_MANAGER = AudioMediaManager
