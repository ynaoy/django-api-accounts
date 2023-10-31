"""
Viewで使うカスタムパーミッションを定義するファイル
"""
from rest_framework.permissions import BasePermission
from .utils import verify_jwt

class OnlyYouPerm(BasePermission):
    """
    個人ページにおいて、ユーザー自身のリクエストしか通さない
    """
    def has_permission(self, request, view):
        objects = verify_jwt(request)
        if(objects):
            return objects[0].pk == view.kwargs['pk'] #objects[0]はUserモデル
        else:
            return False
        
class OnlyLogoutPerm(BasePermission):
    """
    ログアウト中のユーザーしか通さない
    """
    raise_exception = True
    def has_permission(self, request, view):
        objects = verify_jwt(request)
        return not objects