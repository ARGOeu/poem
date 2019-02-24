from django.contrib import admin
from django.forms import ModelForm, CharField, Textarea, ValidationError, ModelMultipleChoiceField, ModelChoiceField
from django.forms.widgets import TextInput, Select
from django.contrib import admin
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import PermissionDenied

from Poem.poem.models import Aggregation, GroupOfAggregations


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
                                       help_text='Profile is a member of given group')
    groupofaggregations.empty_label = '----------------'
    groupofaggregations.label = 'Group of Aggregations'


class GroupOfAggregationsInlineAddForm(GroupOfAggregationsInlineForms):
    def __init__(self, *args, **kwargs):
        super(GroupOfAggregationsInlineAddForm, self).__init__(*args, **kwargs)
        self.fields['groupofaggregations'].help_text = 'Select one of the groups you are member of'
        self.fields['groupofaggregations'].empty_label = '----------------'
        self.fields['groupofaggregations'].label = 'Group of Aggregations'


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

    def has_change_permission(self, request, obj=None):
        return True

    def has_add_permission(self, request, obj=None):
        return True

    def changelist_view(self, request, extra_context=None):
        return super(AggregationAdmin, self).changelist_view(request, extra_context=extra_context)
