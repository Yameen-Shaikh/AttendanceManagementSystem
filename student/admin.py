from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django import forms
from .models import CustomUser
from django.contrib.auth.hashers import make_password

class CustomUserCreationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(attrs={'autocomplete': 'new-password'}))
    password2 = forms.CharField(label='Confirm Password', widget=forms.PasswordInput(attrs={'autocomplete': 'new-password'}))
    roll_no = forms.CharField(widget=forms.TextInput(attrs={'autocomplete': 'off'}), required=False)

    class Meta:
        model = CustomUser
        fields = ('email', 'name', 'role', 'roll_no', 'course')

    def clean_password2(self):
        password = self.cleaned_data.get('password')
        password2 = self.cleaned_data.get('password2')
        if password and password2 and password != password2:
            raise forms.ValidationError("Passwords don't match")
        return password2

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
        return user

class CustomUserChangeForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ('email', 'name', 'role', 'roll_no', 'course', 'is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')

class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = CustomUser
    list_display = ('email', 'name', 'role', 'is_active', 'is_staff')
    list_filter = ('role', 'is_active')
    
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('name', 'role', 'roll_no', 'course')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'name', 'role', 'roll_no', 'course', 'password', 'password2'),
        }),
    )
    
    search_fields = ('email', 'name')
    ordering = ('email',)

    def save_model(self, request, obj, form, change):
        if 'password' in form.cleaned_data and form.cleaned_data['password']:
            obj.password = make_password(form.cleaned_data['password'])
        super().save_model(request, obj, form, change)

admin.site.register(CustomUser, CustomUserAdmin)