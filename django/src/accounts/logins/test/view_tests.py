from django.test import TestCase
from django.urls import reverse
from unittest import skip
from ..models import User
from ..utils import get_jwt

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

def create_jwt_headers(user):
  jwt_dict = get_jwt(user)
  return {"Authorization": "JWT "+jwt_dict["access"]}

class UserViewTests(TestCase):

  def test_index_view(self):
    """
    index_viewにGETメソッドを送ったときに
    帰ってくるJsonオブジェクトに含まれるユーザーの数とユーザーモデルに含まれるユーザーの数が同じ
    """
    create_default_user()
    response = self.client.get(reverse("logins:index"),
                               content_type="application/json")
    self.assertEqual(response.status_code, 200)
    user_num_by_json = len(response.data)
    self.assertEqual(User.objects.all().count(), user_num_by_json)
  
  def test_signup_view_post(self):
    """
    signup_viewにPOSTメソッドを送ったときにユーザーが追加されてログインされている
    """
    response = self.client.post(reverse("logins:signup"),
                                { "user_name": "Test User",
                                  "email": "example@example.com",
                                  "password": "password"},
                                content_type="application/json")
    # クッキーにアクセストークンとリフレッシュトークンが存在する
    self.assertTrue(response.cookies.get("Authorization"))
    self.assertTrue(response.cookies.get("refresh"))

    # ユーザーが追加されている
    self.assertTrue(User.objects.filter(email="example@example.com"))

  def test_signup_view_post_with_invalid_params(self):
    """
    signup_viewに無効なパラメータでPOSTメソッドを送ったときにユーザーが追加されない、ログインされない
    """
    response = self.client.post(reverse("logins:signup"),
                                { "user_name": "a"*16,
                                  "email": "example@example.com",
                                  "password": "password"},
                                content_type="application/json")
    # クッキーが空
    self.assertFalse(response.cookies)
    # ユーザーが追加されていない
    self.assertFalse(User.objects.filter(email="example@example.com"))

  def test_update_view_patch(self):
    """
    logins/update/<users_id>にPATCHメソッドを送ったときにユーザーが更新される
    """
    test_user = create_default_user()
    headers = create_jwt_headers(test_user)
    response = self.client.patch(reverse("logins:update", args=[test_user.pk]),
                                { "user_name":"Changed User",
                                  "email":"changedemail@example.com",
                                },
                                headers = headers,
                                content_type="application/json"
                                )
    self.assertEqual(response.status_code, 200)
    test_user = User.objects.get(pk=test_user.pk)
    self.assertEqual(test_user.user_name,"Changed User")
    self.assertEqual(test_user.email,"changedemail@example.com")

  def test_update_view_patch_with_user_name(self):
    """
    パラメータにメールアドレスをセットして
    logins/update/<users_id>にPATCHメソッドを送ったときにユーザーが更新される
    """
    test_user = create_default_user()
    headers = create_jwt_headers(test_user)
    response = self.client.patch(reverse("logins:update", args=[test_user.pk]),
                                { "user_name":"Changed User",
                                  "email":test_user.email,
                                   },
                                headers = headers,
                                content_type="application/json"
                                )
    self.assertEqual(response.status_code, 200)
    test_user = User.objects.get(pk=test_user.pk)
    self.assertEqual(test_user.user_name,"Changed User")

  def test_update_view_patch_with_email(self):
    """
    パラメータにユーザーネームをセットして
    logins/update/<users_id>にPATCHメソッドを送ったときにユーザーが更新される
    """
    test_user = create_default_user()
    headers = create_jwt_headers(test_user)
    response = self.client.patch(reverse("logins:update", args=[test_user.pk]),
                                { "user_name":test_user.user_name,
                                  "email":"changedemail@example.com",
                                   },
                                headers = headers,
                                content_type="application/json"
                                )
    self.assertEqual(response.status_code, 200)
    test_user = User.objects.get(pk=test_user.pk)
    self.assertEqual(test_user.email,"changedemail@example.com")

  def test_update_view_patch_with_not_login(self):
    """
    非ログイン時にlogins/update/<users_id>にPATCHメソッドを送ったときに
    ユーザーが更新されず、401エラーが返ってくる
    """
    test_user = create_default_user()
    response = self.client.patch(reverse("logins:update", args=[test_user.pk]),
                                { "user_name":"Changed User",
                                  "email":"changedemail@example.com",
                                   },
                                content_type="application/json"
                                )
    self.assertEqual(response.status_code, 401)
    test_user = User.objects.get(pk=test_user.pk)
    self.assertNotEqual(test_user.user_name,"Changed User")
    self.assertNotEqual(test_user.email,"changedemail@example.com")

  def test_update_view_patch_on_another_user(self):
    """
    logins/update/<another_users_id>にPATCHメソッドを送ったときに
    別のユーザーの情報が更新されず、403エラーが返ってくる
    """
    test_user = create_default_user()
    headers = create_jwt_headers(test_user)
    another_user = create_default_user(user_name="another_user",
                                       email="another_email@example.com")
    response = self.client.patch(reverse("logins:update", args=[another_user.pk]),
                                { "user_name":"Changed User",
                                  "email":"changedemail@example.com",
                                   },
                                headers=headers,
                                content_type="application/json"
                                )
    self.assertEqual(response.status_code, 403)
    another_user = User.objects.get(pk=another_user.pk)
    self.assertNotEqual(another_user.user_name,"Changed User")
    self.assertNotEqual(another_user.email,"changedemail@example.com")

  def test_update_view_patch_with_password(self):
    """
    logins/update/<users_id>にPATCHメソッドを送ったときに
    リクエストは成功するが許可されていないフィールドは変更できない
    """
    test_user = create_default_user()
    headers = create_jwt_headers(test_user)
    old_password = test_user.password
    response = self.client.patch(reverse("logins:update", args=[test_user.pk]),
                                {"password":"change_password"},
                                headers=headers,
                                content_type="application/json"
                                )
    self.assertEqual(response.status_code, 200)
    test_user = User.objects.get(pk=test_user.pk)
    self.assertEqual(old_password, test_user.password)

  def test_update_password_view_patch(self):
    """
    logins/update_password/<users_id>にPATCHメソッドを送ったときにパスワードが更新される
    """
    test_user = create_default_user()
    old_password = test_user.password
    headers = create_jwt_headers(test_user)
    response = self.client.patch(reverse("logins:update_password", args=[test_user.pk]),
                                { "password":"change_password" },
                                headers = headers,
                                content_type="application/json"
                                )
    self.assertEqual(response.status_code, 200)
    test_user = User.objects.get(pk=test_user.pk)
    self.assertNotEqual(old_password, test_user.password)

  def test_update_password_view_patch_with_not_login(self):
    """
    非ログイン時にlogins/update_password/<users_id>にPATCHメソッドを送ったときに
    パスワードが更新されず、401エラーが返ってくる
    """
    test_user = create_default_user()
    old_password = test_user.password
    response = self.client.patch(reverse("logins:update_password", args=[test_user.pk]),
                                { "password":"change_password" },
                                content_type="application/json"
                                )
    self.assertEqual(response.status_code, 401)
    test_user = User.objects.get(pk=test_user.pk)
    self.assertEqual(old_password, test_user.password)

  def test_update_password_view_patch_on_another_user(self):
    """
    logins/update_password/<another_users_id>にPATCHメソッドを送ったときに
    別のユーザーのパスワードが更新されず、403エラーが返ってくる
    """
    test_user = create_default_user()
    headers = create_jwt_headers(test_user)
    another_user = create_default_user(user_name="another_user",
                                       email="another_email@example.com")
    old_password = another_user.password
    response = self.client.patch(reverse("logins:update_password", args=[another_user.pk]),
                                { "password":"change_password" },
                                headers=headers,
                                content_type="application/json"
                                )
    self.assertEqual(response.status_code, 403)
    another_user = User.objects.get(pk=another_user.pk)
    self.assertEqual(old_password, another_user.password)

  def test_update_password_view_patch_with_password(self):
    """
    logins/update_password/<users_id>にPATCHメソッドを送ったときに
    リクエストは成功するが許可されていないフィールドは変更できない
    """
    test_user = create_default_user()
    headers = create_jwt_headers(test_user)
    old_password = test_user.password
    response = self.client.patch(reverse("logins:update_password", args=[test_user.pk]),
                                {"user_name":"Changed User"},
                                headers=headers,
                                content_type="application/json"
                                )
    self.assertEqual(response.status_code, 200)
    test_user = User.objects.get(pk=test_user.pk)
    self.assertEqual(old_password, test_user.password)

  def test_login_view_post(self):
    """
    login_viewにPOSTメソッドを送ったときにログインされている
    """
    test_user = create_default_user()
    response = self.client.post(reverse("logins:login"),
                                { "email": test_user.email,
                                  "password": "password"},
                                content_type="application/json")
    self.assertEqual(response.status_code, 201)
    # クッキーにアクセストークンとリフレッシュトークンが存在する
    self.assertTrue(response.cookies.get("Authorization"))
    self.assertTrue(response.cookies.get("refresh"))

  def test_login_view_post_invalid_password(self):
    """
    誤ったメールアドレスでlogin_viewにPOSTメソッドを送ったときにログインされない
    """
    test_user = create_default_user()
    response = self.client.post(reverse("logins:login"),
                                { "email": test_user.email,
                                  "password": "ivalid_password"},
                                content_type="application/json")
    self.assertEqual(response.status_code, 401)
    # クッキーが空
    self.assertFalse(response.cookies)

  def test_login_view_post_invalid_email(self):
    """
    誤ったパスワードでlogin_viewにPOSTメソッドを送ったときにログインされない
    """
    test_user = create_default_user()
    response = self.client.post(reverse("logins:login"),
                                { "email": "invalidexample@example.com",
                                  "password": "password"},
                                content_type="application/json")
    self.assertEqual(response.status_code, 401)
    # クッキーが空
    self.assertFalse(response.cookies)

  def test_login_view_post_with_login(self):
    """
    ログイン中にlogin_viewにPOSTメソッドを送ったときにエラーが表示される
    """
    test_user = create_default_user()
    headers = create_jwt_headers(test_user)
    response = self.client.post(reverse("logins:login"),
                                { "email": test_user.email,
                                  "password": "password"},
                                headers=headers,
                                content_type="application/json")
    self.assertEqual(response.status_code, 403)
    # クッキーが空
    self.assertFalse(response.cookies)

  def test_logout_view_get_with_not_login(self):
    """
    ログインしていないときにlogout_viewにDELETEメソッドを送ったら
    401エラーが返ってくる
    """
    response = self.client.delete(reverse("logins:logout"),
                                  content_type="application/json")
    self.assertEqual(response.status_code, 401)

  def test_logout_view_get(self):
    """
    logout_viewにDELETEメソッドを送ったときにログアウト状態になる
    """
    test_user = create_default_user()
    headers = create_jwt_headers(test_user)
    response = self.client.delete(reverse("logins:logout"),
                                  headers=headers,
                                  content_type="application/json")
    self.assertEqual(response.status_code, 200)
    # クッキーにアクセストークンとリフレッシュトークンが存在しない
    self.assertFalse(response.cookies["Authorization"]["max-age"])
    self.assertFalse(response.cookies["refresh"]["max-age"])

