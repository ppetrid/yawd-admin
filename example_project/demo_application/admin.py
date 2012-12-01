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
    #date_hierarchy = 'transaction_set__date'
    fieldsets = ((None, {
        'fields' : ('title', 'description', 'invoice')
    }),
    ('Repeated income', {
        'fields' : {'repeated', 'when'},
        'description' : 'Use the following fields for repeated transactions.',
        'classes' : ['collapse']
    }))
    
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
    
class InvoiceAdmin(admin.ModelAdmin):
    search_fields = ['title']
    date_hierarchy = 'date'
    list_filter = ['number']
    
admin_site.register(Income, IncomeAdmin)
admin_site.register(Expense, ExpenseAdmin)
admin_site.register(Invoice, InvoiceAdmin)