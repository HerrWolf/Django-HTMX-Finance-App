from django.contrib import admin
from import_export.admin import ImportExportModelAdmin

from tracker.models import Category, Transaction, User
from tracker.resources import TransactionResource


class TransactionAdmin(ImportExportModelAdmin):
    resource_classes = [TransactionResource]


admin.site.register(Category)
admin.site.register(Transaction, TransactionAdmin)
admin.site.register(User)
