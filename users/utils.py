# utils.py

import requests


def get_visitor_location(ip_address):
    ipinfo_api_key = 'f2d2b2edba9968'  # Get your API key by signing up at https://ipinfo.io/signup

    url = f'https://ipinfo.io/{ip_address}?token={ipinfo_api_key}'
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        print(data.get('city'))
        return {
            'city': data.get('city'),
            'region': data.get('region'),
            'country': data.get('country'),
            "timezone": data.get('timezone')
        }
    # return None

# from ipware import get_client_ip
# from .utils import get_visitor_location
#
# if client_ip:
#     location_data = get_visitor_location(client_ip)
#     if location_data:
#         city = location_data.get('city')
#         region = location_data.get('region')
#         country = location_data.get('country')
#         timezone = location_data.get('timezone')
#         visitor, created = Visitor.objects.get_or_create(ip_address=client_ip,
#                                                          city=city, country=country,
#                                                          region=region, timezone=timezone)
#         # `visitor` represents the visitor record in the database
#         visitor.save()
