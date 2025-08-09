from django.http import HttpResponse

from . import sync as syncc


def sync(request):
    return HttpResponse(syncc.fetch_translations())


def pretranslate(request):
    return HttpResponse(syncc.pretranslate())
