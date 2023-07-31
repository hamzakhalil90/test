import json
import re

from django.utils import timezone
from django.utils.deprecation import MiddlewareMixin
from rest_framework.renderers import JSONRenderer

from user_management.models import User
from utils.reusable_methods import create_response


class LockoutMiddleware(MiddlewareMixin):
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.method == "POST" and request.path == "/login":
            try:
                email = json.loads(request.body.decode('utf-8')).get('email')
            except:
                ptrn = 'email"\r\n\r\n.*'
                email = re.findall(
                    ptrn, request.body.decode(
                        'utf-8'))[0].replace(
                    'email"', '').strip() if re.findall(
                    ptrn, request.body.decode('utf-8')) else ""
            response = self.get_response(request)
            if response.status_code == 401:
                try:
                    user = User.objects.get(email=email)
                except Exception as e:
                    response = create_response({}, "Incorrect Email or Password",
                                               status_code=401)
                    response.accepted_renderer = JSONRenderer()
                    response.accepted_media_type = "application/json"
                    response.renderer_context = {}
                    response.render()
                    return response
                if user.last_failed_time:
                    if (timezone.now() - user.last_failed_time).seconds >= 3600:
                        user.failed_login_attempts = 0
                        user.last_failed_time = None
                        user.save()
                user.failed_login_attempts += 1
                user.last_failed_time = timezone.now()
                user.save()

                if user.failed_login_attempts >= 5:
                    user.is_active = "INACTIVE"
                    user.is_locked = True
                    user.save()
                    response = create_response({}, "Your account has been locked. Please contact with administrator.",
                                               status_code=401)
                    response.accepted_renderer = JSONRenderer()
                    response.accepted_media_type = "application/json"
                    response.renderer_context = {}
                    response.render()
                    return response

            return response

        return self.get_response(request)
