from django.contrib import admin

from .models import Rol, Socio, Movimiento, Cargo, Directiva, Prestamo, PagoPrestamo, Configuracion, GastosAdministrativos

admin.site.register(Rol),
admin.site.register(Socio),
admin.site.register(Movimiento),
admin.site.register(Cargo),
admin.site.register(Directiva),
admin.site.register(Prestamo),
admin.site.register(PagoPrestamo),
admin.site.register(Configuracion),
admin.site.register(GastosAdministrativos)