from django.shortcuts import render
from .models import Socio

# Listado de Socios
def socio_list(request):
    
    contexto = {
        'socio' : Socio.objects.all()
    }

    return render(request, 'socio_list.html', contexto)
# Crear socio
# Calcular totales por socio
# Detalle del socio
# Control de aportaciones por mes