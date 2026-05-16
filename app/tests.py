from django.test import TestCase
from django.urls import reverse

from .models import Category, Product


class ProductSearchTests(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name='Освітлення')
        Product.objects.create(
            title='Smart Lamp',
            category=self.category,
            price=1200,
            stock=5,
            features='wireless led wifi',
            description='Modern desk lamp for home office',
        )
        Product.objects.create(
            title='Wooden Table',
            category=self.category,
            price=3500,
            stock=2,
            features='oak handmade',
            description='Dining table made from wood',
        )

    def test_search_by_title(self):
        response = self.client.get(reverse('product'), {'q': 'lamp'})

        self.assertContains(response, 'Smart Lamp')
        self.assertNotContains(response, 'Wooden Table')

    def test_search_by_keywords(self):
        response = self.client.get(reverse('product'), {'q': 'wireless wifi'})

        self.assertContains(response, 'Smart Lamp')
        self.assertNotContains(response, 'Wooden Table')
