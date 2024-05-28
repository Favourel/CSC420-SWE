from datetime import datetime

from django.conf import settings
from django.db import models
from django.contrib.auth.models import AbstractUser

from products.models import Checkout


# Create your models here.


class User(AbstractUser):
    phone_number = models.CharField(max_length=15, null=True, blank=True)


class Notification(models.Model):
    NOTIFICATION_TYPES = (
        (1, "Order"), (2, "Account Created"),
    )

    user = models.ForeignKey(settings.AUTH_USER_MODEL, blank=True, null=True, on_delete=models.CASCADE,
                             related_name="noti_to_user")

    notification_type = models.IntegerField(choices=NOTIFICATION_TYPES)
    orders = models.ManyToManyField(Checkout, blank=True)

    date_posted = models.DateTimeField(default=datetime.now)
    is_seen = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.user} notification'
