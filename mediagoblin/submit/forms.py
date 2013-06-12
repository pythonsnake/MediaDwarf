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


import wtforms
from wtforms.widgets import html_params, HTMLString     
from cgi import escape                                  
from webtest.compat import text_type                    

from mediagoblin.tools.text import tag_length_validator
from mediagoblin.tools.translate import lazy_pass_to_ugettext as _
from mediagoblin.tools.licenses import licenses_as_choices


class MultipleFileInput(object):
    def __call__(self, field, **kwargs):
        kwargs.setdefault('id', field.id)
        value = field._value()
        html = [u'<input %s>' % html_params(name="file[]", type="file", multiple=True, style="display: none;", \
                **kwargs)]
        html.append(u'<input %s>' % html_params(class_="button_action", type="button", value="Browse...", \
                    onclick="$('#file').click();", style="width:auto;", **kwargs))
        html.append(u'<span %s> or drop the file here</span>' % html_params(class_="form_field_description"))
        if value:
            kwargs.setdefault('value', value)
        return HTMLString(u''.join(html))

class MultipleFileField(wtforms.FileField):
    widget = MultipleFileInput()

class SubmitStartForm(wtforms.Form):
    file = MultipleFileField(_('File'))

class SubmitOptionsForm(wtforms.Form):
    tags = wtforms.TextField(
        _('Tags'),
        [tag_length_validator],
        description=_(
          "Separate tags by commas."))
    license = wtforms.SelectField(
        _('License'),
        [wtforms.validators.Optional(),],
        choices=licenses_as_choices())

class AddCollectionForm(wtforms.Form):
    title = wtforms.TextField(
        _('Title'),
        [wtforms.validators.Length(min=0, max=500), wtforms.validators.Required()])
    description = wtforms.TextAreaField(
        _('Description of this collection'),
        description=_("""You can use
                      <a href="http://daringfireball.net/projects/markdown/basics">
                      Markdown</a> for formatting."""))
