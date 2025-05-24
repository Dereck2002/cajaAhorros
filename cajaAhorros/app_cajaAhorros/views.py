from django.shortcuts import render, redirect
from .models import Socio
from .forms import SocioForm

# Listado de Socios
def socio_list(request):
    
    contexto = {
        'socio' : Socio.objects.all()
    }

    return render(request, 'socio_list.html', contexto)
# Crear socio
def crear_socio(request):
    if request.method == 'POST':
        form = SocioForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('socio_list')
    else:
        form = SocioForm()
    
    return render(request, 'crear_socio.html', {'form': form})
# Calcular totales por socio
# Detalle del socio
# Control de aportaciones por mes