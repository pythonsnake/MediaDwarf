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

from collections import namedtuple
# dict {uri: License,...} to enable fast license lookup by uri. Ideally,
License = namedtuple("License", ["abbreviation", "name", "uri", "descr"])

SORTED_LICENSES = [
    License("All rights reserved", "No license specified", "",
        "The copyright holder reserves, or holds for their own use, \
                all the rights provided by copyright law, such as distribution, \
                performance, and creation of derivative works;\
                that is, they have not waived any such right."),
    License("CC BY 3.0", "Creative Commons Attribution Unported 3.0",
           "http://creativecommons.org/licenses/by/3.0/",
           "This license lets others distribute, remix, tweak, and build upon your work, \
                   even commercially, as long as they credit you for the original creation. \
                   This is the most accommodating of licenses offered. \
                   Recommended for maximum dissemination and use of licensed materials."),
    License("CC BY-SA 3.0",
           "Creative Commons Attribution-ShareAlike Unported 3.0",
           "http://creativecommons.org/licenses/by-sa/3.0/",
           "This license lets others remix, tweak, and build upon your work even for commercial purposes, \
                   as long as they credit you and license their new creations under the identical terms. \
                   This is the license used by Wikipedia, and is recommended for materials that would benefit \
                   from incorporating content from Wikipedia and similarly licensed projects."),
    License("CC BY-ND 3.0",
           "Creative Commons Attribution-NoDerivs 3.0 Unported",
           "http://creativecommons.org/licenses/by-nd/3.0/",
           "This license allows for redistribution, commercial and non-commercial, \
                   as long as it is passed along unchanged and in whole, with credit to you."),
    License("CC BY-NC 3.0",
          "Creative Commons Attribution-NonCommercial Unported 3.0",
          "http://creativecommons.org/licenses/by-nc/3.0/",
          "This license lets others remix, tweak, and build upon your work non-commercially, \
                  and although their new works must also acknowledge you and be non-commercial,\
                  they don't have to license their derivative works on the same terms."),
    License("CC BY-NC-SA 3.0",
           "Creative Commons Attribution-NonCommercial-ShareAlike 3.0 Unported",
           "http://creativecommons.org/licenses/by-nc-sa/3.0/",
           "This license lets others remix, tweak, and build upon your work non-commercially, \
                   as long as they credit you and license their new creations under the identical terms."),
    License("CC BY-NC-ND 3.0",
           "Creative Commons Attribution-NonCommercial-NoDerivs 3.0 Unported",
           "http://creativecommons.org/licenses/by-nc-nd/3.0/",
           "This license only allows others to download your works and share them with others as long as they credit you, \
                   but they can't change them in any way or use them commercially."),
    License("CC0 1.0",
           "Creative Commons CC0 1.0 Universal",
           "http://creativecommons.org/publicdomain/zero/1.0/",
           "The person who associated a work with this deed has dedicated the work to the public domain \
                   by waiving all of his or her rights to the work worldwide under copyright law, \
                   including all related and neighboring rights, to the extent allowed by law. (deprecated)"),
    License("Public Domain","Public Domain",
           "http://creativecommons.org/publicdomain/mark/1.0/",
           "The work will be identified as being free of known restrictions under copyright law, \
                   including all related and neighboring rights. (not recommended by CC)"),
    ]

# we'd want to use an OrderedDict (python 2.7+) here to avoid having the
# same data in two structures
SUPPORTED_LICENSES = dict(((l.uri, l) for l in SORTED_LICENSES))


def get_license_by_url(url):
    """Look up a license by its url and return the License object"""
    try:
        return SUPPORTED_LICENSES[url]
    except KeyError:
        # in case of an unknown License, just display the url given
        # rather than exploding in the user's face.
        return License(url, url, url)


def licenses_as_choices():
    """List of (uri, abbreviation) tuples for HTML choice field population

    The data seems to be consumed/deleted during usage, so hand over a
    throwaway list, rather than just a generator.
    """
    return [(lic.uri, lic.abbreviation, lic.descr, index) for index, lic in enumerate(SORTED_LICENSES)]
