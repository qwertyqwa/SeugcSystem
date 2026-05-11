from django.contrib import admin

from .models import User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ("id", "username", "email", "role", "is_staff", "created_at")
    search_fields = ("username", "email")
    list_filter = ("role", "is_staff", "is_active")
