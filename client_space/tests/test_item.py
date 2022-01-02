"""
Test 1:
SetUp:
- Create 2 clients
- Create user and link user to one client
- Create one item and link it to client
test:
+ request all items - get one created
+ request all items specify pages, page size and fields to show
+ request created item - get 200 and item info
+ request non-existing item - get 404 Not found
+ request without authorization - get 401 Not authorized
+ request creation of a new item with correct parameters - get 200, check images are uploaded, check polygons are created
+ request creation of a new item with wrong parameters - get 400 for each wrong parameter
+ Full CRUD test: request POST a new Item, PUT with updates, DELETE the Item
+ request POST a new Item, POST the same message - get 401 about duplicated name
"""
import filecmp
import json
import os

from django.contrib.auth.models import User
from django.contrib.gis.geos import GEOSGeometry
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient

from client_space.models import Client, ClientUser, Item, ItemFile

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
        """request non-existing item - get 404 Not found"""

        token = self.get_token()
        res = self.client.get(reverse('client_space:item', kwargs={'item_id': 9999999}),
                              content_type='application/json',
                              HTTP_AUTHORIZATION=f'Bearer {token}'
                              )
        self.assertEquals(res.status_code, 404)

    def test_get_one_nonexistent_item(self):
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

    def test_get_items_with_pagination(self):
        """Created Items are accessible
        request all items specify pages, page size and fields to show
        """
        token = self.get_token()
        res = self.client.get(reverse('client_space:item'), data={'page_size': 1, },
                              content_type='application/json',
                              HTTP_AUTHORIZATION=f'Bearer {token}'
                              )
        self.assertEquals(res.status_code, 200)
        data = res.json()
        self.assertEquals(data['count'], 2)
        self.assertTrue(len(data['data']), 1)

        res2 = self.client.get(reverse('client_space:item'), data={'page_size': 1, 'page': 1},
                               content_type='application/json',
                               HTTP_AUTHORIZATION=f'Bearer {token}'
                               )
        self.assertEquals(res2.status_code, 200)
        data2 = res2.json()
        self.assertEquals(data2['count'], 2)
        self.assertTrue(len(data2['data']), 1)
        self.assertNotEqual(data2['data'], data['data'])

        res2 = self.client.get(reverse('client_space:item'), data={'page_size': 1, 'page': 5},
                               content_type='application/json',
                               HTTP_AUTHORIZATION=f'Bearer {token}'
                               )
        self.assertEquals(res2.status_code, 200)
        data2 = res2.json()
        self.assertEquals(data2['count'], 2)
        self.assertEquals(data2['data'], [])

        res2 = self.client.get(reverse('client_space:item'), data={'page_size': 100, 'page': 0},
                               content_type='application/json',
                               HTTP_AUTHORIZATION=f'Bearer {token}'
                               )
        self.assertEquals(res2.status_code, 200)
        data2 = res2.json()
        self.assertEquals(data2['count'], 2)
        self.assertEquals(len(data2['data']), 2)

    def test_create_item_ok(self):
        """request creation of a new item with correct parameters
        - get 200, check images are uploaded, check polygons are created"""
        token = self.get_token()
        path_to_image = os.path.join('client_space', 'tests', 'tested.png')
        image_file = open(path_to_image, 'rb')
        data = {
            'client': 'Client1',
            'name': 'Item5',
            'areas': '{"type": "MultiPolygon", "coordinates":[[[[37.60200012009591, 55.753318768941305], [37.60157692828216, 55.750842010116045], [37.60936881881207,55.74906941558997], [37.613412427017465, 55.75213456321547], [37.607292663306005, 55.75327778725062],[37.60314446990378, 55.75346674901331], [37.60200012009591, 55.753318768941305]]]]}',
            'is_active': 'true',
            'max_rate': 12,
            'max_daily_spend': 110.01,
            'image': [image_file, ],
        }
        resp = self.client.post(
            reverse('client_space:item'),
            data=data,
            format='multipart',
            HTTP_AUTHORIZATION=f'Bearer {token}'
        )
        image_file.close()

        self.assertEquals(resp.status_code, 201)
        new_item_id = resp.json()['data']['id']

        item = Item.objects.get(pk=new_item_id)
        self.assertEquals(item.name, data['name'])
        self.assertEquals(item.client.name, data['client'])
        self.assertEquals(item.max_rate, data['max_rate'])
        self.assertEquals(str(item.max_daily_spend), str(data['max_daily_spend']))
        self.assertEquals(json.loads(item.areas.geojson), json.loads(data['areas']))

        images = ItemFile.objects.filter(item=item)
        self.assertTrue(filecmp.cmp(str(images[0].image.file), path_to_image))

        item.delete()

    def test_create_item_not_ok(self):
        """request creation of a new item with wrong parameters
        - get 400 for each wrong parameter"""
        token = self.get_token()
        path_to_image = os.path.join('client_space', 'tests', 'tested.png')

        substitutions = [
            'client',  # not specified client
            'name',  # not specified client
            'image',  # not specified client
            'areas',  # not specified client
            {'client': 'Client5'},  # non-existing client
            {'client': 'Client2'},  # not linked client / unauthorized
            {'name': 'Item1'},  # duplicated item
            {'areas': 'not geojson'},  # duplicated item
            {'is_active': 'asdasd'},  # incorrect value
            {'max_rate': 'ddd'},  # incorrect value
            {'max_rate': '-10'},  # incorrect value
            {'max_daily_spend': '-10'},  # incorrect value
        ]
        for substitution in substitutions:
            image_file = open(path_to_image, 'rb')
            data = {
                'client': 'Client1',
                'name': 'Item5',
                'areas': '{"type": "MultiPolygon", "coordinates":[[[[37.60200012009591, 55.753318768941305], [37.60157692828216, 55.750842010116045], [37.60936881881207,55.74906941558997], [37.613412427017465, 55.75213456321547], [37.607292663306005, 55.75327778725062],[37.60314446990378, 55.75346674901331], [37.60200012009591, 55.753318768941305]]]]}',
                'is_active': 'true',
                'max_rate': 12,
                'max_daily_spend': 110.01,
                'image': [image_file, ],
            }
            if type(substitution) == dict:
                data.update(substitution)
            else:
                del data[substitution]
            resp = self.client.post(
                reverse('client_space:item'),
                data=data,
                HTTP_AUTHORIZATION=f'Bearer {token}'
            )
            image_file.close()

            self.assertEquals(resp.status_code, 400)

    def test_full_crud_item_ok(self):
        """ Full CRUD test:
        request POST a new Item,
        PUT with updates,
        DELETE the Item"""
        client = APIClient()
        token = self.get_token()
        path_to_image = os.path.join('client_space', 'tests', 'tested.png')
        image_file = open(path_to_image, 'rb')
        data = {
            'client': 'Client1',
            'name': 'Item8',
            'areas': '{"type": "MultiPolygon", "coordinates":[[[[37.60200012009591, 55.753318768941305], [37.60157692828216, 55.750842010116045], [37.60936881881207,55.74906941558997], [37.613412427017465, 55.75213456321547], [37.607292663306005, 55.75327778725062],[37.60314446990378, 55.75346674901331], [37.60200012009591, 55.753318768941305]]]]}',
            'is_active': 'true',
            'max_rate': 12,
            'max_daily_spend': 110.01,
            'image': [image_file, ],
        }
        resp = client.post(
            reverse('client_space:item'),
            data=data,
            HTTP_AUTHORIZATION=f'Bearer {token}'
        )
        image_file.close()

        self.assertEquals(resp.status_code, 201)
        new_item_id = resp.json()['data']['id']

        item = Item.objects.get(pk=new_item_id)
        self.assertEquals(item.name, data['name'])
        self.assertEquals(item.client.name, data['client'])
        self.assertEquals(item.max_rate, data['max_rate'])

        data['max_rate'] = 20
        with open(path_to_image, 'rb') as image_file:
            data['image'] = [image_file, ]
            resp = client.put(
                reverse('client_space:item', kwargs={'item_id': new_item_id}),
                data=data,
                format='multipart',
                HTTP_AUTHORIZATION=f'Bearer {token}'
            )

        self.assertEquals(resp.status_code, 200)
        item = Item.objects.get(pk=new_item_id)
        self.assertEquals(item.name, data['name'])
        self.assertEquals(item.client.name, data['client'])
        self.assertEquals(item.max_rate, data['max_rate'])

        resp = client.delete(
            reverse('client_space:item', kwargs={'item_id': new_item_id}),
            HTTP_AUTHORIZATION=f'Bearer {token}'
        )
        self.assertEquals(resp.status_code, 200)
        self.assertEquals(Item.objects.filter(pk=new_item_id).count(), 0)
