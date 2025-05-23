from django.db import models

class Rol(models.Model):
    nombre = models.CharField(max_length=50, unique=True)
    descripcion = models.TextField(blank=True, null=True)
    activo = models.BooleanField(default=True)

    def __str__(self):
        return self.nombre

class Socio(models.Model):
    cedula = models.CharField(max_length=15, unique=True)
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    fecha_nacimiento = models.DateField()
    foto = models.ImageField(upload_to='fotos_socios/', blank=True, null=True)
    fecha_ingreso = models.DateField()

    def __str__(self):
        return f"{self.nombre} {self.apellido} ({self.cedula})"


class Movimiento(models.Model):
    socio = models.ForeignKey(Socio, on_delete=models.CASCADE, related_name='movimientos')
    detalle_movimiento = models.CharField()
    entrada = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    salida = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    saldo = models.DecimalField(max_digits=12, decimal_places=2)
    fecha_movimiento = models.DateField()

    def __str__(self):
        return f"Movimiento {self.pk} - Socio: {self.socio.nombre} - {self.fecha_movimiento}"


class Cargo(models.Model):
    nombre_cargo = models.CharField(max_length=100)
    estado = models.BooleanField(default=True)

    def __str__(self):
        return self.nombre_cargo


class Directiva(models.Model):
    socio = models.ForeignKey(Socio, on_delete=models.CASCADE, related_name='directivas')
    cargo = models.ForeignKey(Cargo, on_delete=models.CASCADE, related_name='directivas')
    estado_directiva = models.BooleanField(default=True)
    fecha_eleccion = models.DateField()
    fecha_salida = models.DateField(blank=True, null=True)

    def __str__(self):
        return f"{self.socio.nombre} - {self.cargo.nombre_cargo}"


class Prestamo(models.Model):
    socio = models.ForeignKey(Socio, on_delete=models.CASCADE, related_name='prestamos')
    garante = models.ForeignKey(Socio, on_delete=models.SET_NULL, null=True, blank=True, related_name='garante_prestamos')
    fecha_prestamo = models.DateField()
    cantidad_solicitada = models.DecimalField(max_digits=12, decimal_places=2)
    cantidad_aprobada = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    plazo = models.PositiveIntegerField(help_text="Plazo en meses")
    interes = models.DecimalField(max_digits=5, decimal_places=2, help_text="Interés porcentual")
    fecha_aprobacion = models.DateField(blank=True, null=True)
    cuota = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    estado_prestamo = models.BooleanField(default=True)
    nota_prestamo = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Préstamo {self.pk} - Socio: {self.socio.nombre}"


class PagoPrestamo(models.Model):
    prestamo = models.ForeignKey(Prestamo, on_delete=models.CASCADE, related_name='pagos')
    cuota_pago = models.PositiveIntegerField()
    saldo_pago = models.DecimalField(max_digits=12, decimal_places=2)
    capital_pago = models.DecimalField(max_digits=12, decimal_places=2)
    interes_pago = models.DecimalField(max_digits=12, decimal_places=2)
    plazo_pago = models.PositiveIntegerField(help_text="Plazo restante en meses")
    valor_cuota_pago = models.DecimalField(max_digits=12, decimal_places=2)
    estado = models.BooleanField(default=True)
    fecha_pago = models.DateField()

    def __str__(self):
        return f"Pago {self.pk} - Préstamo {self.prestamo.pk} - Cuota {self.cuota_pago}"
