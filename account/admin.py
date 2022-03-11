from django.contrib import admin
from account.models import UserAccount, Profile
import csv
import datetime
from django.http import HttpResponse
from django.contrib import admin
from django.utils.translation import gettext_lazy as _



def mark_as_viewed(self, request, queryset):
    queryset.update(viewed=True)

mark_as_viewed.short_description = "Mark as read"

def export_to_csv(modeladmin, request, queryset):
    opts = modeladmin.model._meta
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; \
            filename={}.csv'.format(opts.verbose_name)
    writer = csv.writer(response)

    fields = [field for field in opts.get_fields() if not field.many_to_many and not field.one_to_many]
    writer.writerow([field.verbose_name for field in fields])

    for obj in queryset:
        data_row = []
        for field in fields:
            value = getattr(obj, field.name)
            if isinstance(value, datetime.datetime):
                value = value.strftime('%d/%m/%Y')
            data_row.append(value)
        writer.writerow(data_row)
    return response

export_to_csv.short_description = 'Export to CSV'



@admin.register(UserAccount)
class AccountAdmin(admin.ModelAdmin):
    '''Admin View for Account'''

    list_display = ('username','email','id', 'first_name','last_name','phone','is_subscribed','is_staff','is_admin','is_superuser') 
    readonly_fields=('date_joined', 'last_login',  'is_active')#'password','username','email',
    search_fields = ('username',)
    ordering = ('-pk',)



@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    '''Admin View for Profile'''

    list_display = ('user','image')
    list_filter = ('user',)
    ordering = ('user',)