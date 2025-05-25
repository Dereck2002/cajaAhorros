from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Sum, Q
from .models import Movimiento
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
def ver_aportaciones_socio(request, socio_id):
    socio = get_object_or_404(Socio, pk=socio_id)
    movimientos = Movimiento.objects.filter(socio=socio).order_by('-fecha_movimiento')

    total_aportes = movimientos.filter(salida=0).aggregate(total=Sum('entrada'))['total'] or 0
    total_retiros = movimientos.filter(entrada=0).aggregate(total=Sum('salida'))['total'] or 0
    saldo = total_aportes - total_retiros

    return render(request, 'ver_aportaciones_socio.html', {
        'socio': socio,
        'movimientos': movimientos,
        'total_aportes': total_aportes,
        'total_retiros': total_retiros,
        'saldo': saldo,
    })

# Detalle del socio
def detalle_socio(request, pk):
    socio = get_object_or_404(Socio, pk=pk)
    return render(request, 'detalle.html', {'socio': socio})

# Control de aportaciones por mes