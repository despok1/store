from django.db import models
from django.utils.text import slugify


class Cart(models.Model):
	product_id = models.PositiveIntegerField(default=0)
	quantity = models.PositiveIntegerField(default=1)


# Категории и подкатегории
class Category(models.Model):
	name = models.CharField(max_length=150, unique=True)
	slug = models.SlugField(max_length=160, unique=True, blank=True)
	order = models.PositiveIntegerField(default=0)
	image = models.ImageField(upload_to='categories/', blank=True, null=True)
 
	class Meta:
		db_table = 'categories'
		verbose_name = 'Category'
		verbose_name_plural = 'Categories'

	def __str__(self):
		return self.name

	def save(self, *args, **kwargs):
		if not self.slug:
			self.slug = slugify(self.name)
		super().save(*args, **kwargs)


class SubCategory(models.Model):
	category = models.ForeignKey(Category, related_name='subcategories', on_delete=models.CASCADE)
	name = models.CharField(max_length=150)
	slug = models.SlugField(max_length=160, blank=True)
	order = models.PositiveIntegerField(default=0)
 
	class Meta:
		db_table = 'subcategories'
		unique_together = ('category', 'name')
		verbose_name = 'Subcategory'
		verbose_name_plural = 'Subcategories'

	def __str__(self):
		return f"{self.category.name} — {self.name}"

	def save(self, *args, **kwargs):
		if not self.slug:
			self.slug = slugify(self.name)
		super().save(*args, **kwargs)


# Основная модель продукта
class Product(models.Model):
	title = models.CharField(max_length=255)
	main_image = models.ImageField(upload_to='products/main/', blank=True, null=True)
	
	category = models.ForeignKey(Category, related_name='products', on_delete=models.SET_NULL, null=True, blank=True)
	subcategory = models.ForeignKey(SubCategory, related_name='products', on_delete=models.SET_NULL, null=True, blank=True)
 
 
	price = models.PositiveIntegerField(default=0)
	old_price = models.PositiveIntegerField(default=0) 
	in_stock = models.BooleanField(default=True)
	stock = models.PositiveIntegerField(default=0)
	
	is_featured = models.BooleanField(default=False) 
	features = models.TextField(blank=True)
	description = models.TextField(blank=True)
	
	date_published = models.DateTimeField(auto_now_add=True)
	date_updated = models.DateTimeField(auto_now=True)
	slug = models.SlugField(max_length=300, unique=True, blank=True)

	class Meta:
		db_table = 'products'
		ordering = ('-date_published',)

	def __str__(self):
		return self.title

	def save(self, *args, **kwargs):
		if not self.slug:
			base = slugify(self.title)[:240]
			slug = base
			counter = 1
			while Product.objects.filter(slug=slug).exclude(pk=self.pk).exists():
				slug = f"{base}-{counter}"
				counter += 1
			self.slug = slug
		super().save(*args, **kwargs)



# Дополнительные изображения
class ProductImage(models.Model):
	product = models.ForeignKey(Product, related_name='images', on_delete=models.CASCADE)
	image = models.ImageField(upload_to='products/extra/')
	alt = models.CharField(max_length=255, blank=True)

	class Meta:
		db_table = 'product_images'

	def __str__(self):
		return f"Image for {self.product.title}"




# Список характеристик (пара имя: значение)
# class ProductFeature(models.Model):
# 	product = models.ForeignKey(Product, related_name='features', on_delete=models.CASCADE)
# 	name = models.CharField(max_length=150)
# 	value = models.CharField(max_length=255, blank=True)

# 	class Meta:
# 		unique_together = ('product', 'name')

# 	def __str__(self):
# 		return f"{self.name}: {self.value}"

