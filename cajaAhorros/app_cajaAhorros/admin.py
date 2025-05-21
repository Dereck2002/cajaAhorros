from django.contrib import admin

from .models import Rol, Socio, Movimiento, Cargo, Directiva, Prestamo, PagoPrestamo

admin.site.register(Rol),
admin.site.register(Socio),
admin.site.register(Movimiento),
admin.site.register(Cargo),
admin.site.register(Directiva),
admin.site.register(Prestamo),
admin.site.register(PagoPrestamo),