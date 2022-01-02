from django.test import TestCase
from django.contrib.auth.models import User
import json

test_users = [
    {"username": "testuser1", "email":"testuser1@testuser1.com", "password": "testpassword1"},
    {"username": "testuser2", "email":"testuser2@testuser2.com", "password": "testpassword2"},
]

class LoginTest(TestCase):
    def setUp(self):
        for user in test_users:
            new_user = User.objects.create(username=user["username"], email=user["email"])
            new_user.set_password(user["password"])
            new_user.save()

    def test_login(self):
        USER1 = test_users[0]
        res = self.client.post('/api/token/',
                               data=json.dumps({
                                   'email': USER1["email"],
                                   'password': USER1["password"],
                               }),
                               content_type='application/json',
                               )
        result = json.loads(res.content)
        self.assertTrue("access" in result)