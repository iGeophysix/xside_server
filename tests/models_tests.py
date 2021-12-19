import json

from django.contrib.auth.models import User
from django.test import TestCase

test_user = {"username": "testuser", "email": "testuser@example.com", "password": "testpassword"}


class ClientTest(TestCase):
    def setUp(self):
        new_user = User.objects.create(username=test_user["username"], email=test_user["email"])
        new_user.set_password(test_user["password"])
        new_user.save()

    def get_token(self):
        res = self.client.post('/api/token/',
                               data=json.dumps({
                                   'email': test_user["email"],
                                   'password': test_user["password"],
                               }),
                               content_type='application/json',
                               )
        result = json.loads(res.content)
        self.assertTrue("access" in result)
        return result["access"]

    def test_add_client_forbidden(self):
        res = self.client.post('/api/client/',
                               data=json.dumps({
                                   'name': 'TestClient'
                               }),
                               content_type='application/json',
                               )
        self.assertEquals(res.status_code, 401)
        res = self.client.post('/api/client/',
                               data=json.dumps({
                                   'name': 'TestClient'
                               }),
                               content_type='application/json',
                               HTTP_AUTHORIZATION=f'Bearer WRONG TOKEN'
                               )
        self.assertEquals(res.status_code, 401)

    def test_add_client_ok(self):
        token = self.get_token()
        res = self.client.post('/api/client/',
                               data=json.dumps({
                                   'name': "TestClient",
                               }),
                               content_type='application/json',
                               HTTP_AUTHORIZATION=f'Bearer {token}'
                               )
        self.assertEquals(res.status_code, 201)
        result = json.loads(res.content)["data"]
        self.assertEquals(result["name"], 'TestClient')

    def test_add_client_not_duplicate(self):
        token = self.get_token()
        res = self.client.post('/api/client/',
                               data=json.dumps({
                                   'name': "TestClient",
                               }),
                               content_type='application/json',
                               HTTP_AUTHORIZATION=f'Bearer {token}'
                               )
        self.assertEquals(res.status_code, 201)

        res = self.client.post('/api/client/',
                               data=json.dumps({
                                   'name': "TestClient",
                               }),
                               content_type='application/json',
                               HTTP_AUTHORIZATION=f'Bearer {token}'
                               )
        self.assertEquals(res.status_code, 400, 'Duplicate names in Clients should not be allowed')
