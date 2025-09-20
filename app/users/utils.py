import jwt
import datetime


class AuthService():

    def getToken(self, user):
        secret_key = 'abc'
        payload = {
            "user_id": user.id,
            "exp": datetime.datetime.now() + datetime.timedelta(minutes=30)
        }
        token = jwt.encode(payload, secret_key, algorithm='HS256')

        return token
