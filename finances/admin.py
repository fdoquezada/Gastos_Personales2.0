from django.contrib import admin

from .models import Category, Transaction, Investment, Budget

admin.site.register(Category)
admin.site.register(Transaction)
admin.site.register(Investment)
admin.site.register(Budget)



# Register your models here.
