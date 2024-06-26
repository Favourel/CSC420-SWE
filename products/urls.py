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
    path("apply_coupon/", product_view.apply_coupon, name="apply_coupon"),

    path("product/<uuid:pk>/review", product_view.product_review, name="productReview"),

]
