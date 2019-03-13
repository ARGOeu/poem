from django.contrib import admin
from django.forms import ModelForm, CharField, Textarea, ValidationError, ModelMultipleChoiceField, ModelChoiceField
from django.forms.widgets import TextInput, Select
from django.contrib import admin
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import PermissionDenied
from django.utils.translation import ugettext as _
from django.urls import reverse

from Poem.poem.models import Aggregation, GroupOfAggregations
from Poem.tenants.models import Tenant
from rest_framework_api_key.models import APIKey
from Poem.settings import WEBAPI_AGGREGATION, WEBAPI_METRIC

import requests

class SharedInfo:
    def __init__(self, requser=None, grname=None):
        if requser:
            self.__class__.user = requser
        if grname:
            self.__class__.group = grname

    def getgroup(self):
        if getattr(self.__class__, 'group', None):
            return self.__class__.group
        else:
            return None

    def delgroup(self):
        self.__class__.group = None

    def getuser(self):
        if getattr(self.__class__, 'user', None):
            return self.__class__.user
        else:
            return None


class GroupOfAggregationsInlineForms(ModelForm):
    def __init__(self, *args, **kwargs):
        sh = SharedInfo()
        self.user = sh.getuser()
        if self.user.is_authenticated:
            self.usergroups = self.user.groupsofaggregations.all()
        super(GroupOfAggregationsInlineForms, self).__init__(*args, **kwargs)
        self.fields['groupofaggregations'].widget.can_add_related = False
        self.fields['groupofaggregations'].widget.can_change_related = False

    def clean_groupofaggregations(self):
        groupsel = self.cleaned_data['groupofaggregations']
        gr = SharedInfo(grname=groupsel)
        ugid = [f.id for f in self.usergroups]
        if groupsel.id not in ugid and not self.user.is_superuser:
            raise ValidationError("You are not member of group %s." % (str(groupsel)))
        return groupsel


class GroupOfAggregationsInlineChangeForm(GroupOfAggregationsInlineForms):
    qs = GroupOfAggregations.objects.all()
    groupofaggregations = ModelChoiceField(queryset=qs, widget=Select(),
                                       help_text='Aggregation profile is a member of given group')
    groupofaggregations.empty_label = '----------------'
    groupofaggregations.label = 'Group'


class GroupOfAggregationsInlineAddForm(GroupOfAggregationsInlineForms):
    def __init__(self, *args, **kwargs):
        super(GroupOfAggregationsInlineAddForm, self).__init__(*args, **kwargs)
        self.fields['groupofaggregations'].help_text = 'Select one of the groups you are member of'
        self.fields['groupofaggregations'].empty_label = '----------------'
        self.fields['groupofaggregations'].label = 'Group'


class GroupOfAggregationsInline(admin.TabularInline):
    model = GroupOfAggregations.aggregations.through
    form = GroupOfAggregationsInlineChangeForm
    verbose_name_plural = 'Group of aggregations'
    verbose_name = 'Group of aggregations'
    max_num = 1
    extra = 1
    template = 'admin/edit_inline/stacked-group.html'


    def has_add_permission(self, request):
        return True

    def has_delete_permission(self, request, obj=None):
        if not obj:
            self.form = GroupOfAggregationsInlineAddForm
        return True

    def has_change_permission(self, request, obj=None):
        if not obj:
            self.form = GroupOfAggregationsInlineAddForm
        return True

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if request.user.is_authenticated and not request.user.is_superuser:
            lgi = request.user.groupsofaggregations.all().values_list('id', flat=True)
            kwargs["queryset"] = GroupOfAggregations.objects.filter(pk__in=lgi)
        return super(GroupOfAggregationsInline,
                     self).formfield_for_foreignkey(db_field, request,
                                                    **kwargs)


class AggregationForm(ModelForm):
    class Meta:
        labels = {
            'name': _('Profile name'),
            'apiid': _('WEB-API ID')
        }
        help_texts = {
            'name': _('WEB-API Aggregation profile name'),
            'apiid': _('WEB-API ID of Aggregation profile'),
        }


class AggregationAdmin(admin.ModelAdmin):
    class Media:
        css = {'all': ('/poem_media/css/siteaggregations.css',)}

    def groupname(obj):
        return obj.groupname
    groupname.short_description = 'Group'

    class GroupAggregationsListFilter(admin.SimpleListFilter):
        title = 'aggregation group'
        parameter_name = 'group'

        def lookups(self, request, model_admin):
            qs = model_admin.get_queryset(request)
            groups = set(qs.values_list('groupname', flat=True))
            return tuple((x,x) for x in filter(lambda x: x != '', groups))

        def queryset(self, request, queryset):
            if self.value():
                return queryset.filter(group=self.value())
            else:
                return queryset

    list_display = ('name', groupname,)
    list_filter= (GroupAggregationsListFilter, )
    inlines = (GroupOfAggregationsInline, )
    actions = None
    list_per_page = 20
    form = AggregationForm
    fields = ('name', 'apiid')

    def _groupown_turn(self, user, flag):
        perm_prdel = Permission.objects.get(codename='delete_aggregation')
        try:
            perm_grpown = Permission.objects.get(codename='groupown_aggregation')
        except Permission.DoesNotExist:
            ct = ContentType.objects.get(app_label='poem', model='aggregation')
            perm_grpown = Permission.objects.create(codename='groupown_aggregation',
                                                   content_type=ct,
                                                   name="Group of aggregation owners")
        if flag == 'add':
            user.user_permissions.add(perm_grpown)
            user.user_permissions.add(perm_prdel)
        elif flag == 'del':
            user.user_permissions.remove(perm_grpown)
            user.user_permissions.remove(perm_prdel)

    def get_form(self, request, obj=None, **kwargs):
        rquser = SharedInfo(requser=request.user)
        if obj:
            if request.user.is_authenticated:
                ug = request.user.groupsofaggregations.all().values_list('name', flat=True)
                if obj.groupname in ug:
                    self._groupown_turn(request.user, 'add')
                else:
                    self._groupown_turn(request.user, 'del')
        elif not request.user.is_superuser:
            self._groupown_turn(request.user, 'add')
        return super(AggregationAdmin, self).get_form(request, obj=None, **kwargs)

    def has_change_permission(self, request, obj=None):
        return True

    def has_add_permission(self, request, obj=None):
        if request.user.is_superuser and GroupOfAggregations.objects.count():
            return True
        if request.user.is_authenticated and request.user.groupsofaggregations.count():
            return True
        else:
            return False

    def changelist_view(self, request, extra_context=None):
        token = APIKey.objects.get(client_id="WEB-API")

        headers, payload = dict(), dict()
        headers = {'Accept': 'application/json', 'x-api-key': token.token}
        response = requests.get(WEBAPI_AGGREGATION,
                                headers=headers,
                                timeout=180)
        response.raise_for_status()
        profiles = response.json()['data']

        profiles_api = set([p['id'] for p in profiles])
        profiles_db = set(Aggregation.objects.all().values_list('apiid', flat=True))
        aggregations_not_indb = profiles_api.difference(profiles_db)

        new_aggregations = []
        for p in profiles:
            if p['id'] in aggregations_not_indb:
                new_aggregations.append(Aggregation(name=p['name'], apiid=p['id'], groupname=''))
        if new_aggregations:
            Aggregation.objects.bulk_create(new_aggregations)

        aggregations_deleted_onapi = profiles_db.difference(profiles_api)
        for p in aggregations_deleted_onapi:
            Aggregation.objects.get(apiid=p).delete()

        return super(AggregationAdmin, self).changelist_view(request, extra_context=extra_context)

    def add_view(self, request, form_url='', extra_context=None):
        extra_context = extra_context or {}
        schema = Tenant.objects.get(domain_url=request.get_host()).schema_name

        props = {
            'tenant_host': request.get_host(),
            'tenant_schema': schema,
            'view': 'add',
            'webapimetric': WEBAPI_METRIC,
            'webapiaggregation': WEBAPI_AGGREGATION,
            'tokenapi': '{0}://{1}{2}WEB-API'.format(request.scheme,
                                                     request.get_host(),
                                                     reverse('poemapi:internal:tokens')),
            'aggregationsapi': '{0}://{1}{2}'.format(request.scheme,
                                                     request.get_host(),
                                                     reverse('poemapi:internal:aggregations')),
            'groupsapi': '{0}://{1}{2}aggregations'.format(request.scheme,
                                                           request.get_host(),
                                                           reverse('poemapi:internal:groups')),
            'aggregationschangelist': '{0}://{1}{2}'.format(request.scheme,
                                                            request.get_host(),
                                                            reverse('admin:poem_aggregation_changelist'))
        }
        extra_context = {
            'props': props
        }

        return super().add_view(
            request, form_url, extra_context=extra_context,
        )

    def change_view(self, request, object_id, form_url='', extra_context=None):
        extra_context = extra_context or {}
        schema = Tenant.objects.get(domain_url=request.get_host()).schema_name

        aggregation = Aggregation.objects.get(id=object_id)
        if aggregation.apiid:
            props = {
                'apiid': aggregation.apiid,
                'tenant_host': request.get_host(),
                'tenant_schema': schema,
                'view': 'change',
                'webapimetric': WEBAPI_METRIC,
                'webapiaggregation': WEBAPI_AGGREGATION,
                'tokenapi': '{0}://{1}{2}WEB-API'.format(request.scheme,
                                                         request.get_host(),
                                                         reverse('poemapi:internal:tokens')),
                'aggregationsapi': '{0}://{1}{2}'.format(request.scheme,
                                                         request.get_host(),
                                                         reverse('poemapi:internal:aggregations')),
                'groupsapi': '{0}://{1}{2}aggregations'.format(request.scheme,
                                                               request.get_host(),
                                                               reverse('poemapi:internal:groups')),
                'aggregationschangelist': '{0}://{1}{2}'.format(request.scheme,
                                                                request.get_host(),
                                                                reverse('admin:poem_aggregation_changelist')),
            }
            extra_context = {
                'props': props
            }

        return super().change_view(
            request, object_id, form_url, extra_context=extra_context,
        )
