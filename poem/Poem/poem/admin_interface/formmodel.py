from Poem.poem.models import Profile, Metrics, Probe
from django.contrib.admin.widgets import FilteredSelectMultiple
from django.contrib.auth.forms import UserChangeForm, UserCreationForm
from django.contrib.auth import get_user_model
from django.forms import ModelMultipleChoiceField, ModelChoiceField
from django.forms import ValidationError
from django.forms.utils import flatatt
from django.forms.widgets import SelectMultiple
from django.utils.encoding import force_str, force_text
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

    def label_from_instance(self, obj):
        if self.ftype == 'probes':
            return str(obj.nameversion)
        else:
            return str(obj.name)


class MyUserChangeForm(UserChangeForm):
    def __init__(self, *args, **kwargs):
        super(MyUserChangeForm, self).__init__(*args, **kwargs)
        self.fields['groupsofmetrics'].widget.can_add_related = False
        self.fields['groupsofprobes'].widget.can_add_related = False
        self.fields['groupsofprofiles'].widget.can_add_related = False

    class Meta:
        model = get_user_model()
        fields = '__all__'


class MyFilteredSelectMultiple(FilteredSelectMultiple):
    def __init__(self, verbose_name, is_stacked, attrs=None, choices=()):
        self.verbose_name = verbose_name
        self.name_to_model = {'profiles': Profile,
                              'probes': Probe,
                              'metrics': Metrics}
        self.is_stacked = is_stacked
        super(MyFilteredSelectMultiple, self).__init__(verbose_name, is_stacked, attrs, choices)

    def render(self, name, value, attrs=None, renderer=None):
        html = super(MyFilteredSelectMultiple, self).render(name, value, attrs, renderer)

        if value:
            obj = self.name_to_model[self.verbose_name]
            hs = html.split('\n')
            selected = ['<option value="%s" selected="selected">' % (sel) + \
                        str(obj.objects.get(id=int(sel)).name) + \
                        '</option>' for sel in value]
            hs = hs[:-1] + selected + ['</select>']

            return u'/n'.join(filter(lambda x: 9*'-' not in x, hs))

        else:
            return html

