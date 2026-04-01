from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('email', 'username', 'phone', 'is_staff', 'created_at')
    search_fields = ('email', 'username', 'phone')
    ordering = ('-created_at',)
    fieldsets = UserAdmin.fieldsets + (
        ('Extra', {'fields': ('phone', 'avatar')}),
    )
