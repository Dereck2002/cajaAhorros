# app_cajaAhorros/signals.py

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User, Group
from .models import Socio

@receiver(post_save, sender=Socio)
def crear_usuario_para_socio(sender, instance, created, **kwargs):
    """
    Esta señal se dispara automáticamente después de que un Socio es guardado.
    Ahora también asigna el nuevo usuario al grupo 'Socio'.
    """
    if created and not instance.user:
        
        # --- DEBUGGING: Imprimir los datos recibidos en la consola del servidor ---
        print(f"--- Señal 'crear_usuario_para_socio' disparada para el socio: {instance.nombre} {instance.apellido} ---")
        print(f"Cédula recibida en la señal: '{instance.cedula}'")
        print(f"Email recibido en la señal: '{instance.email}'")

        # --- VALIDACIÓN: Asegurarse de que la cédula no esté vacía ---
        if not instance.cedula:
            print(f"ERROR: No se puede crear usuario para Socio ID {instance.pk} porque la cédula está vacía.")
            return # Detiene la ejecución si no hay cédula
            
        # Limpiamos el nombre de usuario por si tiene espacios extra
        username_a_crear = instance.cedula.strip()

        if not User.objects.filter(username=username_a_crear).exists():
            print(f"Intentando crear nuevo usuario con username: '{username_a_crear}'")
            
            # Usamos getattr para más seguridad, aunque los nombres de campo ya deberían ser correctos.
            nuevo_usuario = User.objects.create_user(
                username=username_a_crear,
                email=instance.email,
                password=username_a_crear, # Usar la cédula como contraseña temporal
                first_name=getattr(instance, 'nombre', ''),
                last_name=getattr(instance, 'apellido', '')
            )
            
            # --- LÓGICA PARA AÑADIR AL GRUPO 'Socio' ---
            try:
                grupo_socio = Group.objects.get(name='Socio')
                nuevo_usuario.groups.add(grupo_socio)
                print(f"Usuario '{username_a_crear}' añadido al grupo 'Socio'.")
            except Group.DoesNotExist:
                print("ADVERTENCIA: El grupo 'Socio' no existe. El nuevo usuario no fue asignado a ningún grupo.")
            
            # Asignamos el nuevo usuario al socio que se acaba de crear.
            instance.user = nuevo_usuario
            instance.save(update_fields=['user']) # Usamos update_fields para evitar que la señal se dispare de nuevo.
            print(f"Socio ID {instance.pk} actualizado con el nuevo usuario ID {nuevo_usuario.pk}.")
        else:
            print(f"ADVERTENCIA: No se creó un nuevo usuario porque el username '{username_a_crear}' ya existe en la base de datos.")

