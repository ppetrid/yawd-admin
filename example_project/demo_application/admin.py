from django.contrib import admin
from django.contrib.contenttypes import generic
from yawdadmin import admin_site
from forms import IncomeForm
from models import Transaction, Income, Expense, Invoice

class TransactionInline(generic.GenericStackedInline):
    model = Transaction
    extra = 1
    #ct_field_name = 'content_type'
    #id_field_name = 'object_id'

class TransactionTabInline(generic.GenericTabularInline):
    model = Transaction
    extra = 1

class IncomeAdmin(admin.ModelAdmin):
    form = IncomeForm
    inlines = [TransactionInline]
    list_display = ('title', 'repeated', 'when')
    search_fields = ['title', 'description']
    fieldsets = ((None, {
        'fields' : ('title', 'description', 'invoice')
    }),
    ('Repeated income', {
        'fields' : {'repeated', 'when'},
        'description' : 'Use the following fields for repeated transactions.',
        'classes' : ['collapse']
    }))
    
    #Custom yawd-admin attributes for the top bar
    order = 1 #put this first in the dropdown list
    
class ExpenseAdmin(admin.ModelAdmin):
    form = IncomeForm
    inlines = [TransactionTabInline]
    list_display = ('title', 'repeated', 'when')
    search_fields = ['title', 'description']
    fieldsets = ((None, {
        'fields' : ('title', 'description')
    }),
    ('Repeated expense', {
        'fields' : {'repeated', 'when'},
        'description' : 'Use the following fields for repeated transactions.',
    }))
    
    #Custom yawd-admin attributes for the top bar
    order = 2 #put this second, after the 'Income' model
    
class InvoiceAdmin(admin.ModelAdmin):
    search_fields = ['title']
    date_hierarchy = 'date'
    list_filter = ['number']
    
    #Custom yawd-admin attributes for the top bar
    order = 3 #put this third, after Income and Expenses
    separator = True #print a separator row BEFORE this element
    
admin_site.register(Income, IncomeAdmin)
admin_site.register(Expense, ExpenseAdmin)
admin_site.register(Invoice, InvoiceAdmin)

#Register this application's items to the top bar navigation!
#Use any of the available bootstrap icon classes for the accompanying icon
#http://twitter.github.com/bootstrap/base-css.html#icons
admin_site.register_top_menu_item('demo_application', icon_class="icon-th")