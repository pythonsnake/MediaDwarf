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

import logging
from mediagoblin.db.models import User

_log = logging.getLogger(__name__)


def setup_user_in_request(request):
    """
    Examine a request and tack on a request.user parameter if that's
    appropriate.
    """
    if 'user_id' not in request.session:
        request.user = None
        return

    request.user = User.query.get(request.session['user_id'])

    if not request.user:
        # Something's wrong... this user doesn't exist?  Invalidate
        # this session.
        _log.warn("Killing session for user id %r", request.session['user_id'])
        request.session.delete()

def validate_query_params(params, required, extra, drop_unknown=True):
    """Check if the query parameters are valid.
    Returns a query parameters dictionary that can safely be used.
    If `drop_unknown` is set to `True` (which is the default)
    any unspecified parameters are dropped automatically..

    The exception raised provides three attributes:

    `missing`
        A set of parameter names expected (present in `required`) but were
        missing.

    `invalid`
        A dictionary of parameters that are invalid.

    `unknown`
        A dictionary of parameters that aren't in `required` or `extra`

    :param params: the dictionary of pprovided query parameters
    :param required: a dictionary of structure {param_name: func}
                     where`param_name` is the parameter's name string
                     and `func` the function the validation is performed against.
    :param extra: same as `required`, but doesn't raise the exception if any of it is missing.
    :param drop_unknown: set to `False` if you want unknown parameters to be silently dropped.
    """
    valid = {}
    missing = required.keys()
    invalid = {}
    unknown = {}

    for i in params:
        if i in required:
            missing.remove(i)
            try:
                required[i](params[i])
                valid[i] = params[i]
            except:
                invalid[i] = params[i]
        elif i in extra:
            try:
                extra[i](params[i])
                valid[i] = params[i]
            except:
                invalid[i] = params[i]
        elif not drop_unknown:
            unknown[i] = params[i]

    if missing or invalid or unknown:
        raise ParamsValidationError(missing, invalid, unknown)
    else:
        return valid

class ParamsValidationError(ValueError):
    """Raised if :func:`validate_query_params` fails to validate"""

    def __init__(self, missing=None, invalid=None, unknown=None):
        self.missing = missing or {}
        self.invalid = invalid or {}
        self.unknown = unknown or {}
        ValueError.__init__(self, 'Query parameters invalid.  ('
                            '%d missing, %d invalid, %d unknown)' % (
            len(self.missing),
            len(self.invalid),
            len(self.unknown)
        ))
