import json

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from client_space.models import Client, ClientUser

test_user = {"username": "testuser", "email": "testuser@example.com", "password": "testpassword"}


class ClientTests(TestCase):
    def setUp(self):
        """Set up databse"""
        new_user = User.objects.create(username=test_user["username"], email=test_user["email"])
        new_user.set_password(test_user["password"])
        new_user.save()

        cl1, _ = Client.objects.get_or_create(name="Client1", )
        cl2, _ = Client.objects.get_or_create(name="Client2", )

        clu, _ = ClientUser.objects.get_or_create(user=new_user)
        clu.client.add(cl1)
        clu.save()

    def get_token(self):
        """Authorization request"""
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

    def test_get_clients_ok(self):
        """Created clients are accessible"""
        cl1 = Client.objects.get(name="Client1")
        cl2 = Client.objects.get(name="Client2")
        self.assertEqual(cl1.name, "Client1")
        self.assertEqual(cl2.name, "Client2")

        token = self.get_token()
        res = self.client.get(reverse('client_space:client'),
                              content_type='application/json',
                              HTTP_AUTHORIZATION=f'Bearer {token}'
                              )
        self.assertEquals(res.status_code, 200)
        data = res.json()
        self.assertEquals(data['count'], 1)
        self.assertEquals(data['data'][0]['name'], "Client1")

    def test_get_clients_unauthorized(self):
        """Check unauthorized access to client"""
        res = self.client.get(reverse('client_space:client', ),
                              content_type='application/json',
                              HTTP_AUTHORIZATION=f'Bearer WRONG TOKEN'
                              )
        self.assertEquals(res.status_code, 401)

    def test_get_one_client_ok(self):
        """Created one client is accessible"""

        token = self.get_token()
        client_id = Client.objects.get(name='Client1').pk
        res = self.client.get(reverse('client_space:client', kwargs={'client_id': client_id}),
                              content_type='application/json',
                              HTTP_AUTHORIZATION=f'Bearer {token}'
                              )
        self.assertEquals(res.status_code, 200)
        data = res.json()
        self.assertEquals(len(data), 1)
        self.assertEquals(data['data']['name'], "Client1")

    def test_get_one_client_forbidden(self):
        """Check user is not allowed to get non-linked client"""
        token = self.get_token()
        client_id = Client.objects.get(name='Client2').pk
        res = self.client.get(reverse('client_space:client', kwargs={'client_id': client_id}),
                              content_type='application/json',
                              HTTP_AUTHORIZATION=f'Bearer {token}'
                              )
        self.assertEquals(res.status_code, 404)

    def test_get_one_client_unauthorized(self):
        """Check unauthorized access to one client"""
        client_id = Client.objects.get(name='Client1').pk
        res = self.client.get(reverse('client_space:client', kwargs={'client_id': client_id}),
                              content_type='application/json',
                              HTTP_AUTHORIZATION=f'Bearer WRONG TOKEN'
                              )
        self.assertEquals(res.status_code, 401)
