from django.contrib import admin
from django.contrib.contenttypes import generic
from yawdadmin import admin_site
from forms import IncomeForm
from models import Transaction, Income, Expense

class TransactionInline(generic.GenericStackedInline):
    model = Transaction
    extra = 1
    #ct_field_name = 'content_type'
    #id_field_name = 'object_id'

class TransactionTabInline(generic.GenericTabularInline):
    model = Transaction
    extra = 1
    #ct_field_name = 'content_type'
    #id_field_name = 'object_id'

class IncomeAdmin(admin.ModelAdmin):
    form = IncomeForm
    inlines = [TransactionInline]
    list_display = ('title', 'repeated', 'when')
    fieldsets = ((None, {
        'fields' : ('title', 'description')
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
    fieldsets = ((None, {
        'fields' : ('title', 'description')
    }),
    ('Repeated expense', {
        'fields' : {'repeated', 'when'},
        'description' : 'Use the following fields for repeated transactions.',
    }))

admin_site.register(Income, IncomeAdmin)
admin_site.register(Expense, ExpenseAdmin)