from django.urls import path
from . import views as user_view

urlpatterns = [
    path("notification/", user_view.notification, name="notification"),
    path("update_notification/", user_view.update_notification, name="update_notification"),
    path("update_profile/", user_view.update_profile, name="update_profile"),
]