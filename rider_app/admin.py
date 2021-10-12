from django.contrib import admin

from rider_app.models import Rider,Bucket, Task, RiderRequest\

admin.site.register(Rider)

admin.site.register(Bucket)

admin.site.register(Task)

admin.site.register(RiderRequest)