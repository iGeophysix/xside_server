import json

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

test_users = [
    {"username": "testuser1", "email": "testuser1@testuser1.com", "password": "testpassword1", "first_name": "Name", "last_name": "Surnname"},
    {"username": "testuser2", "email": "testuser2@testuser2.com", "password": "testpassword2", "first_name": "John", "last_name": "Doe"},
]


class LoginTest(TestCase):
    def setUp(self):
        for user in test_users:
            new_user = User.objects.create(username=user["username"], email=user["email"], first_name=user["first_name"], last_name=user["last_name"])
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

    def test_userinfo(self):
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
        token = result['access']
        res = self.client.get(reverse('client_space:user'),
                              content_type='application/json',
                              HTTP_AUTHORIZATION=f'Bearer {token}'
                              )
        self.assertEquals(res.status_code, 200)
        response = res.json()
        self.assertTrue(response['data']['first_name'], USER1['first_name'])
        self.assertTrue(response['data']['last_name'], USER1['last_name'])
        self.assertTrue(response['data']['email'], USER1['email'])

        data = {
            'first_name': 'Jane',
            'last_name': "Donowan",
            "email": "jane@aaa.com"
        }
        res = self.client.post(reverse('client_space:user'),
                              data=data,
                              content_type='application/json',
                              HTTP_AUTHORIZATION=f'Bearer {token}'
                              )

        self.assertEquals(res.status_code, 200)
        updated_user = User.objects.get(email=data["email"])
        self.assertEquals(updated_user.first_name, data['first_name'])
        self.assertEquals(updated_user.last_name, data['last_name'])
