from django.test import TestCase
from .test.model_tests import UserModelTests
from .test.view_tests import UserViewTests
from .test.utils_tests import UserUtilsTests
from .test.permissions_tests import UserPermissionsTests


class Tests(TestCase):
  UserModelTests()
  UserViewTests()
  UserUtilsTests()
  UserPermissionsTests()