from django import forms
from .models import Socio

class SocioForm(forms.ModelForm):
    class Meta:
        model = Socio
        fields = ('cedula', 'nombre', 'apellido', 'fecha_nacimiento', 'foto', 'fecha_ingreso')
        widgets = {
            'fecha_nacimiento': forms.DateInput(
                attrs={'type': 'date', 'class': 'form-control'},
                format='%Y-%m-%d'
            ),
            'fecha_ingreso': forms.DateInput(
                attrs={'type': 'date', 'class': 'form-control'},
                format='%Y-%m-%d'
            ),
            'foto': forms.FileInput(attrs={'accept': 'image/*', 'class': 'form-control'}),
            'cedula': forms.TextInput(attrs={'min': 0, 'class': 'form-control'}),
            'nombre': forms.TextInput(attrs={'placeholder': 'Nombre', 'class': 'form-control'}),
            'apellido': forms.TextInput(attrs={'placeholder': 'Apellido', 'class': 'form-control'}),
        }

    # Necesario para que las fechas se muestren al editar
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in ['fecha_nacimiento', 'fecha_ingreso']:
            if self.instance and getattr(self.instance, field):
                self.fields[field].initial = getattr(self.instance, field).strftime('%Y-%m-%d')
