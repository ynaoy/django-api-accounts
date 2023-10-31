"""
このアプリで使うカスタムメソッド達
"""
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework import status
from rest_framework.response import Response
import datetime

def get_jwt(user):
    """
    jwtを発行する
    """
    try:
      refresh = RefreshToken.for_user(user)
      return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
      }
    except:
      return {}

def get_jwt_and_set_cookie(user, response):
    """
    jwtを発行して、クッキーにセットする
    """
    token = get_jwt(user)
    if(token):
      response.set_cookie("Authorization", "JWT "+token["access"], httponly=True, max_age=datetime.timedelta(minutes=30))
      response.set_cookie("refresh", token["refresh"], httponly=True, max_age=datetime.timedelta(days=14))
    return response

def verify_jwt(request):
    """
    リクエストのヘッダーにあるjwtを使ってユーザー認証する
    [User,payload]か、Noneを返す
    """
    return JWTAuthentication().authenticate(request)