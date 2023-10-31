from django.contrib.auth.hashers import check_password
from rest_framework import status
from rest_framework.permissions import AllowAny,IsAuthenticated
from rest_framework.generics import ListAPIView, CreateAPIView, UpdateAPIView, DestroyAPIView
from rest_framework.response import Response
from .serializer import UserSerializer
from .models import User
from .permissions import OnlyYouPerm, OnlyLogoutPerm
from .utils import get_jwt_and_set_cookie, verify_jwt
    
class IndexView(ListAPIView):
    """
    ユーザー一覧用ビュー 
    """
    permission_classes = (AllowAny,)
    queryset = User.objects.all()
    serializer_class = UserSerializer

class SignupView(CreateAPIView):
    """
    ユーザー登録用ビュー 
    """
    permission_classes = (AllowAny,)
    queryset = User.objects.all()
    serializer_class = UserSerializer
    valid_fields = ("user_name",
                    "email",
                    "password",
                    )               
    
    def post(self, request, format=None, *args, **kwargs):
      serializer = self.serializer_class(data=request.data)
      if serializer.is_valid(valid_fields=self.valid_fields):
        user_name = serializer.validated_data["user_name"]
        email = serializer.validated_data["email"]
        password = serializer.validated_data["password"]
        user = serializer.create(user_name=user_name,
                                 email=email,
                                 password=password)
        # jwtを発行してクッキーにセットする。そのレスポンスを返す
        response = Response(serializer.validated_data, status=status.HTTP_201_CREATED)
        responce = get_jwt_and_set_cookie(user, response)
        return responce
      return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class UpdateView(UpdateAPIView):
    """
    ユーザー更新用ビュー 
    """
    permission_classes = (IsAuthenticated, OnlyYouPerm,)
    queryset = User.objects.all()
    serializer_class = UserSerializer
    valid_fields = ("user_name",
                    "email",
                    )

    def patch(self, request, format=None, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid(valid_fields=self.valid_fields):
            user = User.objects.get(pk=self.kwargs['pk'])
            user = serializer.update(user ,serializer.validated_data)
            # jwtを発行してクッキーにセットする。そのレスポンスを返す
            response = Response(serializer.validated_data, status=status.HTTP_200_OK)
            responce = get_jwt_and_set_cookie(user, response)
            return responce
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class UpdatePasswordView(UpdateAPIView):
    """
    パスワード更新用ビュー 
    """
    permission_classes = (IsAuthenticated, OnlyYouPerm,)
    queryset = User.objects.all()
    serializer_class = UserSerializer
    valid_fields = ("password",)

    def patch(self, request, format=None, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid(valid_fields=self.valid_fields):
            user = User.objects.get(pk=self.kwargs['pk'])
            user = serializer.update(user ,serializer.validated_data)
            # jwtを発行してクッキーにセットする。そのレスポンスを返す
            response = Response(serializer.validated_data, status=status.HTTP_200_OK)
            responce = get_jwt_and_set_cookie(user, response)
            return responce
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class LoginView(CreateAPIView):
    """
    ログイン用ビュー 
    """
    permission_classes = (AllowAny, OnlyLogoutPerm,)
    queryset = User.objects.all()
    serializer_class = UserSerializer
    valid_fields = ("email",
                    "password",
                    )               
    
    def post(self, request, format=None, *args, **kwargs):
      serializer = self.serializer_class(data=request.data)
      if serializer.is_valid(valid_fields=self.valid_fields):
        email = serializer.validated_data["email"]
        password = serializer.validated_data["password"]
        user_list = User.objects.filter(email=email)
        if user_list and check_password(password, user_list[0].password):
            user = user_list[0]
            # jwtを発行してクッキーにセットする。そのレスポンスを返す
            response = Response(serializer.validated_data, status=status.HTTP_201_CREATED)
            responce = get_jwt_and_set_cookie(user, response)
            return responce
        else:
            return Response(serializer.errors, status=status.HTTP_401_UNAUTHORIZED)
      return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class LogoutView(DestroyAPIView):
    """
    ログアウト用ビュー 
    """
    permission_classes = (IsAuthenticated,)          
    
    def delete(self, request, *args, **kwargs):
      if(verify_jwt(request)):
            response = Response(status=status.HTTP_200_OK)
            response.delete_cookie("Authorization")
            response.delete_cookie("refresh")
            return response
      return Response(status=status.HTTP_401_UNAUTHORIZED)
