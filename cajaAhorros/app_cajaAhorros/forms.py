from django import forms
from .models import Socio

class SocioForm(forms.ModelForm):
    class Meta:
        model = Socio
        fields = ('cedula', 'nombre', 'apellido', 'fecha_nacimiento', 'foto', 'fecha_ingreso')
        widgets = {
            'fecha_nacimiento': forms.DateInput( 
                attrs={'type': 'date', 'class': 'form-control'}
                ),
            'fecha_ingreso': forms.DateInput( 
                attrs={'type': 'date', 'class': 'form-control'}
                ),
            'foto': forms.FileInput(attrs={'accept': 'image/*', 'class': 'form-control'}),
            'cedula': forms.TextInput(attrs={'min': 0, 'class': 'form-control'}),
            'nombre':forms.TextInput(attrs={'placeholder': 'Nombre', 'class': 'form-control'}),
            'apellido': forms.TextInput(attrs={'placeholder': 'Apellido', 'class': 'form-control'}),
        }
        labels = {
            'cedula': 'Cédula',
            'nombre': 'Nombre',
            'apellido': 'Apellido',
            'fecha_nacimiento': 'Fecha de nacimiento',
            'foto': 'Foto del socio',
            'fecha_ingreso': 'Fecha de ingreso',
        }
