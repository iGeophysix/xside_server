"""
Test 1:
SetUp:
- Create 2 clients
- Create user and link user to one client
- Create one item and link it to client
test:
- request all items - get one created
- request all items specify pages, page size and fields to show
- request created item - get 200 and item info
- request non-existing item - get 404 Not found
- request without authorization - get 401 Not authorized
- request creation of a new item with correct parameters - get 200, check images are uploaded, check polygons are created
- request creation of a new item with wrong parameters - get 400 for each wrong parameter
- request POST a new Item, PUT with updates, DELETE the Item
- request POST a new Item, POST the same message - get 401 about duplicated name
- write tests for each validation in item.save_item
"""

import json

from django.contrib.auth.models import User
from django.contrib.gis.geos import GEOSGeometry
from django.test import TestCase
from django.urls import reverse

from client_space.models import Client, ClientUser, Item

test_user = {"username": "testuser", "email": "testuser@example.com", "password": "testpassword"}


class ItemTests(TestCase):
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

        areas1 = GEOSGeometry("""{"type": "MultiPolygon", "coordinates": [[[[37.611174657940857, 55.746186227486824], [37.607576809823506, 55.74094860448799],
                                                            [37.607763223350041, 55.739088538942028], [37.608455233275883, 55.738581936475846],
                                                            [37.610508799552903, 55.738936124770973], [37.613517064601176, 55.741764513942051],
                                                            [37.618113197386265, 55.74386441618126], [37.622807733714573, 55.745659618903289],
                                                            [37.626173906028264, 55.746243218923041], [37.629024423658848, 55.746067337798848],
                                                            [37.632009387016289, 55.745486471543288], [37.635921556502588, 55.743905935600388],
                                                            [37.638293299824007, 55.740940583086676], [37.63899436220526, 55.738765212568367],
                                                            [37.640091720968485, 55.736223052931521], [37.642591707408428, 55.732811602613104],
                                                            [37.64949403703212, 55.73107216164567], [37.643949910998344, 55.742547567139376],
                                                            [37.63832900673151, 55.747489555525512], [37.628320343792431, 55.749215999489572],
                                                            [37.618700936436653, 55.748617442150525], [37.611174657940857, 55.746186227486824]]]]}""")
        areas2 = GEOSGeometry("""{"type": "MultiPolygon", "coordinates": [[[[37.53638963683332, 55.768772401070819], [37.532968143039959, 55.739514903394827],
                                                            [37.59325530537307, 55.738398705210031], [37.592354938387864, 55.761502887932693],
                                                            [37.53638963683332, 55.768772401070819]]]]}""")

        item1, _ = Item.objects.get_or_create(client=cl1,
                                              name='Item1',
                                              areas=areas1,
                                              is_active=True,
                                              max_rate=10,
                                              max_daily_spend=1000)
        item2, _ = Item.objects.get_or_create(client=cl1,
                                              name='Item2',
                                              areas=areas2,
                                              is_active=True,
                                              max_rate=20,
                                              max_daily_spend=2000)
        item3, _ = Item.objects.get_or_create(client=cl2,
                                              name='Item3',
                                              areas=areas2,
                                              is_active=True,
                                              max_rate=20,
                                              max_daily_spend=2000)

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

    def test_get_items_ok(self):
        """Created Items are accessible"""
        i1 = Item.objects.get(client__name="Client1", name="Item1")
        i2 = Item.objects.get(client__name="Client1", name="Item2")
        self.assertEqual(i1.name, "Item1")
        self.assertEqual(i2.name, "Item2")

        token = self.get_token()
        res = self.client.get(reverse('client_space:item'),
                              content_type='application/json',
                              HTTP_AUTHORIZATION=f'Bearer {token}'
                              )
        self.assertEquals(res.status_code, 200)
        data = res.json()
        self.assertEquals(data['count'], 2)
        self.assertTrue((data['data'][0]['name'] == "Item1") or (data['data'][1]['name'] == "Item1"))

    def test_get_items_unauthorized(self):
        """Check unauthorized access to Item"""
        res = self.client.get(reverse('client_space:item', ),
                              content_type='application/json',
                              HTTP_AUTHORIZATION=f'Bearer WRONG TOKEN'
                              )
        self.assertEquals(res.status_code, 401)

    def test_get_one_item_ok(self):
        """Created one Item is accessible"""

        token = self.get_token()
        item_id = Item.objects.get(client__name='Client1', name='Item1').pk
        res = self.client.get(reverse('client_space:item', kwargs={'item_id': item_id}),
                              content_type='application/json',
                              HTTP_AUTHORIZATION=f'Bearer {token}'
                              )
        self.assertEquals(res.status_code, 200)
        data = res.json()
        self.assertEquals(len(data), 1)
        self.assertEquals(data['data']['name'], "Item1")

    def test_get_one_item_forbidden(self):
        """Check user is not allowed to get non-linked Item"""
        token = self.get_token()
        item_id = Item.objects.get(client__name='Client2', name='Item3').pk
        res = self.client.get(reverse('client_space:item', kwargs={'item_id': item_id}),
                              content_type='application/json',
                              HTTP_AUTHORIZATION=f'Bearer {token}'
                              )
        self.assertEquals(res.status_code, 401)

    def test_get_one_item_unauthorized(self):
        """Check unauthorized access to one Item"""
        item_id = Item.objects.get(client__name='Client1', name='Item2').pk
        res = self.client.get(reverse('client_space:item', kwargs={'item_id': item_id}),
                              content_type='application/json',
                              HTTP_AUTHORIZATION=f'Bearer WRONG TOKEN'
                              )
        self.assertEquals(res.status_code, 401)
