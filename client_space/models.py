import os
from hashlib import md5

from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.gis.db import models as geomodel
from django.db import models
from django.dispatch import receiver


def get_srid(lat: float = None, lon: float = None) -> int:
    """This function should return the best UTM zone for a pair of coordinates
    :param lat: latitude of a point inside the zone
    :paran lon: longitude of a point indside the zone
    :return: SRID = spatial reference id"""
    return settings.DEFAULT_SRID


class Client(models.Model):
    """Client objects - company, department.
    One client has many images and videos.
    Many users can access one client"""
    name = models.CharField(max_length=200, unique=True)

    def __str__(self):
        return self.name


class ClientUser(models.Model):
    """
    Model to grant access to specified Clients to a User
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    client = models.ManyToManyField(Client)

    def __str__(self):
        return self.user.get_full_name()


def client_directory_path(instance, filename) -> str:
    """
    Create path to store an image file for Item models
    :param instance: Item instance
    :param filename:
    :return: path to store the image
    """
    return os.path.join('images', str(instance.item.client.name), str(instance.item.name), filename)


class Item(models.Model):
    """Item object contains one campaign input information like client, name, areas etc."""
    client = models.ForeignKey(Client, on_delete=models.RESTRICT)
    name = models.CharField(max_length=200)

    areas = geomodel.MultiPolygonField(verbose_name='Areas to show')
    is_active = models.BooleanField(verbose_name='Item is active', default=False)
    max_rate = models.DecimalField(verbose_name='Maximum Show Rate', max_digits=8, decimal_places=2, default=10)
    max_daily_spend = models.DecimalField(verbose_name='Maximum Daily Spends', max_digits=11, decimal_places=2, default=100)

    class Meta:
        unique_together = [['client', 'name'], ]
        index_together = [['client', 'name'], ]

    def __str__(self):
        return self.name

    def total_area(self) -> str:
        """Calculates total area of all polygons for the item"""
        area = self.areas.transform(
            ct=get_srid(
                lon=(self.areas.extent[0] + self.areas.extent[2]) / 2,
                lat=(self.areas.extent[1] + self.areas.extent[3]) / 2,
            ),
            clone=True).area / 1_000_000
        return f'{round(area, 2)} sq km'


class ItemFile(models.Model):
    """Item files"""
    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name='items')
    image = models.FileField(verbose_name='image', upload_to=client_directory_path, )
    md5 = models.CharField(verbose_name='image md5', max_length=32, default='')

    class Meta:
        unique_together = [['item', 'md5'], ]
        index_together = [['item', 'md5'], ]

    def __str__(self):
        return self.image.name

    def get_md5(self):
        """Get MD5 of the file"""
        result = md5(self.image.read()).hexdigest()
        self.image.seek(0)
        return result


@receiver(models.signals.pre_delete, sender=ItemFile)
def pre_delete_image(sender, instance, *args, **kwargs):
    """ Clean Old Image file """
    try:
        instance.image.delete(save=False)
    except Exception:
        pass


@receiver(models.signals.pre_save, sender=ItemFile)
def pre_save_image(sender, instance, *args, **kwargs):
    """ Clean Old Image file """
    try:
        instance.md5 = instance.get_md5()
    except Exception:
        pass
