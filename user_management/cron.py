from utils.helper import send_password
from utils.reusable_methods import generate_dummy_password
from user_management.models import User, Token
import threading
import datetime


def superuser_password_alert():
    try:
        users = User.objects.filter(is_deleted=False, is_superuser=True)
        for user in users:
            try:
                dummy_password = generate_dummy_password()
                user.set_password(dummy_password)
                token = Token.objects.get(user=user.guid)
                token.token = dummy_password
                token.save()
                user.save()
                send_password(user.first_name, user.last_name, user.email, dummy_password)
                print("Mail sent to ", user.email, "at: ", datetime.datetime.now())
            except Exception as e:
                print(user, " --- ", e)
    except Exception as e:
        print(e)

