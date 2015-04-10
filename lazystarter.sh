#!/bin/sh

# GNU MediaGoblin -- federated, autonomous media hosting
# Copyright (C) 2011 Free Software Foundation, Inc
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

selfname=$(basename "$0")
local_bin="./bin"

# Test whether or not gunicorn is installed
# -----------------------------------------
if [ -f "${local_bin}/python" ]; then
    our_python="${local_bin}/python";
else
    our_python="python";
fi

if $our_python -c "import sys
try:
    import gunicorn
    sys.exit(0)
except ImportError:
    sys.exit(1)
"; then
    use_gunicorn=true;
else
    use_gunicorn=false;
fi
# -----------------------------------------

case "$selfname" in
    lazyserver.sh)
        if $use_gunicorn; then
            starter_cmd=gunicorn;
        else
            starter_cmd=paster;
        fi
        ini_prefix=paste
        ;;
    lazycelery.sh)
        starter_cmd=celeryd
        ini_prefix=mediagoblin
        ;;
    *)
        echo "Start this script with the name lazyserver.sh or lazycelery.sh">&2
        exit 1
        ;;
esac

if [ "$1" = "-h" ]; then
    echo "$0 [-h] [-c filename.ini] [ARGS_to_${starter_cmd} ...]"
    echo ""
    if $use_gunicorn; then
        echo "   For Gunicorn settings, see at:"
        echo "      http://docs.gunicorn.org/en/19.0/settings.html"
    else
        echo "   For example:"
        echo "         $0 -c fcgi.ini port_number=23371"
        echo "     or: $0 --server-name=fcgi --log-file=paste.log"
    fi
    echo ""
    echo "   The configfile defaults to ${ini_prefix}_local.ini,"
    echo "   if that is readable, otherwise ${ini_prefix}.ini."
    exit 1
fi

if [ "$1" = "-c" ]; then
    ini_file=$2
    shift; shift
elif [ -r "${ini_prefix}_local.ini" ]; then
    ini_file="${ini_prefix}_local.ini"
else
    ini_file="${ini_prefix}.ini"
fi

echo "Using ${starter_cmd} config: ${ini_file}"

if [ -f "${local_bin}/${starter_cmd}" ]; then
    echo "Using ${local_bin}/${starter_cmd}"
    starter="${local_bin}/${starter_cmd}"
elif which "${starter_cmd}" > /dev/null; then
    echo "Using ${starter_cmd} from \$PATH"
    starter=$starter_cmd
else
    echo "No ${starter_cmd} found, exiting! X_X"
    exit 1
fi

# If the user somehow doesn't have a mediagoblin.ini
# (maybe they aren't using make) give them one
#   ... this doesn't fulfill all conditions maybe, but is a stopgap
#   that doesn't have noticable race conditions
if [ -f mediagoblin.example.ini ] && \
    [ ! -f mediagoblin.ini ]; then
    echo "No mediagoblin.ini found, making one";
    cp --no-clobber mediagoblin.example.ini mediagoblin.ini;
fi

set -x
export CELERY_ALWAYS_EAGER=true
case "$selfname" in
    lazyserver.sh)
        if $use_gunicorn; then
            $starter --paste "$ini_file" --log-file=- $@;
        else
            $starter serve "$ini_file" "$@" --reload;
        fi
        ;;
    lazycelery.sh)
        MEDIAGOBLIN_CONFIG="${ini_file}" \
            CELERY_CONFIG_MODULE=mediagoblin.init.celery.from_celery \
            $starter -B "$@"
        ;;
    *) exit 1 ;;
esac
