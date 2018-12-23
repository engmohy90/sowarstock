from django.contrib import admin
from . import models
# Register your models here.


class ShoppingCartItemInline(admin.TabularInline):
    model = models.ShoppingCartItem


class ShoppingCartAdmin(admin.ModelAdmin):
    inlines = (ShoppingCartItemInline,)


admin.site.register(models.Address)
admin.site.register(models.SowarStockUser)
admin.site.register(models.Contributor)
admin.site.register(models.Category)
admin.site.register(models.SubCategory)
admin.site.register(models.Product)
admin.site.register(models.Collection)
admin.site.register(models.Client)
admin.site.register(models.Review)
admin.site.register(models.Faq)
admin.site.register(models.FaqPersonal)
admin.site.register(models.UserRequest)
admin.site.register(models.ShoppingCart, ShoppingCartAdmin)
admin.site.register(models.ShoppingCartItem)
admin.site.register(models.LegalDocument)
admin.site.register(models.Order)
admin.site.register(models.OrderItem)
admin.site.register(models.Earning)
admin.site.register(models.Payment)
admin.site.register(models.SampleProduct)
admin.site.register(models.SearchKeywordSynonyms)
admin.site.register(models.SearchKeyword)
admin.site.register(models.SiteSettings)
admin.site.register(models.SystemLog)
