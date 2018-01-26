from django.contrib import admin
from rango.models import *

# Register your models here.
class CategoryAdmin(admin.ModelAdmin):
    fieldsets = [
         (None, {'fields': ['name']}),
         ('Data', {'fields':['likes','views']}),
    ]
class PageAdmin(admin.ModelAdmin):
    fieldsets = [
         (None, {'fields': ['title', 'url', 'category']}),
      ]

admin.site.register(Category, CategoryAdmin)
admin.site.register(Page, PageAdmin)