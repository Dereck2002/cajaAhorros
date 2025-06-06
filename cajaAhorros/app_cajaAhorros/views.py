from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.db.models.functions import TruncMonth
from django.db.models import Count, Sum
from .models import Movimiento, Socio, Cargo, Prestamo, PagoPrestamo, Configuracion
from .forms import SocioForm, PrestamoForm, ConfiguracionForm
from datetime import date
from dateutil.relativedelta import relativedelta
from django.core.paginator import Paginator
from decimal import Decimal
from django.utils import timezone
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from django.http import HttpResponse
from openpyxl import Workbook


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

    return render(request, 'socios/socio_list.html', {
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
    
    return render(request, 'socios/crear_socio.html', {'form': form})


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

    return render(request, 'socios/crear_socio.html', {'form': form})

# Eliminar socio
def eliminar_socio(request, pk):
    socio = get_object_or_404(Socio, pk=pk)
    if request.method == 'POST':
        socio.activo = False
        socio.save()
        return redirect('socio_list')
    return render(request, 'socios/eliminar_socio.html', {'socio': socio})


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

    return render(request, 'aportes/ver_aportaciones_socio.html', {
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

    return render(request, 'socios/detalle.html', {'socio': socio, 'edad': edad})


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

def prestamo_list(request):
    prestamos = Prestamo.objects.all()
    return render(request, 'prestamo/prestamo_list.html', {'prestamos': prestamos})

# Crear préstamo
def crear_o_editar_prestamo(request, pk=None):
    prestamo = get_object_or_404(Prestamo, pk=pk) if pk else None
    config = Configuracion.objects.first()  # Obtiene la configuración actual
    
    if request.method == 'POST':
        form = PrestamoForm(request.POST, instance=prestamo)
        if form.is_valid():
            prestamo = form.save(commit=False)

            # Asignar interés desde configuración (ignorar lo que venga en el form)
            prestamo.interes = config.tasa_interes
            
            # Validar plazo máximo
            if prestamo.plazo > config.plazo_maximo:
                form.add_error('plazo', f'El plazo máximo permitido es {config.plazo_maximo} meses.')
                return render(request, 'prestamo/crear_editar_prestamo.html', {'form': form})

            if not pk:
                prestamo.estado = 'Solicitado'
            else:
                prestamo.estado = 'Pendiente'

            prestamo.cuota = None
            prestamo.save()
            return redirect('prestamo_list')
    else:
        form = PrestamoForm(instance=prestamo)

        if prestamo:
            form.initial['cuota'] = ''

    return render(request, 'prestamo/crear_editar_prestamo.html', {'form': form})


#aprovar prestamo
@require_POST
def aprobar_prestamo(request, pk):
    prestamo = get_object_or_404(Prestamo, pk=pk)
    prestamo.estado = 'Aprobado'
    prestamo.fecha_aprobacion = date.today()
    prestamo.save()
    generar_amortizacion(prestamo)
    return redirect('prestamo_list')


#rechazar prestamo
@require_POST
def rechazar_prestamo(request, pk):
    prestamo = get_object_or_404(Prestamo, pk=pk)
    prestamo.estado = 'Rechazado'
    prestamo.save()
    return redirect('prestamo_list')


#pagos prestamos
@login_required
def pagos_prestamo(request, prestamo_id):
    prestamo = get_object_or_404(Prestamo, id=prestamo_id)
    pagos = PagoPrestamo.objects.filter(prestamo=prestamo).order_by('cuota_pago')

    return render(request, 'prestamo/pagos/pagos_prestamo.html', {
        'prestamo': prestamo,
        'pagos': pagos,
    })

#registros de pagos
@require_POST
@login_required
def registrar_pago(request, pago_id):
    pago = get_object_or_404(PagoPrestamo, id=pago_id)
    pago.estado = True
    pago.fecha_pago = timezone.now().date()
    pago.save()
    return redirect('pagos_prestamo', prestamo_id=pago.prestamo.id)

#tabla amortizacion
def generar_amortizacion(prestamo):
    if prestamo.estado == 'Aprobado' and not prestamo.pagos.exists():
        capital_prestado = prestamo.cantidad_aprobada
        plazo = prestamo.plazo
        interes_anual = prestamo.interes
        saldo = capital_prestado

        # Tasa mensual en decimales
        tasa_mensual = (interes_anual / 100) / 12

        # Si la cuota no está calculada, la calculamos (fórmula francesa)
        if not prestamo.cuota:
            if tasa_mensual == 0:
                cuota = capital_prestado / plazo
            else:
                cuota = capital_prestado * (
                    tasa_mensual * (1 + tasa_mensual) ** plazo
                ) / ((1 + tasa_mensual) ** plazo - 1)
            prestamo.cuota = round(cuota, 2)
            prestamo.save()
        else:
            cuota = prestamo.cuota

        fecha = prestamo.fecha_aprobacion or timezone.now().date()

        for i in range(plazo):
            interes = saldo * tasa_mensual
            capital = cuota - interes

            # Redondear para evitar decimales flotantes
            interes = round(interes, 2)
            capital = round(capital, 2)
            cuota_real = round(capital + interes, 2)

            # Ajustar última cuota para cerrar el saldo
            if i == plazo - 1:
                capital = saldo
                interes = max(0, cuota - capital)
                cuota_real = round(capital + interes, 2)
                saldo = 0
            else:
                saldo -= capital
                saldo = round(saldo, 2)

            PagoPrestamo.objects.create(
                prestamo=prestamo,
                cuota_pago=i + 1,
                saldo_pago=saldo if saldo > 0 else 0.00,
                capital_pago=capital,
                interes_pago=interes,
                plazo_pago=plazo - i,
                valor_cuota_pago=cuota_real,
                estado=False,
                fecha_a_pagar=fecha + relativedelta(months=i)
            )

def exportar_amortizacion_pdf(request, pk):
    prestamo = Prestamo.objects.get(pk=pk)
    pagos = prestamo.pagos.all()

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="amortizacion_prestamo_{pk}.pdf"'

    doc = SimpleDocTemplate(response, pagesize=A4)
    elements = []
    styles = getSampleStyleSheet()

    elements.append(Paragraph(f'Tabla de Amortización - Préstamo #{pk}', styles['Title']))
    elements.append(Spacer(1, 12))

    datos = [['#', 'Saldo', 'Capital', 'Interés', 'Cuota', 'Fecha a Pagar', 'Estado']]

    for pago in pagos:
        datos.append([
            pago.cuota_pago,
            f"${pago.saldo_pago}",
            f"${pago.capital_pago}",
            f"${pago.interes_pago}",
            f"${pago.valor_cuota_pago}",
            pago.fecha_a_pagar.strftime('%d/%m/%Y'),
            "Pagado" if pago.estado else "Pendiente"
        ])

    tabla = Table(datos, repeatRows=1)
    tabla.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#d3d3d3')),
        ('TEXTCOLOR',(0,0),(-1,0),colors.black),
        ('ALIGN',(0,0),(-1,-1),'CENTER'),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0,0), (-1,0), 12),
        ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
    ]))

    elements.append(tabla)
    doc.build(elements)
    return response

def exportar_amortizacion_excel(request, pk):
    prestamo = Prestamo.objects.get(pk=pk)
    pagos = prestamo.pagos.all()

    wb = Workbook()
    ws = wb.active
    ws.title = "Amortización"

    headers = ['#', 'Saldo', 'Capital', 'Interés', 'Cuota', 'Fecha a Pagar', 'Estado']
    ws.append(headers)

    for pago in pagos:
        ws.append([
            pago.cuota_pago,
            pago.saldo_pago,
            pago.capital_pago,
            pago.interes_pago,
            pago.valor_cuota_pago,
            pago.fecha_a_pagar.strftime('%d/%m/%Y'),
            'Pagado' if pago.estado else 'Pendiente'
        ])

    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = f'attachment; filename="amortizacion_prestamo_{pk}.xlsx"'
    wb.save(response)
    return response

#dashboard
@login_required
def dashboard(request):
    socios_activos = Socio.objects.filter(activo=True).count()

    total_aportes = Movimiento.objects.filter(entrada__gt=0).aggregate(total=Sum('entrada'))['total'] or 0
    total_retiros = Movimiento.objects.filter(salida__gt=0).aggregate(total=Sum('salida'))['total'] or 0
    saldo_total = total_aportes - total_retiros

    prestamos_estado = Prestamo.objects.values('estado').annotate(cantidad=Count('id'))

    # Gráfico: aportes vs retiros por mes (últimos 6 meses)
    hoy = date.today()
    hace_seis_meses = hoy - relativedelta(months=5)
    movimientos = Movimiento.objects.filter(fecha_movimiento__gte=hace_seis_meses)

    movimientos_por_mes = movimientos.annotate(
        mes=TruncMonth('fecha_movimiento')
    ).values('mes').annotate(
        total_entradas=Sum('entrada'),
        total_salidas=Sum('salida'),
    ).order_by('mes')

    prestamos_recientes = Prestamo.objects.order_by('-id')[:5]

    return render(request, 'dashboard.html', {
        'socios_activos': socios_activos,
        'total_aportes': total_aportes,
        'total_retiros': total_retiros,
        'saldo_total': saldo_total,
        'prestamos_estado': prestamos_estado,
        'movimientos_por_mes': movimientos_por_mes,
        'prestamos_recientes': prestamos_recientes,
    })           


def configuracion(request):
    config = Configuracion.objects.first()
    if request.method == 'POST':
        form = ConfiguracionForm(request.POST, request.FILES, instance=config)
        if form.is_valid():
            form.save()
            return redirect('dashboard')
    else:
        form = ConfiguracionForm(instance=config)
    return render(request, 'configuracion/configuracion.html', {'form': form})