from django.test import TestCase
from unittest import skip
from ..models import User
from ..utils import get_jwt, get_jwt_and_set_cookie, verify_jwt
from rest_framework import status
from rest_framework.response import Response
from django.http import HttpRequest
from rest_framework.request import Request

def create_default_user(user_name="Test User",
                       email="example@example.com",
                       password="password"):
  """
  パラメータのユーザーを作成する
  """
  user= User.objects.create_user(user_name=user_name,
                                       email=email,
                                       password=password)
  return user

class UserUtilsTests(TestCase):

  def setUp(self):
    self.user = create_default_user()

  def test_get_jwt_with_valid_user(self):
    """
    有効なユーザーを引数にしてget_jwt(user)関数を実行するとjwtが返ってくる
    """
    jwt = get_jwt(self.user)
    self.assertTrue(jwt["access"])
    self.assertTrue(jwt["refresh"])

  def test_get_jwt_with_invalid_user(self):
    """
    無効なユーザーを引数にしてget_jwt(user)関数を実行すると空のオブジェクトが返ってくる
    """
    jwt = get_jwt("")
    # jwtが空
    self.assertFalse(jwt)

  def test_get_jwt_and_set_cookie_with_valid_params(self):
    """
    有効なユーザーとレスポンスを引数にしてget_jwt_and_set_cookie(user,responce)を実行すると
    クッキーにjwtトークンがセットされる
    """
    response = Response(status=status.HTTP_200_OK)
    response = get_jwt_and_set_cookie(self.user, response)
    self.assertTrue(response.cookies.get("Authorization"))
    self.assertTrue(response.cookies.get("refresh"))

  def test_get_jwt_and_set_cookie_with_invalid_params(self):
    """
    無効なユーザーを引数にしてget_jwt_and_set_cookie(user,responce)を実行すると
    クッキーにjwtトークンがセットされない
    """
    response = Response(status=status.HTTP_200_OK)
    response = get_jwt_and_set_cookie("", response)
    # クッキーが空
    self.assertFalse(response.cookies)

  def test_verify_jwt_with_valid_jwt(self):
    """
    jwtがセットされたリクエストを引数にしてverify_jwt(request)を実行すると
    解凍されたjwtが返ってくる
    """
    request = Request(HttpRequest())
    jwt = get_jwt(self.user)
    request.META["HTTP_AUTHORIZATION"]="JWT "+jwt["access"]
    raw_jwt = verify_jwt(request)
    # 認証されると(UserModel,payload)が返ってくる
    self.assertTrue(raw_jwt)

  def test_verify_jwt_with_invalid_jwt(self):
    """
    jwtがセットされていないリクエストを引数にしてverify_jwt(request)を実行すると
    Noneが返ってくる
    """
    request = Request(HttpRequest())
    raw_jwt = verify_jwt(request)
    # 認証に失敗するとNoneが返ってくる
    self.assertFalse(raw_jwt)