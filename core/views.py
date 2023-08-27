from typing import Any, Dict, Optional
from django.forms.models import BaseModelForm
from django.http import HttpResponse
from django.http.response import HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login
from django.views.generic import TemplateView, CreateView, UpdateView, DeleteView
from django.contrib.auth.models import Group
from .forms import RegisterForm, UserForm, ProfileForm, CourseForm
from django.views import View
from django.utils.decorators import method_decorator
from .models import Course, Registration, Mark
from django.contrib.auth.models import User
from django.urls import reverse_lazy
from django.contrib import messages
from django.contrib.auth.mixins import UserPassesTestMixin
import os
from django.conf import settings


# FUNCION PARA CONVERTIR EL PLURAL DE UN GRUPO A SU SINGULAR
def plural_to_singular(plural):
    # Diccionario de palabras
    plural_singular = {
        "estudiantes": "estudiante",
        "profesores": "profesor",
        "preceptores": "preceptor",
        "administrativos": "administrativo",
    }

    return plural_singular.get(plural, "error")


# DECORADOR PERSONALIZADO
def add_group_name_to_context(view_class):
    original_dispatch = view_class.dispatch

    def dispatch(self, request, *args, **kwargs):
        user = self.request.user
        group = user.groups.first()
        group_name = None
        group_name_singular = None
        color = None
        if group:
            if group.name == 'estudiantes':
                color = 'bg-primary'
            elif group.name == 'profesores':
                color = 'bg-success'
            elif group.name == 'preceptores':
                color = 'bg-secondary'
            elif group.name == 'administrativos':
                color = 'bg-danger'

            group_name = group.name
            group_name_singular = plural_to_singular(group.name)

        context = {
            'group_name': group_name,
            'group_name_singular': group_name_singular,
            'color': color
        }

        self.extra_context = context
        return original_dispatch(self, request, *args, **kwargs)

    view_class.dispatch = dispatch
    return view_class


# PAGINA DE INICIO
@add_group_name_to_context
class HomeView(TemplateView):
    template_name = 'home.html'


# PAGINA DE PRECIOS
@add_group_name_to_context
class PricingView(TemplateView):
    template_name = 'pricing.html'


# PAGINA DE PREGUNTAS Y RESPUESTAS / PAGINA DE ACERCA DE (A CARGO DE LOS SEGUIDORES DEL CANAL)

# REGISTRO DE USUARIOS
class RegisterView(View):
    def get(self, request):
        data = {
            'form': RegisterForm()
        }
        return render(request, 'registration/register.html', data)

    def post(self, request):
        user_creation_form = RegisterForm(data=request.POST)
        if user_creation_form.is_valid():
            user_creation_form.save()
            user = authenticate(username=user_creation_form.cleaned_data['username'],
                                password=user_creation_form.cleaned_data['password1'])
            login(request, user)
            return redirect('home')
        data = {
            'form': user_creation_form
        }
        return render(request, 'registration/register.html', data)


# PAGINA DE PERFIL
@add_group_name_to_context
class ProfileView(TemplateView):
    template_name = 'profile/profile.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        context['user_form'] = UserForm(instance=user)
        context['profile_form'] = ProfileForm(instance=user.profile)

        if user.groups.first().name == 'profesores':
            # Obtener todos los cursos asignados al profesor
            assigned_courses = Course.objects.filter(teacher=user).order_by('-id')
            inscription_courses = assigned_courses.filter(status='I')
            progress_courses = assigned_courses.filter(status='P')
            finalized_courses = assigned_courses.filter(status='F')
            context['assigned_courses'] = assigned_courses
            context['inscription_courses'] = inscription_courses
            context['progress_courses'] = progress_courses
            context['finalized_courses'] = finalized_courses


        elif user.groups.first().name == 'estudiantes':
            # Obtener todos los cursos donde esta inscripto el estudiante
            registrations = Registration.objects.filter(student=user)
            enrolled_courses = [registration.course for registration in registrations]
            context['enrolled_courses'] = enrolled_courses

        elif user.groups.first().name == 'preceptores':
            # Obtener todos los cursos existentes
            all_courses = Course.objects.all()
            inscription_courses = all_courses.filter(status='I')
            progress_courses = all_courses.filter(status='P')
            finalized_courses = all_courses.filter(status='F')
            context['all_courses'] = all_courses
            context['inscription_courses'] = inscription_courses
            context['progress_courses'] = progress_courses
            context['finalized_courses'] = finalized_courses

        return context

    def post(self, request, *args, **kwargs):
        user = self.request.user
        user_form = UserForm(request.POST, instance=user)
        profile_form = ProfileForm(request.POST, request.FILES, instance=user.profile)

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            # Redireccionar a la pagina de perfil (con datos actualizados)
            return redirect('profile')

        # Si alguno de los datos no es valido
        context = self.get_context_data()
        context['user_form'] = user_form
        context['profile_form'] = profile_form
        return render(request, 'profile/profile.html', context)


# MOSTRAR TODOS LOS CURSOS
@add_group_name_to_context
class CoursesView(TemplateView):
    template_name = 'courses.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        courses = Course.objects.all().order_by('-id')
        student = self.request.user if self.request.user.is_authenticated else None

        for item in courses:
            if student:
                registration = Registration.objects.filter(course=item, student=student).first()
                item.is_enrolled = registration is not None
            else:
                item.is_enrolled = False

            enrollment_count = Registration.objects.filter(course=item).count()
            item.enrollment_count = enrollment_count

        context['courses'] = courses
        return context


# PAGINA DE ERROR DE ACCESO A PAGINA NO PERMITIDA
@add_group_name_to_context
class ErrorView(TemplateView):
    template_name = 'error.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        error_image_path = os.path.join(settings.MEDIA_URL, 'error.png')
        context['error_image_path'] = error_image_path
        return context


# CREAR UN NUEVO CURSO
@add_group_name_to_context
class CourseCreateView(UserPassesTestMixin, CreateView):
    model = Course
    form_class = CourseForm
    template_name = 'create_course.html'
    success_url = reverse_lazy('courses')

    def test_func(self):
        return self.request.user.groups.filter(name='administrativos').exists()

    def handle_no_permission(self):
        return redirect('error')

    def form_valid(self, form):
        messages.success(self.request, 'El registro se ha guardado correctamente')
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, 'Ha ocurrido un error al guardar el registro')
        return self.render_to_response(self.get_context_data(form=form))


# EDICION DE UN CURSO
@add_group_name_to_context
class CourseEditView(UserPassesTestMixin, UpdateView):
    model = Course
    form_class = CourseForm
    template_name = 'edit_course.html'
    success_url = reverse_lazy('courses')

    def test_func(self):
        return self.request.user.groups.filter(name='administrativos').exists()

    def handle_no_permission(self):
        return redirect('error')

    def form_valid(self, form):
        form.save()
        messages.success(self.request, 'El registro se ha actualizado satisfactoriamente')
        return redirect(self.success_url)

    def form_invalid(self, form):
        messages.error(self.request, 'Ha ocurrido un error al actualizar el registro')
        return self.render_to_response(self.get_context_data(form=form))


# ELIMINACION DE UN REGISTRO
@add_group_name_to_context
class CourseDeleteView(UserPassesTestMixin, DeleteView):
    model = Course
    template_name = 'delete_course.html'
    success_url = reverse_lazy('courses')

    def test_func(self):
        return self.request.user.groups.filter(name='administrativos').exists()

    def handle_no_permission(self):
        return redirect('error')

    def form_valid(self, form):
        messages.success(self.request, 'El registro se ha eliminado correctamente')
        return super().form_valid(form)


# REGISTRO DE UN USUARIO EN UN CURSO
@add_group_name_to_context
class CourseEnrollmentView(TemplateView):
    def get(self, request, course_id):
        course = get_object_or_404(Course, id=course_id)

        if request.user.is_authenticated and request.user.groups.first().name == 'estudiantes':
            student = request.user

            # Crear un registro de inscripción asociado al estudiante y el curso
            registration = Registration(course=course, student=student)
            registration.save()

            messages.success(request, 'Inscripción exitosa')
        else:
            messages.error(request, 'No se pudo completar la inscripción')

        return redirect('courses')


# MOSTRAR LISTA DE ALUMNOS Y NOTAS A LOS PROFESORES
@add_group_name_to_context
class StudentListMarkView(TemplateView):
    template_name = 'student_list_mark.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        course_id = self.kwargs['course_id']
        course = get_object_or_404(Course, id=course_id)
        marks = Mark.objects.filter(course=course)

        student_data = []
        for mark in marks:
            student = get_object_or_404(User, id=mark.student_id)
            student_data.append({
                'mark_id': mark.id,
                'name': student.get_full_name(),
                'mark_1': mark.mark_1,
                'mark_2': mark.mark_2,
                'mark_3': mark.mark_3,
                'average': mark.average,
            })

        context['course'] = course
        context['student_data'] = student_data
        return context


# ACTUALIZAR NOTAS DE ALUMNOS
@add_group_name_to_context
class UpdateMarkView(UpdateView):
    model = Mark
    fields = ['mark_1', 'mark_2', 'mark_3']
    template_name = 'update_mark.html'

    def get_success_url(self):
        return reverse_lazy('student_list_mark', kwargs={'course_id': self.object.course.id})

    def form_valid(self, form):
        response = super().form_valid(form)
        return redirect(self.get_success_url())

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        mark = self.get_object()
        context['course_name'] = mark.course.name
        return context

    def get_object(self, queryset=None):
        mark_id = self.kwargs['mark_id']
        return get_object_or_404(Mark, id=mark_id)
