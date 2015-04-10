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
from mediagoblin.media_types.audio.processing import AudioProcessingManager, \
    sniff_handler
from mediagoblin.tools import pluginapi
from mediagoblin.plugins.api.tools import get_media_file_paths

# Why isn't .ogg in this list?  It's still detected, but via sniffing,
# .ogg files could be either video or audio... sniffing determines which.

ACCEPTED_EXTENSIONS = ["mp3", "flac", "wav", "m4a"]
MEDIA_TYPE = 'mediagoblin.media_types.audio'


def setup_plugin():
    config = pluginapi.get_config(MEDIA_TYPE)


class AudioMediaManager(MediaManagerBase):
    human_readable = "Audio"
    display_template = "mediagoblin/media_displays/audio.html"
    embed_template = "mediagoblin/media_displays/audio_embed.html"

    def oembed_func(self, request, query_params):
        r_params = self.init_oembed(request, query_params)
        html = self.get_embed_html(request, r_params)

        r_params.update({
            'type': 'rich',
            'html': html,
            'url': get_media_file_paths(
                self.entry.media_files, 
                request.urlgen)['webm_audio']})

        return r_params

    default_thumb = "images/media_thumbs/image.png"


def get_media_type_and_manager(ext):
    if ext in ACCEPTED_EXTENSIONS:
        return MEDIA_TYPE, AudioMediaManager

hooks = {
    'setup': setup_plugin,
    'get_media_type_and_manager': get_media_type_and_manager,
    'sniff_handler': sniff_handler,
    ('media_manager', MEDIA_TYPE): lambda: AudioMediaManager,
    ('reprocess_manager', MEDIA_TYPE): lambda: AudioProcessingManager,
}
