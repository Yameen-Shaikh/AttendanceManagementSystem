from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django import forms
from .models import CustomUser

class CustomUserAdminForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = '__all__'
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'e.g., John Doe'}),
            'email': forms.EmailInput(attrs={'placeholder': 'e.g., john.doe@example.com'}),
            'roll_no': forms.TextInput(attrs={'placeholder': 'e.g., 12345'}),
        }

class CustomUserAdmin(UserAdmin):
    form = CustomUserAdminForm
    list_display = ('email', 'name', 'role', 'is_active', 'is_staff')
    list_filter = ('role', 'is_active')
    fieldsets = (
        (None, {'fields': ('password',)}),
        ('Personal info', {'fields': ('name', 'email', 'role', 'roll_no')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    ordering = ('email',)
    search_fields = ('email', 'name')

admin.site.register(CustomUser, CustomUserAdmin)
