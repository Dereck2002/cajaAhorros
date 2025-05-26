from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Sum, Q
from .models import Movimiento, Socio
from .forms import SocioForm
from datetime import date, datetime
from dateutil.relativedelta import relativedelta
from django.core.paginator import Paginator


# Listado de Socios
def socio_list(request):
    filtro = request.GET.get('filtro', 'todos')
    socios = Socio.objects.all()
    hoy = date.today().replace(day=1)

    def meses_faltantes(socio):
        movimientos = Movimiento.objects.filter(socio=socio, entrada__gt=0).order_by('fecha_movimiento')
        if not movimientos.exists():
            return True  # Deudor si no tiene aportes

        fechas_aportes = movimientos.dates('fecha_movimiento', 'month')
        meses_aporte_set = set((d.year, d.month) for d in fechas_aportes)

        inicio = movimientos.first().fecha_movimiento.replace(day=1)
        actual = inicio
        while actual <= hoy:
            if (actual.year, actual.month) not in meses_aporte_set:
                return True  # Falta al menos un mes
            actual += relativedelta(months=1)
        return False  # Al día

    socios_filtrados = []
    for socio in socios:
        faltante = meses_faltantes(socio)
        if filtro == 'al_dia' and not faltante:
            socios_filtrados.append(socio)
        elif filtro == 'deudores' and faltante:
            socios_filtrados.append(socio)
        elif filtro == 'todos':
            socios_filtrados.append(socio)

    # Paginación
    paginator = Paginator(socios_filtrados, 10)  # 10 por página
    page = request.GET.get('page')
    socios_paginados = paginator.get_page(page)

    return render(request, 'socio_list.html', {
        'socios': socios_paginados,
        'filtro': filtro
    })

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
    movimientos = Movimiento.objects.filter(socio=socio).order_by('fecha_movimiento')

    total_aportes = movimientos.filter(salida=0).aggregate(total=Sum('entrada'))['total'] or 0
    total_retiros = movimientos.filter(entrada=0).aggregate(total=Sum('salida'))['total'] or 0
    saldo = total_aportes - total_retiros

    # Detectar meses faltantes
    meses_con_aporte = movimientos.filter(entrada__gt=0).dates('fecha_movimiento', 'month')
    meses_con_aporte_set = set((m.year, m.month) for m in meses_con_aporte)

    meses_faltantes = []
    if movimientos.exists():
        inicio = movimientos.first().fecha_movimiento.replace(day=1)
        fin = datetime.today().date().replace(day=1)
        actual = inicio

        while actual <= fin:
            if (actual.year, actual.month) not in meses_con_aporte_set:
                meses_faltantes.append(actual.strftime('%B %Y')) 
            actual += relativedelta(months=1)

    return render(request, 'ver_aportaciones_socio.html', {
        'socio': socio,
        'movimientos': movimientos,
        'total_aportes': total_aportes,
        'total_retiros': total_retiros,
        'saldo': saldo,
        'meses_faltantes': meses_faltantes,
    })

# Detalle del socio
def detalle_socio(request, pk):
    socio = get_object_or_404(Socio, pk=pk)
    # Calcular edad
    hoy = date.today()
    edad = hoy.year - socio.fecha_nacimiento.year - (
        (hoy.month, hoy.day) < (socio.fecha_nacimiento.month, socio.fecha_nacimiento.day)
    )

    return render(request, 'detalle.html', {'socio': socio, 'edad': edad})

# Control de aportaciones por mes