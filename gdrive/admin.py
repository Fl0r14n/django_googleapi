from django.contrib import admin
from models import CredentialsModel


class CredentialsAdmin(admin.ModelAdmin):
    list_display = ('id', 'credential')
    search_fields = ('id__username', 'id__email')

    def has_add_permission(self, request):
        return False

admin.site.register(CredentialsModel, CredentialsAdmin)

