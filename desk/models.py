import base64
from django.db import models

from django.conf import settings

class session(models.Model):
    author = models.ForeignKey(settings.AUTH_USER_MODEL)
    title = models.CharField(max_length=300)
    pub_date = models.DateTimeField('date published')
    end_date = models.DateTimeField(null=True, blank=True)
    def __str__(self):
        return self.title
    def was_published_recently(self):
        return self.pub_date >= timezone.now() - datetime.timedelta(days=1)
    

class session_object(models.Model):
    session = models.ForeignKey(session, on_delete=models.CASCADE)
    author = models.ForeignKey(settings.AUTH_USER_MODEL)
    date_added = models.DateTimeField('date added')
    data_type = models.CharField(max_length=200)
    _data = models.TextField(
            db_column='data',
            blank=True)
    def set_data(self, data):
        self._data = base64.encodestring(data)
    def get_data(self):
        return base64.decodestring(self._data)
        
    binary_data = property(get_data, set_data)

class session_object_movement(models.Model):
    session_object = models.ForeignKey(session_object, on_delete=models.CASCADE)
    movement_type = models.CharField(max_length=30)
    movement_time = models.DateTimeField('movement_time')
    _data = models.TextField(
            db_column='data',
            blank=True)
    def set_data(self, data):
        self._data = base64.encodestring(data)
    def get_data(self):
        return base64.decodestring(self._data)

    binary_data = property(get_data, set_data)

class session_message(models.Model):
    author = models.ForeignKey(settings.AUTH_USER_MODEL)
    session = models.ForeignKey(session, on_delete=models.CASCADE)
    text = models.CharField(max_length=300)