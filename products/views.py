import json
from statistics import mean

from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db.models import Max, Q
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect, HttpResponseRedirect
from django.contrib.auth.decorators import login_required

from .forms import ReviewBox
from .models import *
from users.models import *
from django.contrib import messages
# Create your views here.


def total_cart_items(request):
    check_out_list = Checkout.objects.filter(user=request.user, complete=False)
    get_cart_items = sum([item.quantity for item in check_out_list])
    return get_cart_items


def home(request):
    categories = Category.getAllCategory()
    products = Product.objects.all().order_by("-id")

    if request.user.is_authenticated:
        notification = Notification.objects.filter(user=request.user, is_seen=False).order_by("-id")[:10]
        notification_count = Notification.objects.filter(user=request.user, is_seen=False).count()
        get_cart_items = total_cart_items(request)
    else:
        notification = 0
        notification_count = 0
        get_cart_items = 0

    context = {
        "notification": notification,
        "notification_count": notification_count,
        "categories": categories,
        "products": products,
        "get_cart_items": get_cart_items,
    }
    return render(request, "products/home.html", context)


@login_required
def products_view(request):
    categories = Category.getAllCategory()
    products = Product.objects.all().order_by("-id")
    maximum_price = Product.objects.all().aggregate(Max("price"))
    half_max_price = maximum_price["price__max"] / 2

    # price_filter = ProductPriceFilter(request.GET, queryset=products)
    # product_list = price_filter.qs

    paginator = Paginator(products, 5)
    page = request.GET.get('page', 1)

    try:
        product_list = paginator.page(page)
    except PageNotAnInteger:
        product_list = paginator.page(1)
    except EmptyPage:
        product_list = paginator.page(paginator.num_pages)

    page_list = product_list.paginator.page_range

    if request.GET.get('category_id'):
        filterProduct = Product.getProductByFilter(request.GET['category_id']).order_by('-id')
        filter_category_product = filterProduct.all().order_by('-product_purchase')
        # price_filter = ProductPriceFilter(request.GET, queryset=filter_category_product)
        # result = price_filter.qs
        maximum_price = Product.objects.all().aggregate(Max("price"))
        half_max_price = maximum_price["price__max"] / 2

        return render(request, 'products/market.html', {
                                                      # "products": result,
                                                      # "page_list": page_list,
                                                      # "price_filter": price_filter,
                                                      "categories": categories,
                                                      "products": filter_category_product,
                                                      "maximum_price": maximum_price,
                                                      "half_max_price": half_max_price,
                                                      # "notification_count": notification_count,
                                                      # "notification": notification,
                                                      "get_cart_items": total_cart_items(request)
                                                      })
    notification = Notification.objects.filter(user=request.user, is_seen=False).order_by("-id")[:10]
    notification_count = Notification.objects.filter(user=request.user, is_seen=False).count()

    context = {
        "notification": notification,
        "notification_count": notification_count,
        "categories": categories,
        "products": products,
        "get_cart_items": total_cart_items(request),

        # "price_filter": price_filter,
        "maximum_price": maximum_price,
        "half_max_price": half_max_price,

        # "notification_count": notification_count,
        # "notification": notification,
        "page_list": page_list,

    }
    return render(request, "products/market.html", context)


@login_required
def products_details(request, pk):
    product = get_object_or_404(Product, pk=pk)
    notification = Notification.objects.filter(user=request.user, is_seen=False).order_by("-id")[:10]
    notification_count = Notification.objects.filter(user=request.user, is_seen=False).count()
    recently_viewed_products = []
    if 'recently_viewed_products' in request.session:
        recently_viewed_ids = request.session['recently_viewed_products']
        recently_viewed_products = Product.objects.filter(pk__in=recently_viewed_ids).exclude(pk=pk)

    ratings = [i.rating for i in product.productreview_set.all()]
    if len(ratings) < 1:
        overall_rating = 0
        one_star = 0
        two_star = 0
        three_star = 0
        four_star = 0
        five_star = 0
    else:
        overall_rating = mean(ratings)
        one_star = float(ratings.count(1) * 100) / len(ratings)
        two_star = float(ratings.count(2) * 100) / len(ratings)
        three_star = float(ratings.count(3) * 100) / len(ratings)
        four_star = float(ratings.count(4) * 100) / len(ratings)
        five_star = float(ratings.count(5) * 100) / len(ratings)
    context = {
        "notification": notification,
        "notification_count": notification_count,
        "product": product,
        "recently_viewed_products": recently_viewed_products,
        "form": ReviewBox(),
        "get_cart_items": total_cart_items(request),

        "one_star": str(one_star)[:5],
        "two_star": str(two_star)[:5],
        "three_star": str(three_star)[:5],
        "four_star": str(four_star)[:5],
        "five_star": str(five_star)[:5],
        "overall_rating": str(overall_rating)[:3],
    }
    return render(request, "products/product_detail.html", context)

@login_required
def search_view(request):
    notification = Notification.objects.filter(user=request.user, is_seen=False).order_by("-id")[:10]
    notification_count = Notification.objects.filter(user=request.user, is_seen=False).count()
    if request.method == "GET":
        query = request.GET.get('q')
        submitbutton = request.GET.get('submit')
        if query is not None:
            lookups_product = Q(name__icontains=query)
            # result_user = User.objects.filter(lookups_user).distinct()
            result_product = Product.objects.filter(lookups_product).distinct()
            context = {
                'submitbutton': submitbutton,

                "result_product": result_product,
                "notification_count": notification_count,
                "notification": notification,
                "get_cart_items": total_cart_items(request)
            }
            return render(request, "products/search.html", context)
        else:
            context = {
                'submitbutton': submitbutton,
                "notification_count": notification_count,
                "notification": notification,
                "get_cart_items": total_cart_items(request)
            }
            return render(request, 'products/search.html', context)
    return render(request, "products/search.html", {})



@login_required
def add_to_checkout(request, pk):
    user = request.user
    product = get_object_or_404(Product, pk=pk)
    # checkout_list = Checkout.objects.filter(user=user, complete=False)

    create_object, created = Checkout.objects.get_or_create(
        user=user,
        product=product,
        complete=False,
    )
    create_object.quantity = (create_object.quantity + 1)
    create_object.price = (create_object.quantity * create_object.product.price)
    create_object.save()
    if create_object.quantity > 1:
        messages.success(request, f'"{product}" quantity has been updated!')
    else:
        messages.success(request, f'"{product}" has been added to your cart!')
    return redirect("checkout")


@login_required
def remove_from_checkout(request, pk):
    customer = request.user
    product = get_object_or_404(Product, pk=pk)
    orderItem, created = Checkout.objects.get_or_create(user=customer, product=product, complete=False)
    if Checkout.objects.filter(user=customer, product=product).exists():
        if orderItem.quantity <= 0:
            orderItem.delete()
            messages.success(request, f"'{product.name}' has been removed from your cart/checkout")
            return redirect("checkout")
        if orderItem.quantity >= 1:
            orderItem.quantity = (orderItem.quantity - 1)
            orderItem.price = (orderItem.quantity * orderItem.product.price)
            orderItem.save()
            messages.success(request, f"'{product.name}' quantity has been reduced from your cart/checkout")
            return redirect("checkout")
    else:
        messages.success(request, f"'{product.name}' has been removed from your cart/checkout")
        return HttpResponseRedirect(request.META.get("HTTP_REFERER"))

    return render(request, 'market/checkout.html', {})


@login_required
def delete_from_checkout(request, pk):
    customer = request.user
    product = get_object_or_404(Product, pk=pk)
    print(Checkout.objects.filter(user=customer, product=product, complete=False))
    orderItem, created = Checkout.objects.get_or_create(user=customer, product=product, complete=False)
    if Checkout.objects.filter(user=customer, product=product, complete=False).exists():
        print(Checkout.objects.filter(user=customer, product=product, complete=False))
        orderItem.delete()
        messages.success(request, f"'{product.name}' has been removed from your cart")
        return redirect("checkout")
    else:
        messages.success(request, f"'{product.name}' doesn't exists in your cart")
        return HttpResponseRedirect(request.META.get("HTTP_REFERER"))


@login_required
def checkout(request):
    notification = Notification.objects.filter(user=request.user, is_seen=False).order_by("-id")[:10]
    notification_count = Notification.objects.filter(user=request.user, is_seen=False).count()
    check_out_list = Checkout.objects.filter(user=request.user, complete=False).order_by("-id")
    get_cart_total = sum([(item.product.price * item.quantity) for item in check_out_list])
    if get_cart_total >= 200000:
        get_shipping_fee = 0
    else:
        get_shipping_fee = sum([item.product.shipping_fee for item in check_out_list])
    context = {
        "notification_count": notification_count,
        "notification": notification,
        "items": check_out_list,
        "get_cart_total": get_cart_total,
        "get_shipping_fee": get_shipping_fee,
        "get_cart_items": total_cart_items(request),
        "paystack_public_key": settings.PAYSTACK_PUBLIC_KEY
    }
    return render(request, "products/checkout.html", context)


@login_required
def process_order(request):
    data = json.loads(request.body)
    transaction_id = datetime.now().timestamp()
    reference = str(data['ref']['reference'])
    check_out_list = Checkout.objects.filter(user=request.user, complete=False).order_by("-id")

    queryset = []
    for item in check_out_list:
        queryset.append(item.complete == True)
        item.complete = True
        item.save()

    order = Order.objects.create(
        user=request.user,
        transaction_id=transaction_id,
        ordered=True,
        reference=reference
    )

    order.order_item.set([item for item in check_out_list])
    order.default_order_item = [str(item) for item in order.order_item.all()]
    order.default_price = sum([item.get_total for item in check_out_list])
    order.save()

    product_queryset = []
    for item in check_out_list:
        product_queryset.append(item.product.product_purchase + item.quantity)
        item.product.product_purchase += item.quantity
        item.product.save()

    notification = Notification.objects.create(
        user=request.user,
        notification_type=1
    )
    notification.orders.set([item for item in check_out_list])
    notification.save()

    return JsonResponse('Payment complete!', safe=False)


def paginate_products(request):
    pass


def high_low_price_products(request):
    pass


def recent_products(request):
    pass


@login_required
def product_review(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        form = ReviewBox(request.POST)
        if form.is_valid():
            form = form.save(commit=False)
            form.customer_info = request.user
            form.product = product
            form.default_product = str(product)
            form.save()

            ratings = [i.rating for i in product.productreview_set.all()]
            product.rating_count = round(mean(ratings))
            product.save()

    data = {
        "comment": request.POST.get('comment', None),
        "message": "Your review has been sent"
    }

    return JsonResponse(data)
