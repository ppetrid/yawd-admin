import json
from django.conf.urls import patterns, url
from django.contrib import admin
from django.template.response import TemplateResponse, HttpResponse
from django.utils.translation import ugettext as _


class SortableModelAdmin(admin.ModelAdmin):
    sortable = True
    sortable_order_field = 'order'
    sortable_mptt = False 

    def get_urls(self):
        """
        Override get_urls to include the translation messages view
        for the specified language
        """
        urls = super(SortableModelAdmin, self).get_urls()

        info = self.model._meta.app_label, self.model._meta.module_name
        my_urls = patterns('',
            url(r'^sortables/$',
                self.admin_site.admin_view(self.sortables),
                name="%s_%s_sortables" % info),
            url(r'^sortables/reorder/$',
                self.admin_site.admin_view(self.reorder),
                name="%s_%s_reorder" % info),
            url(r'^ajax/$',
                self.admin_site.admin_view(self.partial_changelist_view),
                name="%s_%s_partial_changelist" % info),
        )
        return my_urls + urls

    def _reorder(self, data, request):
        for obj in data:
            model_obj = self.model.objects.get(pk=int(obj['pk']))
            if self.sortable_mptt:
                setattr(model_obj,
                    model_obj._mptt_meta.parent_attr,
                    self.model.objects.get(pk=int(obj['parent'])) if 'parent' \
                        in obj else None)
            setattr(model_obj, self.sortable_order_field, int(obj['order']))
            model_obj.save()

    def sortables_ordered(self, queryset):
        """
        Should return a queryset that orders the objects properly
        (e.g. for nested categories the queryset should return:
        Parent1, Paren1Child1, Parent1Child2, Parent2, Parent2Child1 etc) 
        """
        return queryset

    def sortables(self, request):
        return TemplateResponse(request, 'admin/sortables/list.html',
                                {'mptt': self.sortable_mptt,
                                 'objects': self.sortables_ordered(self.queryset(request))})
    
    def reorder(self, request):
        if not request.GET.get('data', None):
            return HttpResponse(json.dumps({'message': _('No data sent with the request')}))
        try:
            self._reorder(json.loads(request.GET.get('data', None)), request) 
        except:
            return HttpResponse(json.dumps({'message': _('Unable to reorder objects')}))
        return HttpResponse(json.dumps({'message': _('The order was saved')}))

    def partial_changelist_view(self, request):
        template = self.change_list_template
        self.change_list_template = 'admin/sortables/partial_change_list.html'
        try: #revert state even on exception
            response = super(SortableModelAdmin, self).changelist_view(request)
        finally:
            self.change_list_template = template
            return response


class OneToOneInline(admin.StackedInline):
    template = 'admin/edit_inline/one-to-one-inline.html'
    can_delete = False
