import json
from django.conf.urls import patterns, url
from django.contrib import admin
from django.contrib.admin.options import InlineModelAdmin 
from django.contrib.admin.util import unquote, get_deleted_objects
from django.core.exceptions import PermissionDenied
from django.db import router
from django.http import Http404
from django.forms.widgets import HiddenInput
from django.template.response import TemplateResponse, HttpResponse
from django.utils.encoding import force_text
from django.utils.html import escape, escapejs
from django.utils.translation import ugettext as _
from templatetags.yawdadmin_tags import inline_items_for_result
from forms import PopupInlineFormSet


try: #django 1.6 and above
    from django.contrib.admin.options import IS_POPUP_VAR #@UnresolvedImport
except:
    IS_POPUP_VAR = '_popup'


class PopupInline(InlineModelAdmin):
    extra = 1
    formset = PopupInlineFormSet
    list_display = []
    sortable = False
    sortable_order_field = 'order'
    template = 'admin/edit_inline/popup.html'


class PopupModelAdmin(admin.ModelAdmin):
    linked_inline = None
    popup_only = False
    
    def add_view(self, request, form_url='', extra_context=None):
        if self.popup_only and not IS_POPUP_VAR in request.REQUEST:
            raise Http404
        
        return super(PopupModelAdmin, self).add_view(request, form_url, extra_context)

    def ajaxdelete_view(self, request, object_id):
        "The 'delete' admin view for this model."
        opts = self.model._meta
        app_label = opts.app_label

        obj = self.get_object(request, unquote(object_id))

        if not self.has_delete_permission(request, obj):
            raise PermissionDenied

        if obj is None:
            raise Http404(
                _('%(name)s object with primary key %(key)r does not exist.') %
                    {'name': force_text(opts.verbose_name), 'key': escape(object_id)}
            )

        using = router.db_for_write(self.model)

        # Populate deleted_objects, a data structure of all related objects that
        # will also be deleted.
        (deleted_objects, perms_needed, protected) = get_deleted_objects(
            [obj], opts, request.user, self.admin_site, using)

        if perms_needed:
            return PermissionDenied

        obj_display = force_text(obj)
        self.log_deletion(request, obj, obj_display)
        self.delete_model(request, obj)

        return HttpResponse('<html><body>OK</body></html>')
    
    def change_view(self, request, object_id, form_url='', extra_context=None):
        if self.popup_only and not IS_POPUP_VAR in request.REQUEST:
            raise Http404
        
        return super(PopupModelAdmin, self).change_view(request, object_id, 
                                                        form_url, extra_context)

    def formfield_for_dbfield(self, db_field, **kwargs):
        """
        Override foreignkey widget if popup and field matches fk_name
        """
        formfield = super(PopupModelAdmin, self).formfield_for_dbfield(db_field,
                                                                       **kwargs)

        request = kwargs.pop("request", None)
        fk_name = request.GET.get('fk_name')
        fk_id = request.GET.get('fk_id')

        if IS_POPUP_VAR in request.REQUEST and db_field.name == fk_name:
            formfield.widget = HiddenInput()
            formfield.popup_fk = True
            if fk_id:
                formfield.initial = fk_id
        return formfield

    def get_urls(self):
        """
        Override get_urls to include the ajax delete url
        """
        urls = super(PopupModelAdmin, self).get_urls()

        info = self.model._meta.app_label, self.model._meta.module_name
        my_urls = patterns('',
            url(r'^(.+)/ajax/delete/$',
                self.admin_site.admin_view(self.ajaxdelete_view),
                name="%s_%s_deleteit" % info),
            url(r'^ajax/reorder/$',
                self.admin_site.admin_view(self.inline_reorder),
                name="%s_%s_inlinereorder" % info),
        )
        return my_urls + urls

    def inline_reorder(self, request):
        if not self.linked_inline or not self.linked_inline.sortable or \
                not self.linked_inline.sortable_order_field:
            raise Http404
        if not request.POST.get('data'):
            raise PermissionDenied
        for obj in json.loads(request.POST['data']):
            model_obj = self.model.objects.get(pk=int(obj['pk']))
            setattr(model_obj, self.linked_inline.sortable_order_field,
                    int(obj['order']))
            model_obj.save()
        return HttpResponse('<html><body>OK</body></html>')

    def response_add(self, request, obj, post_url_continue=None):
        """
        Override add response to handle the PopupInline case 
        """
        if IS_POPUP_VAR in request.POST and request.GET.get('fk_name'):
            return HttpResponse(
                '<!DOCTYPE html><html><head><title></title></head><body>'
                '<script type="text/javascript">parent.dismissAddAnotherPopupInline'
                '(window, "%s", "%s", "%s");</script></body></html>' % \
                    # escape() calls force_text.
                    (escape(obj.pk),
                     escapejs(inline_items_for_result(self.linked_inline, obj) \
                                              if self.linked_inline else obj),
                     'true' if self.linked_inline.can_delete else 'false'))
        return super(PopupModelAdmin, self).response_add(request, obj,
                                                         post_url_continue)

    def response_change(self, request, obj):
        """
        Override change response to handle the PopupInline case 
        """
        if IS_POPUP_VAR in request.POST and request.GET.get('fk_name'):
            return HttpResponse(
                    '<!DOCTYPE html><html><head><title></title></head><body>'
                    '<script type="text/javascript">parent.dismissEditPopupInline'
                    '(window, "%s", "%s");</script></body></html>' % \
                    # escape() calls force_text.
                    (escape(obj.pk),
                     escapejs(inline_items_for_result(self.linked_inline, obj) \
                                              if self.linked_inline else obj)))
        return super(PopupModelAdmin, self).response_change(request, obj)


class SortableModelAdmin(admin.ModelAdmin):
    sortable = True
    sortable_order_field = 'order'
    sortable_mptt = False 

    def get_urls(self):
        """
        Override get_urls to include the sortable views
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
        data = dict([(str(d['pk']), d) for d in data])
        
        data_objects = self.model.objects.filter(pk__in=data.keys())
        for item in data_objects:
            data[str(item.pk)]['object'] = item

        for d in data.itervalues():
            if self.sortable_mptt:
                parent = data[str(d['parent'])]['object'] if 'parent' in d else None
                setattr(d['object'],
                        d['object']._mptt_meta.parent_attr,
                        parent)
            setattr(d['object'], self.sortable_order_field, int(d['order']))
            d['object'].save()

        if self.sortable_mptt:
            self.model.objects.rebuild()

    def sortables_ordered(self, queryset):
        """
        Should return a queryset that orders the objects properly
        (e.g. for nested categories the queryset should return:
        Parent1, Paren1Child1, Parent1Child2, Parent2, Parent2Child1 etc) 
        """
        return queryset

    def sortables(self, request):
        return TemplateResponse(request, 'admin/sortables/mptt_list.html' if self.sortable_mptt \
                                    else 'admin/sortables/list.html',
                                {'mptt': self.sortable_mptt,
                                 'objects': self.sortables_ordered(self.queryset(request))})
    
    def reorder(self, request):
        if not request.POST.get('data', None):
            return HttpResponse(json.dumps({'message': _('No data sent with the request')}))
        try:
            self._reorder(json.loads(request.POST.get('data', None)), request) 
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
    one_to_one = True
    show_title = True
