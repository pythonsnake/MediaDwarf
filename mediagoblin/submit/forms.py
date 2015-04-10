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

from mediagoblin import mg_globals
from mediagoblin.tools.text import tag_length_validator
from mediagoblin.tools.translate import lazy_pass_to_ugettext as _
from mediagoblin.tools.licenses import licenses_as_choices


class SelectWithDescription(wtforms.widgets.Select):
    def __call__(self, field, **kwargs):
        kwargs.setdefault('id', field.id)
        # Descriptions' dict so we don't have to iter_choices twice
        d = {}
        if self.multiple:
            kwargs['multiple'] = True
        html = ['<select %s>' % html_params(name=field.name, **kwargs)]
        for value, label, descr, index, selected in field.iter_choices():
            html.append(self.render_option(value, label, selected, index=index))
            d[index] = descr
        html.append('</select>')
        html.append(u'<div %s>' % html_params(class_="form_field_description", id="hide-all", style="display:none"))
        for i in d:
            html.append(u'<div %s>%s</div>' % (html_params(id='d_'+str(i)), d[i]))
        html.append(u'</div>')
        return HTMLString(''.join(html))

    @classmethod
    def render_option(cls, value, label, selected, **kwargs):
        options = dict(kwargs, value=value)
        if selected:
            options['selected'] = True
        options['data-id'] = kwargs['index']
        return HTMLString('<option %s>%s</option>' % (html_params(**options), escape(text_type(label))))


class SelectFieldWithDescription(wtforms.SelectMultipleField):
    widget = SelectWithDescription(multiple=False)

    def iter_choices(self):
        for value, label, descr, index in self.choices:
            selected = self.data is not None and self.coerce(value) in self.data
            yield (value, label, descr, index, selected)

def get_submit_start_form(form, **kwargs):
    max_file_size = kwargs.get('max_file_size')
    desc = None
    if max_file_size:
        desc = _('Max file size: {0} mb'.format(max_file_size))

    class SubmitStartForm(wtforms.Form):
        file = wtforms.FileField(
            _('File'),
            description=desc)
        title = wtforms.TextField(
            _('Title'),
            [wtforms.validators.Length(min=0, max=500)])
        description = wtforms.TextAreaField(
            _('Description of this work'),
            description=_("""You can use
                        <a href="http://daringfireball.net/projects/markdown/basics">
                        Markdown</a> for formatting."""))
        tags = wtforms.TextField(
            _('Tags'),
            [tag_length_validator],
            description=_(
            "Separate tags by commas."))
        license = SelectFieldWithDescription(
            _('License'),
            [wtforms.validators.Optional(),],
            choices=licenses_as_choices())
        max_file_size = wtforms.HiddenField('')
        upload_limit = wtforms.HiddenField('')
        uploaded = wtforms.HiddenField('')

    return SubmitStartForm(form, **kwargs)

class AddCollectionForm(wtforms.Form):
    title = wtforms.TextField(
        _('Title'),
        [wtforms.validators.Length(min=0, max=500), wtforms.validators.InputRequired()])
    description = wtforms.TextAreaField(
        _('Description of this collection'),
        description=_("""You can use
                      <a href="http://daringfireball.net/projects/markdown/basics">
                      Markdown</a> for formatting."""))
