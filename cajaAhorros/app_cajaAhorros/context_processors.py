from .models import Configuracion

def configuracion(request):
    return {
        'configuracion': Configuracion.objects.first()
    }
