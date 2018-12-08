from django import template
import re

register = template.Library()

@register.simple_tag
def active(request, pattern):
  print (pattern)
  # if re.search(pattern, request.resolver_match.url_name):
  #  return 'active'
  #return ''
