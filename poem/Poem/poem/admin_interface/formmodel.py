from Poem.poem.models import Profile, Metrics, Probe
from django.contrib.admin.widgets import FilteredSelectMultiple
from django.contrib.auth.forms import UserChangeForm, UserCreationForm
from django.contrib.auth import get_user_model
from django.forms import ModelMultipleChoiceField, ModelChoiceField
from django.forms import ValidationError
from django.forms.util import flatatt
from django.forms.widgets import SelectMultiple
from django.utils.encoding import force_unicode, force_text
from django.utils.html import escape
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext as _
from itertools import chain

class MyModelChoiceField(ModelChoiceField):
    def label_from_instance(self, obj):
        return str(obj.name)

class MyModelMultipleChoiceField(ModelMultipleChoiceField):
    def __init__(self, *args, **kwargs):
        self.ftype = kwargs.pop('ftype', None)
        super(ModelMultipleChoiceField, self).__init__(*args, **kwargs)

    def clean(self, value):
        if self.required and not value:
            raise ValidationError(self.error_messages['required'])
        elif not self.required and not value:
            return []
        key = self.to_field_name or 'pk'
        for pk in value:
            try:
                self.queryset.filter(**{key: pk})
            except ValueError:
                raise ValidationError(self.error_messages['invalid_pk_value'] % pk)
        if self.ftype == 'profiles':
            qs = Profile.objects.filter(**{'%s__in' % key: value})
        elif self.ftype == 'metrics':
            qs = Metrics.objects.filter(**{'%s__in' % key: value})
        elif self.ftype == 'probes':
            qs = Probe.objects.filter(**{'%s__in' % key: value})
        else:
            qs = self.queryset.filter(**{'%s__in' % key: value})
        pks = set([force_unicode(getattr(o, key)) for o in qs])
        for val in value:
            if force_unicode(val) not in pks:
                raise ValidationError(self.error_messages['invalid_choice'] % val)
        self.run_validators(value)
        if self.ftype == 'profiles' or self.ftype == 'permissions'\
                or self.ftype == 'metrics'\
                or self.ftype == 'probes':
            return qs
        else:
            return qs[0]

    def label_from_instance(self, obj):
        if self.ftype == 'probes':
            return str(obj.nameversion)
        else:
            return str(obj.name)

    def _has_changed(self, initial, data):
        initial_value = initial if initial is not None else ''
        data_value = data if data is not None else ''
        return force_text(self.prepare_value(initial_value)) != force_text(data_value)

class MySelect(SelectMultiple):
    allow_multiple_selected = False

    def render(self, name, value, attrs=None, choices=()):
        self.selformname = name
        if value is None: value = ''
        final_attrs = self.build_attrs(attrs, name=name)
        output = [u'<select%s>' % flatatt(final_attrs)]
        options = self.render_options(choices, [value])
        if options:
            output.append(options)
        output.append(u'</select>')
        return mark_safe(u'\n'.join(output))

    def render_options(self, choices, selected_choices):
        sel = force_unicode(selected_choices)
        output = []
        for option_value, option_label in chain(self.choices, choices):
            if isinstance(option_label, (list, tuple)):
                output.append(u'<optgroup label="%s">' % escape(force_unicode(option_value)))
                for option in option_label:
                    output.append(self.render_option(selected_choices, *option))
                output.append(u'</optgroup>')
            else:
                output.append(self.render_option(selected_choices, option_value, option_label))
        if self.selformname == 'permissions':
            for o in output:
                if sel.strip('[]') in o:
                    ind = output.index(o)
                    o = o.replace('value=\"%s\"' % (sel.strip('[]')), 'value=\"%s\" selected=\"selected\"' % (sel.strip('[]')))
                    del(output[ind])
                    output.insert(ind, o)
        return u'\n'.join(output)

class MyUserChangeForm(UserChangeForm):
    def __init__(self, *args, **kwargs):
        super(MyUserChangeForm, self).__init__(*args, **kwargs)
        self.fields['groupsofmetrics'].widget.can_add_related = False
        self.fields['groupsofprobes'].widget.can_add_related = False
        self.fields['groupsofprofiles'].widget.can_add_related = False

    class Meta:
        model = get_user_model()
        fields = '__all__'

class MyUserCreationForm(UserCreationForm):
    class Meta:
        model = get_user_model()
        fields = ('username', )

    def clean_username(self):
        username = self.cleaned_data["username"]
        try:
            get_user_model()._default_manager.get(username=username)
        except get_user_model().DoesNotExist:
            return username
        raise forms.ValidationError(
            self.error_messages['duplicate_username'],
            code='duplicate_username',
        )

class MyFilteredSelectMultiple(FilteredSelectMultiple):
    def render(self, name, value, attrs=None, choices=()):
        self.selformname = name
        return super(MyFilteredSelectMultiple, self).render(name, value, attrs, choices)

    def render_options(self, choices, selected_choices):
        selected_choices = set(force_unicode(v) for v in selected_choices)
        output = []
        if self.selformname == 'profiles':
            for sel in selected_choices:
                output.append('<option value="%s" selected="selected">' % (sel)
                              + str(Profile.objects.get(id=int(sel)).name)
                              + '</option>\n')
        elif self.selformname == 'metrics':
            for sel in selected_choices:
                output.append('<option value="%s" selected="selected">' % (sel)
                              + str(Metrics.objects.get(id=int(sel)).name)
                              + '</option>\n')
        elif self.selformname == 'probes':
            for sel in selected_choices:
                output.append('<option value="%s" selected="selected">' % (sel)
                              + str(Probe.objects.get(pk=sel).name)
                              + '</option>\n')
        for option_value, option_label in chain(self.choices, choices):
            if isinstance(option_label, (list, tuple)):
                output.append(u'<optgroup label="%s">' % escape(force_unicode(option_value)))
                for option in option_label:
                    output.append(self.render_option(selected_choices, *option))
                output.append(u'</optgroup>')
            else:
                output.append(self.render_option(selected_choices, option_value, option_label))
        return u'\n'.join(filter(lambda x: '----' not in x, output))
