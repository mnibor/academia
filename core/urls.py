from django.urls import path
from .views import HomeView, PricingView, RegisterView, ProfileView, CoursesView, CourseCreateView, CourseEditView, CourseDeleteView, CourseEnrollmentView, StudentListMarkView, UpdateMarkView, AttendanceListView, AddAttendanceView, evolution, ErrorView
from django.contrib.auth.decorators import login_required

urlpatterns = [
    # PAGINA DE INICIO
    path('', HomeView.as_view(), name='home'),

    # PAGINA DE PRECIOS
    path('pricing/', PricingView.as_view(), name='pricing'),

    # PAGINA DE PREGUNTAS Y RESPUESTAS / PAGINA DE ACERCA DE (A CARGO DE LOS SEGUIDORES DEL CANAL)

    # PAGINAS DE LOGIN Y REGISTRO (VIDEO 5)
    path('register/', RegisterView.as_view(), name='register'),

    # PAGINAS DE PERFIL: VISTA DE PERFIL - EDICION DEL PERFIL (VIDEO 8)
    path('profile/', login_required(ProfileView.as_view()), name='profile'),

    # PAGINAS QUE ADMINISTRAN LOS CURSOS: LA LISTA DE CURSOS - (LA CREACION DE CURSOS - LA EDICION DE CURSOS - LA ELIMINACION DE CURSOS) (VIDEO 10)
    path('courses/', CoursesView.as_view(), name='courses'),
    path('courses/create/', login_required(CourseCreateView.as_view()), name='course_create'),
    path('courses/<int:pk>/edit/', login_required(CourseEditView.as_view()), name='course_edit'),
    path('courses/<int:pk>/delete/', login_required(CourseDeleteView.as_view()), name='course_delete'),

    # INSCRIPCION DE UN ALUMNO EN UN CURSO
    path('enroll_course/<int:course_id>', login_required(CourseEnrollmentView.as_view()), name='enroll_course'),
    path('error/', login_required(ErrorView.as_view()), name='error'),

    # PAGINA DE VISTA DE INSCRIPCION

    # PAGINAS ADMINISTRACION DE NOTAS: (LISTA DE ESTUDIANTES POR CURSO - EDICION DE NOTAS)
    path('courses/<int:course_id>', login_required(StudentListMarkView.as_view()), name='student_list_mark'),
    path('courses/update_mark/<int:mark_id>', login_required(UpdateMarkView.as_view()), name='update_mark'),

    # PAGINAS DE ASISTENCIAS: (LISTA DE ESTUDIANTES POR CURSO - AGREGAR ASISTENCIAS)
    path('course/<int:course_id>/list_attendance/', login_required(AttendanceListView.as_view()), name='list_attendance'),
    path('course/<int:course_id>/add_attendance/', login_required(AddAttendanceView.as_view()), name='add_attendance'),

    # EVOLUCION DEL ESTUDIANTE
    path('evolution/<int:course_id>/', login_required(evolution), name='evolution'),
]
