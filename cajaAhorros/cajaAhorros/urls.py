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
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)