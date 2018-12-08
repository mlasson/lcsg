from django.views.generic import TemplateView
from django.contrib.auth import logout

class HomeView(TemplateView):
  template_name = 'home.html'

class AboutView(TemplateView):
  template_name = 'about.html'

class ProfileView(TemplateView):
  template_name = 'registration/profile.html'

class ContactView(TemplateView):
  template_name = 'contact.html'
