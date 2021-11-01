from django.contrib import admin
from mysite import models

# Register your models here.
'''
class ExrateAdmin(admin.ModelAdmin):
    list_display = ('date','time','currency')
'''
class ExrateQueryAdmin(admin.ModelAdmin):
    list_display = ('date','currency')
class BcoExrateAdmin(admin.ModelAdmin):
    list_display = ('year','month','day_r','currency')
class TiptopUserAdmin(admin.ModelAdmin):
    list_display = ('account','name','c_date')
class HealthAdmin(admin.ModelAdmin):
    list_display = ('h_date','cpf01','name','phone')
'''
admin.site.register(models.Exrate, ExrateAdmin)
'''
admin.site.register(models.ExrateQuery, ExrateQueryAdmin)
admin.site.register(models.BcoExrate, BcoExrateAdmin)
admin.site.register(models.TiptopUser,TiptopUserAdmin)
admin.site.register(models.Health, HealthAdmin)