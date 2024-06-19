from django import forms

from core.models import DBConnection


class DBConnectionForm(forms.ModelForm):
    class Meta:
        model = DBConnection
        fields = ['db_type', 'db_host', 'db_port', 'db_name', 'db_user', 'db_password', 'use_ssl']
        widgets = {
            'db_password': forms.PasswordInput(),
        }
