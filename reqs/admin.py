from django import forms
from django.contrib import admin
from django.core.exceptions import ValidationError
from reversion.admin import VersionAdmin

from reqs.models import Agency, AgencyGroup, Office, Policy, Requirement, Topic


def is_extension_pdf(uploaded_file):
    if (not uploaded_file.name.endswith('pdf')
            or uploaded_file.content_type != 'application/pdf'):
        raise ValidationError('The file must be a PDF.')


class PolicyForm(forms.ModelForm):
    document_source = forms.FileField(required=False,
                                      validators=[is_extension_pdf])

    class Meta:
        model = Policy
        fields = '__all__'


@admin.register(Policy)
class PolicyAdmin(VersionAdmin):
    form = PolicyForm
    search_fields = ['title', 'omb_policy_id']
    list_filter = ['policy_type', 'policy_status', 'public']
    radio_fields = {'policy_type': admin.VERTICAL}


@admin.register(Topic)
class TopicAdmin(VersionAdmin):
    search_fields = ['name']


@admin.register(Office)
class OfficeAdmin(VersionAdmin):
    search_fields = ['name']


@admin.register(Requirement)
class RequirementAdmin(VersionAdmin):
    search_fields = ['req_id', 'req_text']
    filter_horizontal = ['agencies', 'agency_groups', 'topics']
    fields = [
        'policy',
        'req_id',
        'policy_section',
        'policy_sub_section',
        'req_text',
        'verb',
        'impacted_entity',
        'req_deadline',
        'citation',
        'req_status',
        'precedent',
        'related_reqs',
        'omb_data_collection',
        'topics',
        'agencies',
        'agency_groups',
    ]


@admin.register(Agency)
class AgencyAdmin(VersionAdmin):
    fieldsets = (
        ('Editable fields', {'fields': ['public']}),
        ('Imported fields', {
            'description': ('Data for these fields has been imported from '
                            'itdashboard.gov.'),
            'fields': ['name', 'abbr']
        })
    )
    list_display = ['name', 'abbr', 'public']
    list_filter = ['public']
    readonly_fields = ['name', 'abbr']
    search_fields = ['name']

    def has_add_permission(self, request):
        """Don't allow users to add Agencies."""
        return False


@admin.register(AgencyGroup)
class AgencyGroupAdmin(VersionAdmin):
    fields = ['name', 'agencies']
    filter_horizontal = ['agencies']
    search_fields = ['name']
