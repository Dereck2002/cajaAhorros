from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Sum, Q
from .models import Movimiento, Socio, Cargo
from .forms import SocioForm
from datetime import date, datetime
from dateutil.relativedelta import relativedelta
from django.core.paginator import Paginator
from decimal import Decimal
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required


@login_required
def socio_list(request):
    filtro = request.GET.get('filtro', 'todos')
    socios = Socio.objects.filter(activo=True)  # 👈 Solo activos
    cargos = Cargo.objects.all()
    hoy = date.today().replace(day=1)

    def meses_faltantes(socio):
        movimientos = Movimiento.objects.filter(socio=socio, entrada__gt=0).order_by('fecha_movimiento')
        if not movimientos.exists():
            return True
        fechas_aportes = movimientos.dates('fecha_movimiento', 'month')
        meses_aporte_set = set((d.year, d.month) for d in fechas_aportes)
        inicio = movimientos.first().fecha_movimiento.replace(day=1)
        actual = inicio
        while actual <= hoy:
            if (actual.year, actual.month) not in meses_aporte_set:
                return True
            actual += relativedelta(months=1)
        return False

    socios_filtrados = []
    for socio in socios:
        faltante = meses_faltantes(socio)
        if filtro == 'al_dia' and not faltante:
            socios_filtrados.append(socio)
        elif filtro == 'deudores' and faltante:
            socios_filtrados.append(socio)
        elif filtro == 'todos':
            socios_filtrados.append(socio)
#paginacion
    paginator = Paginator(socios_filtrados, 10)
    page = request.GET.get('page')
    socios_paginados = paginator.get_page(page)

    return render(request, 'socio_list.html', {
        'socios': socios_paginados,
        'filtro': filtro,
        'cargos': cargos,
    })

# Crear socio
@login_required
def crear_socio(request):
    if request.method == 'POST':
        form = SocioForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('socio_list')
    else:
        form = SocioForm()
    
    return render(request, 'crear_socio.html', {'form': form})


# Editar socio
def editar_socio(request, pk):
    socio = get_object_or_404(Socio, pk=pk)
    if request.method == 'POST':
        form = SocioForm(request.POST, request.FILES, instance=socio)
        if form.is_valid():
            form.save()
            return redirect('socio_list')
    else:
        form = SocioForm(instance=socio)

    return render(request, 'crear_socio.html', {'form': form})

# Eliminar socio
def eliminar_socio(request, pk):
    socio = get_object_or_404(Socio, pk=pk)
    if request.method == 'POST':
        socio.activo = False
        socio.save()
        return redirect('socio_list')
    return render(request, 'eliminar_socio.html', {'socio': socio})


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
        fin = date.today().replace(day=1)
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


# Agregar Nuevo Aportes
def agregar_aporte(request, socio_id):
    socio = get_object_or_404(Socio, pk=socio_id)

    if request.method == 'POST':
        detalle = request.POST.get('detalle_movimiento')
        entrada = request.POST.get('entrada')
        fecha = request.POST.get('fecha_movimiento')

        entrada_decimal = Decimal(entrada)

        ultimo_movimiento = Movimiento.objects.filter(socio=socio).order_by('-fecha_movimiento').first()
        saldo_anterior = ultimo_movimiento.saldo if ultimo_movimiento else Decimal('0.00')

        nuevo_saldo = saldo_anterior + entrada_decimal

        Movimiento.objects.create(
            socio=socio,
            detalle_movimiento=detalle,
            entrada=entrada_decimal,
            salida=Decimal('0.00'),
            saldo=nuevo_saldo,
            fecha_movimiento=fecha
        )

        return redirect('ver_aportaciones_socio', socio_id=socio_id)        

# Detalle del socio
def detalle_socio(request, pk):
    socio = get_object_or_404(Socio, pk=pk)
    # Calcular edad
    hoy = date.today()
    edad = hoy.year - socio.fecha_nacimiento.year - (
        (hoy.month, hoy.day) < (socio.fecha_nacimiento.month, socio.fecha_nacimiento.day)
    )

    return render(request, 'detalle.html', {'socio': socio, 'edad': edad})


# Editar aporte
def editar_aporte(request, aporte_id):
    aporte = get_object_or_404(Movimiento, pk=aporte_id)

    if request.method == 'POST':
        detalle = request.POST.get('detalle_movimiento')
        entrada = request.POST.get('entrada')
        fecha = request.POST.get('fecha_movimiento')

        entrada_decimal = Decimal(entrada)

        # Actualizar campos
        aporte.detalle_movimiento = detalle
        aporte.entrada = entrada_decimal
        aporte.fecha_movimiento = fecha
        # Saldo puede ser recalculado según lógica de negocio; aquí simplificamos y dejamos igual.
        aporte.save()
        return redirect('ver_aportaciones_socio', socio_id=aporte.socio.id)

    # Si por alguna razón GET: redirigimos al detalle
    return redirect('ver_aportaciones_socio', socio_id=aporte.socio.id)


# Eliminar aporte
def eliminar_aporte(request, aporte_id):
    aporte = get_object_or_404(Movimiento, pk=aporte_id)
    socio_id = aporte.socio.id

    if request.method == 'POST':
        aporte.delete()
        return redirect('ver_aportaciones_socio', socio_id=socio_id)

    return render(request, 'eliminar_aporte_confirm.html', {'aporte': aporte})


@require_POST
def agregar_cargo(request):
    nombre = request.POST.get('nombre_cargo')
    estado = request.POST.get('estado') == 'true'
    Cargo.objects.create(nombre_cargo=nombre, estado=estado)
    return redirect('socio_list')

@require_POST
def editar_cargo(request, id):
    cargo = get_object_or_404(Cargo, id=id)
    cargo.nombre_cargo = request.POST.get('nombre_cargo')
    cargo.estado = request.POST.get('estado') == 'true'
    cargo.save()
    return redirect('socio_list')

@require_POST
def eliminar_cargo(request, id):
    cargo = get_object_or_404(Cargo, id=id)
    cargo.delete()
    return redirect('socio_list')
