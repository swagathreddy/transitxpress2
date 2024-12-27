from django.contrib import admin
from .models import Feature,Confirmation
# Register your models here.

class ConfirmationAdmin(admin.ModelAdmin):
    list_display = ('user','from_location','to_location','passenger_name', 'email','payment_mode', 'qr_code_image', 'booking_date')
admin.site.register(Feature)
admin.site.register(Confirmation, ConfirmationAdmin)
