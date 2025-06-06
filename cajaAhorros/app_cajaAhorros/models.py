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
    telefono = models.CharField(max_length=15, blank=True, null=True)
    direccion = models.CharField(max_length=200, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    fecha_nacimiento = models.DateField()
    ocupacion = models.CharField(max_length=100, blank=True, null=True)
    foto = models.ImageField(upload_to='fotos_socios/', blank=True, null=True)
    fecha_ingreso = models.DateField()
    activo = models.BooleanField(default=True) 

    def __str__(self):
        return f"{self.nombre} {self.apellido} ({self.cedula})"


class Movimiento(models.Model):
    socio = models.ForeignKey(Socio, on_delete=models.CASCADE, related_name='movimientos')
    detalle_movimiento = models.CharField(max_length=255)
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


class Configuracion(models.Model):
    ruc = models.CharField(max_length=20, unique=True)
    nombre_empresa = models.CharField(max_length=100)
    direccion = models.CharField(max_length=200) 
    telefono = models.CharField(max_length=15)
    email = models.EmailField()
    logo = models.ImageField(upload_to='logos/', blank=True, null=True)
    ciudad = models.CharField(max_length=100)
    tasa_interes = models.DecimalField(max_digits=5, decimal_places=2)   
    plazo_maximo = models.IntegerField()

    def __str__(self):
        return self.nombre_empresa
    

class Prestamo(models.Model):
    ESTADOS = [
        ('Solicitado', 'Solicitado'),
        ('Pendiente', 'Pendiente'),
        ('Aprobado', 'Aprobado'),
        ('Rechazado', 'Rechazado'),
    ]

    socio = models.ForeignKey(Socio, on_delete=models.CASCADE, related_name='prestamos')
    garante = models.ForeignKey(Socio, on_delete=models.SET_NULL, null=True, blank=True, related_name='garante_prestamos')
    fecha_prestamo = models.DateField(null=True, blank=True)
    cantidad_solicitada = models.DecimalField(max_digits=12, decimal_places=2)
    cantidad_aprobada = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    plazo = models.PositiveIntegerField(help_text="Plazo en meses")
    interes = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    cuota = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    estado = models.CharField(max_length=20, choices=ESTADOS, default='Solicitado')
    nota = models.TextField(blank=True, null=True)
    fecha_aprobacion = models.DateField(blank=True, null=True)

    def save(self, *args, **kwargs):
        
        if not self.cantidad_aprobada:
            self.cantidad_aprobada = self.cantidad_solicitada
        super().save(*args, **kwargs)
    

class PagoPrestamo(models.Model):
    prestamo = models.ForeignKey(Prestamo, on_delete=models.CASCADE, related_name='pagos')
    cuota_pago = models.PositiveIntegerField()
    saldo_pago = models.DecimalField(max_digits=12, decimal_places=2)
    capital_pago = models.DecimalField(max_digits=12, decimal_places=2)
    interes_pago = models.DecimalField(max_digits=12, decimal_places=2)
    plazo_pago = models.PositiveIntegerField(help_text="Plazo restante en meses")
    valor_cuota_pago = models.DecimalField(max_digits=12, decimal_places=2)
    estado = models.BooleanField(default=True)
    fecha_pago = models.DateField(null=True, blank=True)
    fecha_a_pagar = models.DateField(blank=True, null=True)

    def __str__(self):
        return f"Pago {self.pk} - Prestamo {self.prestamo.pk} - Cuota {self.cuota_pago}"  
