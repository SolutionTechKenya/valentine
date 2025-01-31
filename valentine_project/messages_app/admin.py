from django.contrib import admin
from django.http import HttpResponse
import csv
import json
import openpyxl
import io
import datetime
from .models import ValentineMessage, PremiumServiceRequest

@admin.register(ValentineMessage)
class ValentineMessageAdmin(admin.ModelAdmin):
    list_display = ('sender_name', 'recipient_name', 'message_type', 'status', 'scheduled_for', 'created_at')
    list_filter = ('status', 'relationship', 'message_type', 'delivery_method', 'created_at', 'scheduled_for')
    search_fields = ('sender_name', 'recipient_name', 'email', 'phone_number', 'description', 'custom_message')
    readonly_fields = ('created_at',)
    
    fieldsets = (
        ('Sender Information', {
            'fields': ('sender_name', 'email', 'phone_number', 'phone_country')
        }),
        ('Recipient Information', {
            'fields': ('recipient_name', 'relationship')
        }),
        ('Message Details', {
            'fields': ('message_type', 'delivery_method')
        }),
        ('Message Content', {
            'fields': ('description', 'custom_message', 'generated_message')
        }),
        ('Scheduling & Status', {
            'fields': ('scheduled_for', 'status', 'created_at', 'error_details')
        })
    )

    def get_fieldsets(self, request, obj=None):
        """Dynamically adjust fieldsets based on message type"""
        fieldsets = list(super().get_fieldsets(request, obj))
        
        if obj and obj.message_type == 'custom':
            message_content = next(f for f in fieldsets if f[0] == 'Message Content')
            fields = list(message_content[1]['fields'])
            if 'description' in fields:
                fields.remove('description')
            message_content[1]['fields'] = tuple(fields)
        
        return fieldsets

    # Admin Actions for Downloading Data
    actions = ["export_as_csv", "export_as_excel", "export_as_json"]

    def export_as_csv(self, request, queryset):
        """Export selected messages as a CSV file."""
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="valentine_messages.csv"'
        
        writer = csv.writer(response)
        fields = [field.name for field in ValentineMessage._meta.fields]
        writer.writerow(fields)

        for obj in queryset:
            writer.writerow([getattr(obj, field) if getattr(obj, field) is not None else "" for field in fields])

        return response
    export_as_csv.short_description = "Download selected messages as CSV"

    def export_as_excel(self, request, queryset):
        """Export selected messages as an Excel file."""
        workbook = openpyxl.Workbook()
        sheet = workbook.active
        sheet.title = "Valentine Messages"

        fields = [field.name for field in ValentineMessage._meta.fields]
        sheet.append(fields)

        for obj in queryset:
            row = []
            for field in fields:
                value = getattr(obj, field)
                if isinstance(value, (datetime.datetime, datetime.date)):
                    value = value.isoformat()  # Convert datetime to string format
                elif isinstance(value, dict):
                    value = json.dumps(value)  # Convert dictionary to string
                row.append(value)
            sheet.append(row)

        buffer = io.BytesIO()
        workbook.save(buffer)
        buffer.seek(0)

        response = HttpResponse(
            buffer.getvalue(),
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = 'attachment; filename="valentine_messages.xlsx"'
        return response
    export_as_excel.short_description = "Download selected messages as Excel"

    def export_as_json(self, request, queryset):
        """Export selected messages as a JSON file."""
        def custom_serializer(obj):
            """Convert datetime objects to string format."""
            if isinstance(obj, (datetime.datetime, datetime.date)):
                return obj.isoformat()  # Convert datetime to "YYYY-MM-DDTHH:MM:SS" format
            raise TypeError(f"Type {type(obj)} not serializable")

        data = list(queryset.values())
        json_data = json.dumps(data, indent=4, default=custom_serializer)

        response = HttpResponse(
            json_data,
            content_type='application/json'
        )
        response['Content-Disposition'] = 'attachment; filename="valentine_messages.json"'
        return response
    export_as_json.short_description = "Download selected messages as JSON"

@admin.register(PremiumServiceRequest)
class PremiumServiceRequestAdmin(admin.ModelAdmin):
    list_display = ('id', 'contact_number', 'status', 'created_at', 'updated_at')
    list_filter = ('status', 'created_at')
    search_fields = ('contact_number', 'request_description', 'admin_notes')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Request Information', {
            'fields': ('contact_number', 'request_description')
        }),
        ('Status & Notes', {
            'fields': ('status', 'admin_notes')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def get_readonly_fields(self, request, obj=None):
        """Make certain fields readonly once created"""
        if obj:  # editing an existing object
            return self.readonly_fields + ('contact_number',)
        return self.readonly_fields
