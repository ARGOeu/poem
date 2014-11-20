"""
Custom widgets for POEM Admin interface.
"""
# widgets.py
from itertools import chain

from django import forms
from django.forms import util
from django.utils.html import escape, conditional_escape
from django.utils.encoding import smart_unicode, force_unicode
from django.utils.safestring import mark_safe
from django.conf import settings
from django.core.urlresolvers import reverse

# from taggit.utils import edit_string_for_tags

# from Poem.poem.models import GroupReference

class JQueryAutoComplete(forms.TextInput):
    """
    jQuery autocomplete for forms.TextInput.

    For available options see the autocomplete sample page::
        http://jquery.bassistance.de/autocomplete/
    """
    def __init__(self, options={}, attrs={}):
        self.options = options
        self.attrs = {'autocomplete': 'on'}
        self.attrs.update(attrs)

    def render_js(self, field_id):
        options = ','.join(' %s: %s' % (key, value) for
                                    key,value in self.options.items())

        return u'$(\'#%s\').autocomplete( {%s} );' % (field_id, options)

    def render(self, name, value=None, attrs=None):
        final_attrs = self.build_attrs(attrs, name=name)
        if value:
            final_attrs['value'] = escape(smart_unicode(value))

        if not self.attrs.has_key('id'):
            final_attrs['id'] = 'id_%s' % name

        return mark_safe('''<input type="text" %(attrs)s/>
              <script type="text/javascript">
                      %(js)s
              </script>''' % {'attrs': util.flatatt(final_attrs),
                              'js': self.render_js(final_attrs['id'])})


class FilteredSelectMultiple2(forms.SelectMultiple):
    class Media:
        js = (settings.ADMIN_MEDIA_PREFIX + "js/core.js",
              settings.ADMIN_MEDIA_PREFIX + "js/SelectBox.js",
              settings.ADMIN_MEDIA_PREFIX + "js/SelectFilter2.js")

    def __init__(self, verbose_name, is_stacked, attrs=None, choices=()):
        self.verbose_name = verbose_name
        self.is_stacked = is_stacked
        super(FilteredSelectMultiple2, self).__init__(attrs, choices)

    def render(self, name, value, attrs=None, choices=()):
        output = [super(FilteredSelectMultiple2, self).render(name, value, attrs, choices)]
        output.append(u'<script type="text/javascript">')
        output.append(u'var t = []; $(".red_row").each(function(i, item) { t[i] = $(item).val() }); ')
        output.append(u' addEvent(window, "load", function(e) {')
        output.append(u'SelectFilter.init("id_%s", "%s", %s, "%s"); });' % \
            (name, self.verbose_name.replace('"', '\\"'), int(self.is_stacked), settings.ADMIN_MEDIA_PREFIX))
        output.append(u'$(function() {setTimeout(function() { $.each(window.t, function(i, item) { $("#id_groups_to option[value="+item+"]").css("color","red"); $("#id_groups_from option[value="+item+"]").css("color","red"); }); }, 2000 );} );')
        output.append(u'</script>\n' )
        return mark_safe(u''.join(output))

    def render_options(self, choices, selected_choices):
        def render_option(option_value, option_label):
            option_value = force_unicode(option_value)
            selected_html = (option_value in selected_choices) and u' selected="selected"' or ''
            # if selected_html and GroupReference.objects.get(id=int(option_value)).is_deleted=='Y':
            #    selected_html = u' class="red_row" %s' % selected_html
            # return u'<option value="%s"%s>%s</option>' % (
            #    escape(option_value), selected_html,
            #    conditional_escape(force_unicode(option_label)))
        # Normalize to strings.
        selected_choices = set([force_unicode(v) for v in selected_choices])
        output = []
        for option_value, option_label in chain(self.choices, choices):
            if isinstance(option_label, (list, tuple)):
                output.append(u'<optgroup label="%s">' % escape(force_unicode(option_value)))
                for option in option_label:
                    output.append(render_option(*option))
                output.append(u'</optgroup>')
            else:
                output.append(render_option(option_value, option_label))
        return u'\n'.join(output)

class NamespaceTextInput(forms.TextInput):
    """
    Widget adding namespace to the profile name.
    """
    def render(self, name, value, attrs=None):
        output = super(NamespaceTextInput, self).render(name, value, attrs)
        return mark_safe(u'<span class="namespace">%s-</span> %s' % (settings.POEM_NAMESPACE, output) )
