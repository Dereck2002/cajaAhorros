from django import forms
from .models import Socio

class SocioForm(forms.ModelForm):
    class Meta:
        model = Socio
        fields = '__all__'
        widgets = {
            'fecha_nacimiento': forms.DateInput(attrs={'type': 'date'}),
            'fecha_ingreso': forms.DateInput(attrs={'type': 'date'}),
        }
        labels = {
            'cedula': 'Cédula',
            'nombre': 'Nombre',
            'apellido': 'Apellido',
            'fecha_nacimiento': 'Fecha de nacimiento',
            'foto': 'Foto del socio',
            'fecha_ingreso': 'Fecha de ingreso',
        }
