from django.urls import path
from .views import HomeView, PricingView, RegisterView, ProfileView

urlpatterns = [
    # PAGINA DE INICIO
    path('', HomeView.as_view(), name='home'),

    # PAGINA DE PRECIOS
    path('pricing/', PricingView.as_view(), name='pricing'),

    # PAGINA DE PREGUNTAS Y RESPUESTAS / PAGINA DE ACERCA DE (A CARGO DE LOS SEGUIDORES DEL CANAL)

    # PAGINAS DE LOGIN Y REGISTRO (VIDEO 5)
    path('register/', RegisterView.as_view(), name='register'),

    # PAGINAS DE PERFIL: VISTA DE PERFIL - EDICION DEL PERFIL (VIDEO 8)
    path('profile/', ProfileView.as_view(), name='profile'),

    # PAGINAS QUE ADMINISTRAN LOS CURSOS: LA LISTA DE CURSOS - (LA CREACION DE CURSOS - LA EDICION DE CURSOS - LA ELIMINACION DE CURSOS) (VIDEO 10)

    # PAGINA DE VISTA DE INSCRIPCION (VIDEO 11)

    # PAGINAS ADMINISTRACION DE NOTAS: (LISTA DE ESTUDIANTES POR CURSO - EDICION DE NOTAS) (VIDEO 12)

    # PAGINAS DE ASISTENCIAS: (LISTA DE ESTUDIANTES POR CURSO - AGREGAR ASISTENCIAS) (VIDEO 13)

]
