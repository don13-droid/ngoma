import csv
import datetime
from django.http import HttpResponse
from django.contrib import admin
from .models import Sales, News_and_Updates, Song_Payments

def make_cleared(modeladmin, request, queryset):
    queryset.update(cleared=True)
make_cleared.short_description='Mark selected sales as cleared'


def export_to_csv(modeladmin, request, queryset):
    opts = modeladmin.model._meta
    content_disposition = f'attachment; filename={opts.verbose_name}.csv'
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = content_disposition

    writer = csv.writer(response)
    fields = [field for field in opts.get_fields() if not field.many_to_many and not field.one_to_many]
    # Write a first row with header information
    writer.writerow([field.verbose_name for field in fields])
    # Write data rows
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

@admin.register(Sales)
class SalesAdmin(admin.ModelAdmin):
    list_display = ['song','amount','status','created','cleared']
    list_filter = ['song','amount', 'status','created','cleared']
    list_editable=['cleared']
    actions = [make_cleared, export_to_csv]

@admin.register(News_and_Updates)
class UpdatesAdmin(admin.ModelAdmin):
    list_display = ['title', 'status', 'created']
    list_filter = ['status', 'created']

@admin.register(Song_Payments)
class SongPayementsAdmin(admin.ModelAdmin):
    list_display = ['song', 'user', 'payment_status', 'amount', 'created']
    list_filter = ['payment_status', 'song']