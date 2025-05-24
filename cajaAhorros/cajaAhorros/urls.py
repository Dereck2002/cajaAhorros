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
from django.urls import path
from app_cajaAhorros import views

urlpatterns = [
    path('socios/', views.socio_list, name='socio_list'),
    path('socios/crear/', views.crear_socio, name='crear_socio'),
    path('socio/<int:socio_id>/aportaciones/', views.ver_aportaciones_socio, name='ver_aportaciones_socio'),
    path('admin/', admin.site.urls),
]
