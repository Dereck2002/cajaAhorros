# app_cajaAhorros/decorators.py

from django.shortcuts import redirect
from django.contrib import messages

def role_required(allowed_roles=[]):
    """
    Decorador que verifica si un usuario pertenece a uno de los roles permitidos.
    Redirige a la página principal si el usuario no tiene permiso.
    """
    def decorator(view_func):
        def wrapper_func(request, *args, **kwargs):
            # El superusuario de Django tiene todos los permisos por defecto.
            if request.user.is_superuser:
                return view_func(request, *args, **kwargs)

            # Obtenemos los grupos (roles) a los que pertenece el usuario.
            user_groups = request.user.groups.values_list('name', flat=True)
            
            # Verificamos si alguno de los grupos del usuario está en la lista de roles permitidos.
            # El rol 'Administrador' siempre tiene acceso a todo lo que no esté explícitamente restringido a otros.
            if 'Administrador' in user_groups or any(group in allowed_roles for group in user_groups):
                return view_func(request, *args, **kwargs)
            else:
                # Si el usuario no tiene permiso, lo redirigimos con un mensaje de error.
                messages.error(request, "No tienes permiso para acceder a esta página.")
                return redirect('dashboard') # 'dashboard' es la vista que redirige a cada uno a su página
        return wrapper_func
    return decorator

