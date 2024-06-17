import uuid
import requests
from requests.exceptions import RequestException
from django.contrib.auth.backends import ModelBackend
from users.models import User, Notification
from django.contrib.auth import get_user_model
import logging
from django.contrib import messages


logger = logging.getLogger(__name__)


class UniversityAuthBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        logger.debug(f"Attempting authentication for user: {username}")
        # Make a request to the university's authentication API
        auth_url = 'https://portal.unilorin.edu.ng/api/login'
        payload = {'username': username, 'password': password}

        try:
            response = requests.post(auth_url, data=payload)

            response_data = response.json()

            if response.status_code == 200:

                # Authentication successful, retrieve user data
                user_data = response_data['data']
                user_model = get_user_model()

                # Retrieve other data
                # department_name = user_data['department']
                role_name = user_data['role_names']

                # Check if user exists in our system, if not create a new one
                user, created = user_model.objects.get_or_create(username=username, password=password)
                if created:
                    user.email = user_data.get('email', '')
                    user.first_name = user_data.get('firstname', '')
                    user.last_name = user_data.get('lastname', '')
                    user.phone_number = user_data.get('phone', '')

                    # user.department = department_name.get('name', '')
                    user.status = role_name[0]

                    user.save()
                    Notification.objects.create(user=user, notification_type=2)
                    messages.success(request, f"Account successfully created for {user}!")
                return user
            else:
                raise RequestException(
                    "Authentication failed with status code: " + str(response.status_code))  # Raise exception

        except Exception as e:
            # Handle exceptions (e.g., network issues, server errors)
            print(f"Authentication failed: {str(e)}")
            return None
