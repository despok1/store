from django.contrib import admin
from . import models
from django_summernote.admin import SummernoteModelAdmin




@admin.register(models.Category)
class CategoryAdmin(admin.ModelAdmin):
	list_display = ('name', 'slug')
	prepopulated_fields = {'slug': ('name',)}


@admin.register(models.SubCategory)
class SubCategoryAdmin(admin.ModelAdmin):
	list_display = ('name', 'category', 'slug')
	list_filter = ('category',)
	prepopulated_fields = {'slug': ('name',)}


class ProductImageInline(admin.TabularInline):
	model = models.ProductImage
	extra = 1


class VariantInline(admin.TabularInline):
	model = models.Variant
	extra = 1


# class ProductFeatureInline(admin.TabularInline):
# 	model = models.ProductFeature
# 	extra = 1


@admin.register(models.Product)
class ProductAdmin(SummernoteModelAdmin):
	summernote_fields = ('description', 'features',)
	list_display = ('title', 'category', 'subcategory', 'price', 'in_stock', 'date_published')
	list_filter = ('category', 'subcategory', 'in_stock')
	search_fields = ('title', 'description', 'slug')
	inlines = (ProductImageInline, VariantInline)
	prepopulated_fields = {'slug': ('title',)}


@admin.register(models.Variant)
class VariantAdmin(admin.ModelAdmin):
	list_display = ('product', 'name', 'price', 'old_price', 'in_stock', 'stock')
	list_filter = ('product', 'in_stock')
	search_fields = ('name', 'product__title')


@admin.register(models.ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
	list_display = ('product', 'image')


# @admin.register(models.ProductFeature)
# class ProductFeatureAdmin(admin.ModelAdmin):
# 	list_display = ('product', 'name', 'value')
