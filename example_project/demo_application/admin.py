from django import forms
from django.contrib import admin
from django.contrib.contenttypes import generic
from django.utils.text import mark_safe
from yawdadmin import admin_site
from yawdadmin.admin import SortableModelAdmin, PopupModelAdmin, PopupInline, \
    OneToOneInline
from yawdadmin.sites import YawdAdminDashboard
from forms import SideBarExampleAdminForm, WidgetsExampleAdminForm
from models import SideBarMenuExample, DragNDropChangelistExample, \
    InlineExample, StackedInlineExample, TabularInlineExample, \
    ModalStackedInlineExample, PopupInlineExample, NestedInlineExample, \
    InlineExampleExtension, WidgetsExample


class SideBarMenuExampleAdmin(admin.ModelAdmin):
    #enable the sidebarmenu
    affix=True

    #Custom yawd-admin attributes for the top-bar navigation
    order = 1 #put this first in the dropdown list
    
    #Icon used for this model throughout the yawd-admin pages
    title_icon = 'icon-sort-by-attributes'

    fieldsets = (('', {
        'fields' : ('title', 'field1',)
    }),
                 ('Fieldset', {
        'fields' : ('field2', 'field3'),
        'description': 'Fieldset description example'
    }),
                 ('Collapsed fieldset', {
        'fields' : ('field4', 'field5'),
        'classes': ('collapsed',),
        'description': 'How collapsed fieldsets look in yawd-admin'
    }),
              ('Another fieldset', {
        'fields' : ('field6', 'field7'),
    }),
        ('Last fieldset', {
        'fields' : ('field8', 'field9'),
        'description': 'More fields just to make sure you get the idea of side-bar navigation.'
    }),
    )
    form = SideBarExampleAdminForm
    search_fields = ('title',)


class DragNDropChangelistExampleAdmin(SortableModelAdmin):
    #Uncomment the following line if the field you'd
    #like to sort on is not named 'order'
    #sortable_order_field = 'weird_order_field_name'

    #Custom yawd-admin attributes for the top-bar navigation
    order = 2 #put this second, after the 'SideBarMenuExampleAdmin' model

    #Icon used for this model throughout the yawd-admin pages
    title_icon = 'icon-star'

    list_display = ('title', 'subtitle', 'boolean', 'order')
    list_filter = ('boolean',)
    search_fields = ('title', 'subtitle')


#use OneToOneInline to optimize the form appearance for OneToOne relations
class OneToOneInlineExampleAdmin(OneToOneInline):
    model = InlineExampleExtension


class StackedInlineExampleAdmin(admin.StackedInline):
    extra = 2
    model = StackedInlineExample
    description = 'Inlines in yawd-admin can be collapsible.'
    
    #you can collapse inlines
    collapse = True


class TabularInlineExampleAdmin(admin.TabularInline):

    description = 'Inlines can be have a description'
    
    extra = 3
    model = TabularInlineExample


class ModalStackedInlineExampleAdmin(admin.StackedInline):
    #enable modal functionality
    modal = True
    
    description = 'This inline form opens in a modal window'

    extra = 2
    model = ModalStackedInlineExample


class PopupInlineExampleInline(PopupInline):
    """
    Used as an inline in ``InlineExampleAdmin``.
    This *has* to be linked to a PopupAdmin class 
    """
    model = PopupInlineExample
    #Popup inlines can be sorted using drag n' drop
    sortable = True

    extra = 1
    description = 'Drag n\' drop to order rows.'


class NestedInlineAdmin(admin.StackedInline):
    model = NestedInlineExample
    description = 'Nested inline example'


class PopupInlineExampleAdmin(PopupModelAdmin):
    inlines = (NestedInlineAdmin,)

    #link this model admin with an inline
    linked_inline = PopupInlineExampleInline
    
    #exclude this from the top-menu
    exclude_from_top_menu = True
    #we want PopupInlineExample records to be edited only
    #as an inline to the InlineExample model
    popup_only = True


class InlineExampleAdmin(admin.ModelAdmin):
    #Custom yawd-admin attributes for the top-bar navigation
    order = 3 #put this third, after SideBarMenuExample and DragNDropChangelistExample
    separator = True #print a separator row BEFORE this element

    title_icon = 'icon-rocket'

    #enable the sidebar
    affix = True
    
    inlines = (OneToOneInlineExampleAdmin,
               StackedInlineExampleAdmin, ModalStackedInlineExampleAdmin,
               PopupInlineExampleInline, TabularInlineExampleAdmin)
    
    search_fields = ('title',)


class WidgetsExampleAdmin(admin.ModelAdmin):
    filter_horizontal = ('multiple_select',)
    form = WidgetsExampleAdminForm
    raw_id_fields = ('foreign_key2',)
    fieldsets = (('', {'fields': ('autocomplete', 'datetime', 'text_area',
                                  'radio_select')}),
                 ('Foreign keys', {'fields': ('foreign_key', 'foreign_key2', 'foreign_key3')}),
                 ('Boolean fields', {'fields': ('boolean', 'boolean2', 'boolean3',
                                                'boolean4')}),
                 ('Multiple select', {'fields': ('multiple_select', 'multiple_select2')}))
    search_fields = ('autocomplete',)
    list_display = ('__unicode__', 'boolean', 'get_boolean_display')
    #Custom yawd-admin attributes for the top-bar navigation
    order = 4 #put this last
    title_icon = 'icon-th'


    def get_boolean_display(self, obj):
        if obj.boolean:
            return mark_safe('<span class="label label-success"><i class="icon-thumbs-up"></i> YES</span>')
        return mark_safe('<span class="label label-warning"><i class="icon-thumbs-down"></i> NO</span>')
    get_boolean_display.short_description = 'Boolean again (custom method example)'
    get_boolean_display.admin_order_field = 'boolean'


admin_site.register(SideBarMenuExample, SideBarMenuExampleAdmin)
admin_site.register(DragNDropChangelistExample, DragNDropChangelistExampleAdmin)
admin_site.register(InlineExample, InlineExampleAdmin)
admin_site.register(PopupInlineExample, PopupInlineExampleAdmin)
admin_site.register(WidgetsExample, WidgetsExampleAdmin)

#Register this application's items to the top bar navigation!
#Use any of the available bootstrap icon classes for the accompanying icon
#http://twitter.github.com/bootstrap/base-css.html#icons
admin_site.register_top_menu_item('demo_application', icon_class="icon-gears")

#HOW TO USE THE ADMIN SITE OPTIONS
from yawdadmin.admin_options import OptionSetAdmin, SiteOption

class CustomOptions(OptionSetAdmin):
    optionset_label = 'custom-options'
    verbose_name = 'Custom DB Options'

    option_1 = SiteOption(field=forms.CharField(
            widget=forms.Textarea(
                attrs = {
                    'class' : 'textarea-medium'
                }
            ),
            required=False,
            help_text='A fancy custom text area option.',
        ))

    option_2 = SiteOption(field=forms.CharField(
            help_text='The second awesome option. This one is required!',
    ))

    option_3 = SiteOption(field=forms.BooleanField(
            required=False,
            help_text='Another custom option',
            label='Boolean'
        ))


#register the OptionSetAdmin to the admin site
#almost like we would do for a ModelAdmin
admin_site.register_options(CustomOptions)


#SORRY :( dashboard features are not documented yet, they're not mature enough
#and need improvements
class DemoAppDashboard(YawdAdminDashboard):
    show_app_label_link = False

    @classmethod
    def app_sorter(self, x):
        return x['order'] if 'order' in x else 0

admin_site.dashboard_class = DemoAppDashboard

#register dashboard app_labels - undocumented
#used to set app label icons, perhaps exclude models from the app index pages etc
 

admin_site.register_app_label('demo_application', {'icon': 'icon-gears', 'order': 1,
                                                   'linksets': [(None, ('SideBarMenuExample',
                                                                        'DragNDropChangelistExample',)),
                                                                ('Inlines & widgets',(
                                                                        'InlineExample',
                                                                        'WidgetsExample')),]})
admin_site.register_app_label('auth', {'icon': 'icon-group', 'order': 2})
admin_site.register_app_label('sites', {'icon': 'icon-cloud', 'order': 3})
