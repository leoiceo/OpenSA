from django.http import HttpResponse, HttpResponseRedirect
from django.conf import settings
from django.views.generic import TemplateView, View
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from django.db.models import Count
from django.shortcuts import redirect,render
from django.contrib.auth.mixins import LoginRequiredMixin
import io
from opensa.utils import create_validate_code
from users.models import Project

class IndexView(LoginRequiredMixin, TemplateView):
    template_name = 'index.html'

def page_not_found(request):
    return render(request, '404.html')

def server_error(request):
    return render(request, '500.html')

def permission_denied(request):
    return render(request, '404.html')

def CheckCode(request):
    mstream = io.BytesIO()
    validate_code = create_validate_code()
    img = validate_code[0]
    img.save(mstream, "GIF")
    request.session["CheckCode"] = validate_code[1]
    return HttpResponse(mstream.getvalue())



