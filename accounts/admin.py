from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ['username', 'email', 'first_name', 'last_name', 'role', 'is_staff']
    
    # Add custom fields to the admin user edit form
    fieldsets = UserAdmin.fieldsets + (
        ('ALAGA Role Information', {'fields': ('role', 'contact_number')}),
    )
    
    # Add custom fields when creating a user from the admin dashboard
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('ALAGA Role Information', {'fields': ('role', 'contact_number')}),
    )