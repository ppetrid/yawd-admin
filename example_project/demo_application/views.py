import json
from django.views.generic import View
from django.http.response import HttpResponse
from django.core.exceptions import PermissionDenied
from models import WidgetsExample

# Create your views here.
class TypeaheadProfessionsView(View):
    def get(self, request, *args, **kwargs):
        if not request.is_ajax():
            raise PermissionDenied

        query = request.GET.get('query', None)
        results = []

        for el in WidgetsExample.objects.values_list('autocomplete', flat=True).distinct():
            if el and (not query or el.find(query.decode('utf-8')) != -1):
                results.append(el)

        return HttpResponse(json.dumps({'results': results}))
