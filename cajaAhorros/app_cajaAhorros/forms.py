from django import forms
from .models import Socio, Prestamo, Configuracion

class SocioForm(forms.ModelForm):
    class Meta:
        model = Socio
        fields = ('cedula', 'nombre', 'apellido', 'telefono', 'direccion', 'email', 'fecha_nacimiento', 'ocupacion', 'foto', 'fecha_ingreso')
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
            'telefono': forms.TextInput(attrs={'placeholder': 'Teléfono', 'class': 'form-control'}),
            'direccion': forms.TextInput(attrs={'placeholder': 'Dirección', 'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'placeholder': 'Email', 'class': 'form-control'}),
            'ocupacion': forms.TextInput(attrs={'placeholder': 'Ocupación', 'class': 'form-control'}),
            # 'activo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            # 'activo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),

        }

    # Necesario para que las fechas se muestren al editar
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in ['fecha_nacimiento', 'fecha_ingreso']:
            if self.instance and getattr(self.instance, field):
                self.fields[field].initial = getattr(self.instance, field).strftime('%Y-%m-%d')


class PrestamoForm(forms.ModelForm):
    class Meta:
        model = Prestamo
        fields = [
            'socio',
            'garante',
            'fecha_prestamo',
            'cantidad_solicitada',
            'cantidad_aprobada',
            'plazo',          
            'cuota',
            'nota',
            'fecha_aprobacion'
        ]
        widgets = {
            'fecha_prestamo': forms.DateInput(attrs={'type': 'date'}),
            'fecha_aprobacion': forms.DateInput(attrs={'type': 'date'}),
            'nota': forms.Textarea(attrs={'rows': 2}),
            # Aquí puedes dejar el readonly, pero si ocultas el campo, no es necesario
            # 'cuota': forms.NumberInput(attrs={'readonly': 'readonly'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if self.instance.pk:
            self.fields['socio'].disabled = True
            self.fields['garante'].disabled = True
            self.fields['fecha_prestamo'].disabled = True
            self.fields['cantidad_solicitada'].disabled = True
        else:
            self.fields['cantidad_aprobada'].widget = forms.HiddenInput()
            self.fields['nota'].widget = forms.HiddenInput()
            self.fields['fecha_aprobacion'].widget = forms.HiddenInput()
            self.fields['cuota'].widget = forms.HiddenInput()  # <-- Aquí ocultas cuota



#configuracion
class ConfiguracionForm(forms.ModelForm):
    class Meta:
        model = Configuracion
        fields = ['ruc', 'nombre_empresa', 'direccion', 'telefono', 'email', 'logo', 'ciudad', 'tasa_interes', 'plazo_maximo', 'aporte_inicial', 'gastos_adm' ]
        widgets = {
            'ruc': forms.TextInput(attrs={'class': 'form-control'}),
            'nombre_empresa': forms.TextInput(attrs={'class': 'form-control'}),
            'direccion': forms.TextInput(attrs={'class': 'form-control'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'logo': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'ciudad': forms.TextInput(attrs={'class': 'form-control'}),
            'tasa_interes': forms.NumberInput(attrs={'class': 'form-control'}),
            'plazo_maximo': forms.NumberInput(attrs={'class': 'form-control'}),
            'aporte_inicial': forms.NumberInput(attrs={'class': 'form-control'}),
            'gastos_adm': forms.NumberInput(attrs={'class': 'form-control'}),
        }

