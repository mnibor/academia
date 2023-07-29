from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.views.generic import TemplateView
from django.contrib.auth.models import Group
from .forms import RegisterForm, UserForm, ProfileForm
from django.views import View
from django.utils.decorators import method_decorator

def plural_to_singular(plural):
    # Diccionario de palabras
    plural_singular = {
        "estudiantes": "estudiante",
        "profesores": "profesor",
        "preceptores": "preceptor",
        "administrativos": "administrativo",
    }

    return plural_singular.get(plural, "error")


class CustomTemplateView(TemplateView):
    group_name = None
    group_name_singular =None
    color = None

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        if user.is_authenticated:
            group = Group.objects.filter(user=user).first()
            if group:
                if group.name == 'estudiantes':
                    self.color = 'bg-primary'
                elif group.name == 'profesores':
                    self.color = 'bg-success'
                elif group.name == 'preceptores':
                    self.color = 'bg-secondary'
                elif group.name == 'administrativos':
                    self.color = 'bg-danger'

                self.group_name = group.name
                self.group_name_singular = plural_to_singular(group.name)

        context['group_name'] = self.group_name
        context['group_name_singular'] = self.group_name_singular
        context['color'] = self.color
        return context

# PAGINA DE INICIO
class HomeView(CustomTemplateView):
    template_name = 'home.html'

# PAGINA DE PRECIOS
class PricingView(CustomTemplateView):
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
class ProfileView(CustomTemplateView):
    template_name = 'profile/profile.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        context['user_form'] = UserForm(instance=user)
        context['profile_form'] = ProfileForm(instance=user.profile)

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





