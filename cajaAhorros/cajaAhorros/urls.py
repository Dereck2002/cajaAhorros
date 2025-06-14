"""
URL configuration for cajaAhorros project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path, include
from app_cajaAhorros import views
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.dashboard, name='dashboard'),
    path('socios/', views.socio_list, name='socio_list'),
    path('socios/crear/', views.crear_socio, name='crear_socio'),
    path('socios/<int:pk>/editar/', views.editar_socio, name='editar_socio'),
    path('socios/eliminar/<int:pk>/', views.eliminar_socio, name='eliminar_socio'),
    path('socio/<int:socio_id>/aportaciones/', views.ver_aportaciones_socio, name='ver_aportaciones_socio'),
    path('socio/<int:socio_id>/agregar-aporte/', views.agregar_aporte, name='agregar_aporte'),
    path('aportes/editar/<int:aporte_id>/', views.editar_aporte, name='editar_aporte'),
    path('aportes/eliminar/<int:aporte_id>/', views.eliminar_aporte, name='eliminar_aporte'),
    path('cargos/agregar/', views.agregar_cargo, name='agregar_cargo'),
    path('cargos/editar/<int:id>/', views.editar_cargo, name='editar_cargo'),
    path('cargos/eliminar/<int:id>/', views.eliminar_cargo, name='eliminar_cargo'),
    path('socios/<int:pk>/', views.detalle_socio, name='detalle_socio'),
    path('accounts/', include('allauth.urls')),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('accounts/profile/', views.dashboard, name='profile'),
    path('prestamos/', views.prestamo_list, name='prestamo_list'),
    path('prestamos/nuevo/', views.crear_o_editar_prestamo, name='prestamo_create'),
    path('prestamos/editar/<int:pk>/', views.crear_o_editar_prestamo, name='prestamo_edit'),
    path('prestamos/aprobar/<int:pk>/', views.aprobar_prestamo, name='aprobar_prestamo'),
    path('prestamos/<int:pk>/rechazar/', views.rechazar_prestamo, name='prestamo_rechazado'),
    path('pagos/prestamo/<int:prestamo_id>/', views.pagos_prestamo, name='pagos_prestamo'),
    path('pagos/registrar/<int:pago_id>/', views.registrar_pago, name='registrar_pago'),
    path('prestamo/<int:pk>/exportar-pdf/', views.exportar_amortizacion_pdf, name='exportar_amortizacion_pdf'),
    path('prestamo/<int:pk>/exportar-pdf/', views.exportar_amortizacion_excel, name='exportar_amortizacion_excel'),
    path('socios/exportar/pdf/', views.exportar_socios_pdf, name='exportar_socios_pdf'),
    path('socios/exportar/excel/', views.exportar_socios_excel, name='exportar_socios_excel'),
    path('socios/imprimir/', views.imprimir_socios, name='imprimir_socios'),
    path('prestamos/exportar/pdf/', views.exportar_prestamos_pdf, name='exportar_prestamos_pdf'),
    path('prestamos/exportar/excel/', views.exportar_prestamos_excel, name='exportar_prestamos_excel'),
    path('gastos/exportar/pdf/', views.exportar_gastosadministrativos_pdf, name='exportar_gastos_pdf'),
    path('gastos/exportar/excel/', views.exportar_gastosadministrativos_excel, name='exportar_gastos_excel'),
    path('configuracion/', views.configuracion, name='configuracion'),
    path('gastos/', views.gastos_administrativos, name='gastos_admin'),
    path('gastos/<str:action>/', views.gastos_administrativos, name='gastos_administrativos_action'),
    path('gastos/editar/<int:pk>/', views.gastos_administrativos, {'action': 'editar'}, name='gasto_editar'),
    path('gastos/<str:action>/<int:pk>/', views.gastos_administrativos, name='gastos_administrativos_action_pk'),
    path('aportaciones/<int:socio_id>/exportar/pdf/', views.exportar_aportaciones_pdf, name='exportar_aportaciones_pdf'),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)