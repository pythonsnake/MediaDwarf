'use strict';
/**
 * GNU MediaGoblin -- federated, autonomous media hosting
 * Copyright (C) 2011, 2012 MediaGoblin contributors.  See AUTHORS.
 *
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU Affero General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU Affero General Public License for more details.
 *
 * You should have received a copy of the GNU Affero General Public License
 * along with this program.  If not, see <http://www.gnu.org/licenses/>.
 */

var notifications = {};

(function (n) {
    n._base = '/';
    n._endpoint = 'notifications/json';

    n.init = function () {
        $('.notification-gem').on('click', function () {
            $('.header_dropdown_down:visible').click();
        });
    }

})(notifications)

$(document).ready(function () {
    notifications.init();

    var mark_all_comments_seen = document.getElementById('mark_all_comments_seen');

    if (mark_all_comments_seen) {
        mark_all_comments_seen.href = '#';
        mark_all_comments_seen.onclick = function() {
            $.ajax({
                type: 'GET',
                url: mark_all_comments_seen_url,
                success: function(res, status, xhr) { window.location.reload(); },
            });
        }
    }
});
