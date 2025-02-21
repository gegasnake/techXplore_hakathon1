from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser


class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ('ssn', 'phone_number', 'is_staff', 'is_superuser')
    list_filter = ('is_staff', 'is_superuser', 'is_active')
    search_fields = ('ssn', 'phone_number')
    ordering = ('ssn',)

    fieldsets = (
        (None, {'fields': ('ssn', 'phone_number', 'password')}),
        ('Permissions', {'fields': ('is_staff', 'is_superuser', 'is_active')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('ssn', 'phone_number', 'password1', 'password2', 'is_staff', 'is_superuser', 'is_active'),
        }),
    )


admin.site.register(CustomUser, CustomUserAdmin)
