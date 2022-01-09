from django.contrib.auth.models import User
from django.contrib.gis.db import models as geomodels
from django.db import models
from django.utils.translation import gettext_lazy as _

from client_space.models import ItemFile


class VideoModule(models.Model):
    """Video modules installed on cars"""
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=64, verbose_name="Module name")
    phone = models.CharField(max_length=10, verbose_name="Phone number (10 digits)", null=True, blank=True)

    def __str__(self):
        return f'{self.name} ({self.phone})'

class Log(models.Model):
    """Video modules logs"""

    class Events(models.TextChoices):
        """Log events"""
        START = 'S', _('Start')
        SHOW = 'SH', _('Show')
        STOP = 'P', _('Stop')
        WARNING = 'WA', _('Warning')
        ERROR = 'ER', _('Error')

    module = models.ForeignKey(VideoModule, on_delete=models.RESTRICT)
    timestamp = models.DateTimeField()
    point = geomodels.PointField(verbose_name="Log geo location", )
    event = models.CharField(max_length=2, choices=Events.choices)
    item_file = models.ForeignKey(ItemFile, verbose_name="Shown Item File", on_delete=models.DO_NOTHING, blank=True, null=True, default=None)
    data = models.JSONField(verbose_name="Other log data", blank=True, null=True)

    class Meta:
        indexes = [
            models.Index(fields=['module'], name='module_idx'),
            models.Index(fields=['item_file'], name='item_file_idx'),
        ]

    def __str__(self):
        return f"{self.module.name} @ {self.timestamp}"
