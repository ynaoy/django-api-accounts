from django.test import TestCase
from unittest import skip
from ..models import User
from ..utils import get_jwt
from django.http import HttpRequest
from rest_framework.request import Request
from ..permissions import OnlyYouPerm, OnlyLogoutPerm

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

class UserPermissionsTests(TestCase):

  class viewMock():
    def __init__(self, id):
      self.kwargs = {"pk": id}

  def setUp(self):
    self.only_you_perm = OnlyYouPerm()
    self.only_logout_perm = OnlyLogoutPerm()
    self.user =  create_default_user()
    self.view = self.viewMock(self.user.id)

  def test_OnlyYouPerm_with_my_user(self):
    """
    OnlyYouPermクラスのhas_permission(request, view)にて
    ログイン中のユーザーのpk == viewのプロパティのpk の時Trueが返ってくる
    """
    request = Request(HttpRequest())
    jwt = get_jwt(self.user)
    request.META["HTTP_AUTHORIZATION"]="JWT "+jwt["access"]
    is_permission = self.only_you_perm.has_permission(request, self.view)
    self.assertTrue(is_permission)

  def test_OnlyYouPerm_another_user_accessed(self):
    """
    OnlyYouPermクラスのhas_permission(request, view)にて
    viewのプロパティのpkがログイン中のユーザーでない時Falseが返ってくる
    """
    request = Request(HttpRequest())
    another_user = create_default_user(user_name="another_user",
                                       email="anotheremail@example.com")
    jwt = get_jwt(another_user)
    request.META["HTTP_AUTHORIZATION"]="JWT "+jwt["access"]
    is_permission = self.only_you_perm.has_permission(request, self.view)
    self.assertFalse(is_permission)

  def test_OnlyYouPerm_whith_not_login(self):
    """
    OnlyYouPermクラスのhas_permission(request, view)にて
    ログインしていない時Falseが返ってくる
    """
    request = Request(HttpRequest())
    is_permission = self.only_you_perm.has_permission(request, self.view)
    self.assertFalse(is_permission)
    
  def test_OnlyLogoutPerm(self):
    """
    OnlyLogoutPermクラスのhas_permission(request, view)にて
    ユーザーがログインしていない時Trueが返ってくる
    """
    request = Request(HttpRequest())
    is_permission = self.only_logout_perm.has_permission(request, self.view)
    self.assertTrue(is_permission)

  def test_OnlyLogoutPerm_with_login(self):
    """
    OnlyLogoutPermクラスのhas_permission(request, view)にて
    ユーザーがログインしている時Falseが返ってくる
    """
    request = Request(HttpRequest())
    jwt = get_jwt(self.user)
    request.META["HTTP_AUTHORIZATION"]="JWT "+jwt["access"]
    is_permission = self.only_logout_perm.has_permission(request, self.view)
    self.assertFalse(is_permission)
