import json

from dateutil import parser as dateparser
from django.contrib.auth.models import User
from django.contrib.gis.geos import GEOSGeometry
from django.test import TestCase
from django.urls import reverse

from client_space.models import Client, ClientUser, Item, ItemFile
from logger.models import VideoModule, Log

test_user = {"username": "svcModule1", "email": "module1@example.com", "password": "testpassword"}

test_client = [{"name": "Client1"}, {"name": "Client2"}]
test_areas = {
    "type": "MultiPolygon",
    "coordinates": [
        [
            [
                [
                    37.632980346679695,
                    55.772904096077305
                ],
                [
                    37.64739990234376,
                    55.7700073342752
                ],
                [
                    37.65254974365235,
                    55.76826917386254
                ],
                [
                    37.6552963256836,
                    55.76672407732225
                ],
                [
                    37.66147613525391,
                    55.755133901266255
                ],
                [
                    37.6607894897461,
                    55.74817814201809
                ],
                [
                    37.65838623046876,
                    55.743347023896575
                ],
                [
                    37.653923034667976,
                    55.73890186689086
                ],
                [
                    37.64465332031251,
                    55.73310307504565
                ],
                [
                    37.63538360595704,
                    55.73058999769508
                ],
                [
                    37.62954711914063,
                    55.72981671057788
                ],
                [
                    37.61066436767579,
                    55.73058999769508
                ],
                [
                    37.60482788085938,
                    55.73155658505244
                ],
                [
                    37.58869171142579,
                    55.735615990618776
                ],
                [
                    37.58182525634766,
                    55.73948169869349
                ],
                [
                    37.57907867431641,
                    55.745279542927584
                ],
                [
                    37.57873535156251,
                    55.75397469418902
                ],
                [
                    37.586288452148445,
                    55.76614465033217
                ],
                [
                    37.596244812011726,
                    55.77386963550732
                ],
                [
                    37.632980346679695,
                    55.772904096077305
                ]
            ]
        ]
    ]
}
test_items = [
    {"client": "Client1", "name": "Item1", "areas": test_areas, "images": ['img/img1.png', ]},
    {"client": "Client1", "name": "Item2", "areas": test_areas, "images": ['img/img2.png', ]},
    {"client": "Client1", "name": "Item3", "areas": test_areas, "images": ['img/img3.png', ]},
]

test_videomodule = {"user": test_user['username'], "name": "Module1", "phone": "9051111111"}
test_track = [
    {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "properties": {
                    "event": "S",
                    "item_file": "",
                    "data": "{\"msg\": \"Downloaded 14 images\"}",
                    "timestamp": "2022-01-08T18:34:36+0300"
                },
                "geometry": {
                    "type": "Point",
                    "coordinates": [
                        37.53892600536346,
                        55.7412453008087
                    ]
                }
            }
        ]
    },  # start
    {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "properties": {
                    "event": "SH",
                    "item_file": "img/img1.png",
                    "data": None,
                    "timestamp": "2022-01-08T18:35:12+0300"
                },
                "geometry": {
                    "type": "Point",
                    "coordinates": [
                        37.52500534057617,
                        55.73783881954505
                    ]
                }
            }
        ]
    },  # point 1
    {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "properties": {
                    "event": "SH",
                    "item_file": "img/img1.png",
                    "data": None,
                    "timestamp": "2022-01-08T18:35:18+0300"
                },
                "geometry": {
                    "type": "Point",
                    "coordinates": [
                        37.52678096294403,
                        55.73822387555036
                    ]
                }
            }
        ]
    },  # point 2
    {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "properties": {
                    "event": "SH",
                    "item_file": "img/img1.png",
                    "data": None,
                    "timestamp": "2022-01-08T18:35:23+0300"
                },
                "geometry": {
                    "type": "Point",
                    "coordinates": [
                        37.53026247024536,
                        55.73885354718511
                    ]
                }
            }
        ]
    },  # point 3
    {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "properties": {
                    "event": "SH",
                    "item_file": "img/img2.png",
                    "data": None,
                    "timestamp": "2022-01-08T18:35:28+0300"
                },
                "geometry": {
                    "type": "Point",
                    "coordinates": [
                        37.53649592399597,
                        55.74026083411281
                    ]
                }
            }
        ]
    },  # point 4
    {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "properties": {
                    "event": "SH",
                    "item_file": "img/img2.png",
                    "data": None,
                    "timestamp": "2022-01-08T18:35:32+0300"
                },
                "geometry": {
                    "type": "Point",
                    "coordinates": [
                        37.53892600536346,
                        55.7412453008087
                    ]
                }
            }
        ]
    },  # point 5
    {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "properties": {
                    "event": "SH",
                    "item_file": "img/img3.png",
                    "data": None,
                    "timestamp": "2022-01-08T18:35:36+0300"
                },
                "geometry": {
                    "type": "Point",
                    "coordinates": [
                        37.53892600536346,
                        55.7412453008087
                    ]
                }
            }
        ]
    },  # point 6
    {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "properties": {
                    "event": "SH",
                    "item_file": "img/img3.png",
                    "data": None,
                    "timestamp": "2022-01-08T18:36:36+0300"
                },
                "geometry": {
                    "type": "Point",
                    "coordinates": [
                        37.55023956298828,
                        55.745376166366704
                    ]
                }
            }
        ]
    },  # point 7
    {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "properties": {
                    "event": "ER",
                    "item_file": "",
                    "data": "{\"msg\": \"Wrong coordinates\"}",
                    "timestamp": "2022-01-08T18:38:36+0300"
                },
                "geometry": {
                    "type": "Point",
                    "coordinates": [
                        37.53892600536346,
                        55.7412453008087
                    ]
                }
            }
        ]
    },  # error
]


class ClientTests(TestCase):
    def setUp(self):
        """Set up databse"""
        User.objects.create(username="User", email="user@example.com")
        new_user = User.objects.create(username=test_user["username"], email=test_user["email"])
        new_user.set_password(test_user["password"])
        new_user.save()

        VideoModule.objects.create(user=new_user, name=test_videomodule['name'], phone=test_videomodule['phone'])

        for client in test_client:
            Client.objects.create(name=client['name'])
        cl1 = Client.objects.get(name='Client1')
        clu, _ = ClientUser.objects.get_or_create(user=new_user)
        clu.client.add(cl1)
        clu.save()

        for test_item in test_items:
            client = Client.objects.get(name=test_item['client'])
            name = test_item['name']
            areas = GEOSGeometry(json.dumps(test_item['areas']))
            images = test_item['images']
            item = Item(client=client, name=name, areas=areas)
            item.save()
            for image in images:
                itemfile = ItemFile(item=item, image=image)
                itemfile.save()

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

    def test_insert_event_ok(self):
        """Test that events can be inserted"""
        token = self.get_token()

        for test_log in test_track:
            res = self.client.post(reverse('logger:incoming'),
                                   data=test_log,
                                   content_type='application/json',
                                   HTTP_AUTHORIZATION=f'Bearer {token}'
                                   )

            self.assertIn(res.status_code, (200, 201))

            log = Log.objects.order_by('pk').last()
            props = test_log['features'][0]['properties']
            geom = GEOSGeometry(json.dumps(test_log['features'][0]['geometry']))
            self.assertEquals(log.event, props['event'])
            self.assertEquals(log.data, json.loads(props['data']) if props['data'] else None)
            self.assertEquals(log.item_file, ItemFile.objects.get(image=props['item_file']) if props['item_file'] else None)
            self.assertEquals(log.timestamp, dateparser.parse(props['timestamp']))
            self.assertEquals(log.point, geom)
