from django.contrib import admin

from .models import VideoModule


# Register your models here.
class VideoModuleAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'phone',)


admin.site.register(VideoModule, VideoModuleAdmin)
