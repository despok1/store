from django.db.models import Q
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.conf import settings
from django.utils import timezone
from threading import Thread
from functools import lru_cache
import logging
import urllib3

from .models import Product, Category
from django.http import JsonResponse
from django.template.loader import render_to_string
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
import json
import os
from collections import defaultdict


logger = logging.getLogger(__name__)

http = urllib3.PoolManager()


def send_resend_email(subject, message, from_email, recipient_list):
    api_key = getattr(settings, 'RESEND_API_KEY', None)
    if not api_key:
        raise ValueError('RESEND_API_KEY is not configured')

    verified_from = getattr(settings, 'RESEND_FROM_EMAIL', None)
    if verified_from:
        from_address = verified_from
    else:
        from_address = from_email

    data = {
        'from': from_address,
        'to': recipient_list,
        'subject': subject,
        'text': message,
    }
    encoded = json.dumps(data).encode('utf-8')
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {api_key}',
    }
    response = http.request(
        'POST',
        'https://api.resend.com/emails',
        body=encoded,
        headers=headers,
        timeout=urllib3.util.Timeout(connect=10.0, read=30.0),
    )

    if response.status >= 400:
        raise RuntimeError(
            f'Resend API error {response.status}: {response.data.decode("utf-8", errors="replace")}'
        )


def send_mail_async(subject, message, from_email, recipient_list):
    def _send():
        try:
            send_resend_email(subject, message, from_email, recipient_list)
        except Exception:
            logger.exception('Failed to send order email via Resend')

    Thread(target=_send, daemon=True).start()

@lru_cache(maxsize=1)
def get_cities_by_region():
    json_path = os.path.join(settings.BASE_DIR, 'static', 'json', 'CitiesAndVillages - 14 March.json')
    with open(json_path, 'r', encoding='utf-8') as f:
        cities_data = json.load(f)

    cities_by_region = defaultdict(list)
    for item in cities_data:
        region = item['region']
        city = item['object_name']
        if city not in cities_by_region[region]:
            cities_by_region[region].append(city)
    return cities_by_region


def index(request):
    categories = Category.objects.all().order_by('order')
    products = Product.objects.all().order_by('-is_featured', '-date_published') #! featured first, then by date

    paginator = Paginator(products, 24)
    page_number = request.GET.get('page', 1)
    if paginator.num_pages == 0:
        page_obj = None
    else:
        try:
            page_obj = paginator.page(page_number)
        except PageNotAnInteger:
            page_obj = paginator.page(1)
        except EmptyPage:
            page_obj = paginator.page(paginator.num_pages)

    query_string = ''
    if request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.GET.get('ajax') == '1':
        html = render_to_string('app/parts/product_grid_items.html', {'products': page_obj.object_list if page_obj else []})
        return JsonResponse({'html': html, 'has_next': page_obj.has_next() if page_obj else False})

    return render(request, 'app/index.html', {
        'products': page_obj.object_list if page_obj else [],
        'page_obj': page_obj,
        'query_string': query_string,
        'categories': categories,
    })


def product_list(request):
    category_slug = request.GET.get('category')
    subcategory_slug = request.GET.get('subcategory')
    search_query = request.GET.get('q', '').strip()
    sort_by = request.GET.get('sort', 'default')
    
    # Price filter
    try:
        min_price = int(request.GET.get('min_price', 0))
    except (ValueError, TypeError):
        min_price = 0
    try:
        max_price = int(request.GET.get('max_price', 999999999))
    except (ValueError, TypeError):
        max_price = 999999999
    
    products = Product.objects.select_related('category', 'subcategory').all()

    selected_category_obj = None
    subcategories = []
    
    if category_slug:
        products = products.filter(category__slug=category_slug)
        try:
            selected_category_obj = Category.objects.get(slug=category_slug)
            subcategories = selected_category_obj.subcategories.all().order_by('order')
        except Category.DoesNotExist:
            pass
    
    if subcategory_slug:
        products = products.filter(subcategory__slug=subcategory_slug)

    if search_query:
        keywords = [word for word in search_query.split() if word]
        for keyword in keywords:
            products = products.filter(
                Q(title__icontains=keyword)
                # | Q(description__icontains=keyword)
                # | Q(features__icontains=keyword)
                | Q(category__name__icontains=keyword)
                | Q(subcategory__name__icontains=keyword)
            )
    
    # Get price range from filtered products (before applying price filter)
    from django.db.models import Min, Max
    price_stats = products.aggregate(price_min=Min('price'), price_max=Max('price'))
    price_min = price_stats['price_min'] or 0
    price_max = price_stats['price_max'] or 999999999
    
    # If no price parameters provided, use the actual range
    if 'min_price' not in request.GET:
        min_price = price_min
    if 'max_price' not in request.GET:
        max_price = price_max
    
    # Apply price filter
    products = products.filter(price__gte=min_price, price__lte=max_price)

    # Apply sorting
    if sort_by == 'newest':
        products = products.order_by('-date_published')
    elif sort_by == 'price_asc':
        products = products.order_by('price')
    elif sort_by == 'price_desc':
        products = products.order_by('-price')
    else:  # default
        products = products.order_by('-is_featured', '-date_published')
    
    products = products.distinct()
    categories = Category.objects.all().order_by('order')

    paginator = Paginator(products, 24)
    page_number = request.GET.get('page', 1)
    if paginator.num_pages == 0:
        page_obj = None
    else:
        try:
            page_obj = paginator.page(page_number)
        except PageNotAnInteger:
            page_obj = paginator.page(1)
        except EmptyPage:
            page_obj = paginator.page(paginator.num_pages)

    query_params = request.GET.copy()
    if 'page' in query_params:
        del query_params['page']
    query_string = query_params.urlencode()

    if request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.GET.get('ajax') == '1':
        html = render_to_string('app/parts/product_grid_items.html', {'products': page_obj.object_list})
        return JsonResponse({'html': html, 'has_next': page_obj.has_next()})

    return render(
        request,
        'app/product.html',
        {
            'products': page_obj.object_list if page_obj else [],
            'page_obj': page_obj,
            'is_paginated': page_obj.has_other_pages() if page_obj else False,
            'query_string': query_string,
            'categories': categories,
            'selected_category': category_slug,
            'selected_category_obj': selected_category_obj,
            'subcategories': subcategories,
            'search_query': search_query,
            'sort_by': sort_by,
            'min_price': min_price,
            'max_price': max_price,
            'price_min': price_min,
            'price_max': price_max,
        },
    )


def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug)
    variants = product.variants.all()
    
    # Get related products from the same category
    related_products = Product.objects.filter(
        category=product.category
    ).exclude(
        id=product.id
    ).order_by(
        '-is_featured',  # Featured products first
        '-date_published'  # Then by newest
    )[:8]  # Limit to 8 products
    
    return render(request, 'app/product-detail.html', {
        'product': product,
        'related_products': related_products,
        'variants': variants
    })

def contact(request):
    return render(request, 'app/contact.html')

def cart(request):
    if request.method == 'POST':
        if 'product_id' in request.POST:
            # Add to cart
            product_id = request.POST.get('product_id')
            variant_id = request.POST.get('variant_id')
            quantity = int(request.POST.get('quantity', 1))
            if product_id:
                cart = request.session.get('cart', {})
                cart_key = f'{product_id}:{variant_id}' if variant_id else str(product_id)
                if cart_key in cart:
                    cart[cart_key] += quantity
                else:
                    cart[cart_key] = quantity
                request.session['cart'] = cart
                messages.success(request, 'Товар додано в кошик!')
        elif 'name' in request.POST:
            # Checkout
            name = request.POST.get('name', '').strip()
            phone = request.POST.get('phone', '').strip()
            region = request.POST.get('time', '').strip()  # Note: 'time' is region
            city = request.POST.get('city', '').strip()
            
            # Validation
            errors = []
            if not name:
                errors.append('Ім\'я обов\'язкове.')
            if not phone:
                errors.append('Телефон обов\'язковий.')
            if not region or region == 'Виберіть Область...':
                errors.append('Область обов\'язкова.')
            if not city or city == 'Виберіть Місто...':
                errors.append('Місто обов\'язкове.')
            
            cart = request.session.get('cart', {})
            if not cart:
                errors.append('Кошик порожній.')
            
            if errors:
                for error in errors:
                    messages.error(request, error)
            else:
                # Get cart items
                cart_items = []
                total = 0
                for cart_key, quantity in cart.items():
                    product_id, variant_id = cart_key.split(':') if ':' in cart_key else (cart_key, None)
                    try:
                        product = Product.objects.get(id=product_id)
                        variant = None
                        price = product.price
                        old_price = product.old_price
                        if variant_id:
                            variant = product.variants.filter(id=variant_id).first()
                            if variant:
                                price = variant.price
                                old_price = variant.old_price
                        subtotal = price * quantity
                        total += subtotal
                        cart_items.append({
                            'product': product,
                            'variant': variant,
                            'price': price,
                            'old_price': old_price,
                            'quantity': quantity,
                            'subtotal': subtotal,
                            'key': cart_key,
                        })
                    except Product.DoesNotExist:
                        pass
                
                # Form email
                subject = f'Нове замовлення від {name}'
                message = f'''
Замовлення від: {name}
Телефон: {phone}
Область: {region}
Місто: {city}

Товари:
'''
                for item in cart_items:
                    title = item['product'].title
                    if item['variant']:
                        title = f"{title} — {item['variant'].name}"
                    message += f'- {title} (кількість: {item["quantity"]}, ціна: {item["price"]}грн, всього: {item["subtotal"]}грн)\n'
                
                message += f'\nЗагальна вартість: {total}грн\n'
                message += f'Дата і час: {timezone.now().strftime("%Y-%m-%d %H:%M:%S")}\n'
                
                send_mail_async(
                    subject,
                    message,
                    settings.DEFAULT_FROM_EMAIL,
                    [settings.STORE_EMAIL],
                )
                messages.success(request, 'Замовлення успішно оформлено')
                request.session['cart'] = {}
                return redirect('cart')
    
    # Rest of the function...
    
    cart_items = []
    total = 0
    cities_by_region = get_cities_by_region()
    cities_json = json.dumps(cities_by_region, ensure_ascii=False)

    cart = request.session.get('cart', {})
    for cart_key, quantity in cart.items():
        product_id, variant_id = cart_key.split(':') if ':' in cart_key else (cart_key, None)
        try:
            product = Product.objects.get(id=product_id)
            variant = None
            price = product.price
            old_price = product.old_price
            if variant_id:
                variant = product.variants.filter(id=variant_id).first()
                if variant:
                    price = variant.price
                    old_price = variant.old_price
            subtotal = price * quantity
            total += subtotal
            cart_items.append({
                'product': product,
                'variant': variant,
                'price': price,
                'old_price': old_price,
                'quantity': quantity,
                'subtotal': subtotal,
                'key': cart_key,
            })
        except Product.DoesNotExist:
            pass  # Игнорировать несуществующие товары
    return render(request, 'app/shoping-cart.html', {
        'cart_items': cart_items,
        'total': total,
        'cities_json': cities_json
    })


@csrf_exempt
@require_POST
def update_cart(request):
    try:
        data = json.loads(request.body)
        cart_key = str(data.get('cart_key') or data.get('product_id'))
        quantity = int(data.get('quantity', 0))
        
        if quantity < 0:
            quantity = 0
        
        cart = request.session.get('cart', {})
        
        if quantity == 0:
            cart.pop(cart_key, None)
        else:
            cart[cart_key] = quantity
        
        request.session['cart'] = cart
        
        # Пересчитать итоги
        total = 0
        subtotal = 0
        if cart_key in cart:
            product_id, variant_id = cart_key.split(':') if ':' in cart_key else (cart_key, None)
            product = Product.objects.get(id=product_id)
            price = product.price
            if variant_id:
                variant = product.variants.filter(id=variant_id).first()
                if variant:
                    price = variant.price
            subtotal = price * cart[cart_key]
        
        for key, qty in cart.items():
            try:
                product_id, variant_id = key.split(':') if ':' in key else (key, None)
                prod = Product.objects.get(id=product_id)
                price = prod.price
                if variant_id:
                    variant = prod.variants.filter(id=variant_id).first()
                    if variant:
                        price = variant.price
                total += price * qty
            except Product.DoesNotExist:
                pass
        
        return JsonResponse({
            'success': True,
            'subtotal': subtotal,
            'total': total,
            'quantity': cart.get(cart_key, 0)
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})