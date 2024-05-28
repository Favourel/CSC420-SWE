from django.urls import path
from . import views as product_view

urlpatterns = [
    path("", product_view.home, name="home"),
    path("products/", product_view.products_view, name="products"),
    path('products/<uuid:pk>/', product_view.products_details, name='product-detail'),
    path("search/", product_view.search_view, name="search"),
    path("<uuid:pk>/add_to_checkout/", product_view.add_to_checkout, name="add_to_checkout"),
    path("<uuid:pk>/remove_from_checkout/", product_view.remove_from_checkout, name="remove_from_checkout"),
    path("<uuid:pk>/delete_from_checkout/", product_view.delete_from_checkout, name="delete_from_checkout"),
    path("checkout/", product_view.checkout, name="checkout"),
    path("process/order/", product_view.process_order, name="process_order"),
    path("paginate_products/", product_view.paginate_products, name="paginate_products"),
    path("high_low_price_products/", product_view.high_low_price_products, name="high_low_price_products"),
    path("recent_products/", product_view.recent_products, name="recent_products"),
    path("product/<uuid:pk>/review", product_view.product_review, name="productReview"),

]
