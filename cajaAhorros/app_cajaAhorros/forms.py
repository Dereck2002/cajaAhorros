from django import forms
from .models import Socio, Prestamo

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


class PrestamoForm(forms.ModelForm):
    fecha_prestamo = forms.DateField(
        widget=forms.DateInput(format='%Y-%m-%d', attrs={'type': 'date'}),
        input_formats=['%Y-%m-%d']
    )
    fecha_aprobacion = forms.DateField(
        required=False,
        widget=forms.DateInput(format='%Y-%m-%d', attrs={'type': 'date'}),
        input_formats=['%Y-%m-%d']
    )

    class Meta:
        model = Prestamo
        fields = [
            'socio',
            'garante',
            'fecha_prestamo',
            'cantidad_solicitada',
            'cantidad_aprobada',
            'plazo',
            'interes',
            'cuota',
            'nota',
            'fecha_aprobacion'
        ]
        widgets = {
            'nota': forms.Textarea(attrs={'rows': 2}),
            'cuota': forms.NumberInput(attrs={'readonly': 'readonly'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if self.instance.pk:
            # Modo edición: deshabilitar campos que no deben cambiarse
            self.fields['socio'].disabled = True
            self.fields['garante'].disabled = True
            self.fields['fecha_prestamo'].disabled = True
            self.fields['cantidad_solicitada'].disabled = True
        else:
            # Modo creación: ocultar campos no necesarios
            self.fields['cantidad_aprobada'].widget = forms.HiddenInput()
            self.fields['nota'].widget = forms.HiddenInput()
            self.fields['fecha_aprobacion'].widget = forms.HiddenInput()

    def clean(self):
        cleaned_data = super().clean()
        cantidad_solicitada = cleaned_data.get('cantidad_solicitada')
        plazo = cleaned_data.get('plazo')
        interes = cleaned_data.get('interes')

        if cantidad_solicitada is not None and interes is not None and plazo:
            cuota = (cantidad_solicitada * interes) / plazo
            cleaned_data['cuota'] = cuota

        if not self.instance.pk:
            # Crear: estado solicitado y cantidad_aprobada igual a solicitada
            cleaned_data['estado'] = 'Solicitado'
            cleaned_data['cantidad_aprobada'] = cantidad_solicitada
        else:
            # Editar: estado pendiente
            cleaned_data['estado'] = 'Pendiente'

        return cleaned_data