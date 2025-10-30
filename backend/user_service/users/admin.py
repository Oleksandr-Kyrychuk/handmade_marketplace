from django.contrib import admin
from .models import User

# Реєструємо простий адмін для User
@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('email', 'first_name', 'last_name', 'is_verified', 'roles')
    search_fields = ('email', 'first_name', 'last_name')
    # autocomplete_fields = ['some_field_if_needed']

