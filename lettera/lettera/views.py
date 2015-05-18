from django.views import generic
from django.contrib.auth import logout

class HomeView(generic.TemplateView):
  template_name = 'home.html'

class AboutView(generic.TemplateView):
  template_name = 'about.html'

class ProfileView(generic.TemplateView):
  template_name = 'registration/profile.html'

class ContactView(generic.TemplateView):
  template_name = 'contact.html'
