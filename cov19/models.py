from django.db import models


# Create your models here.

# python manage.py makemigrations
# python manage.py migrate

class details(models.Model):
    # 创建表的字段
    id = models.IntegerField(primary_key=True)  # 创建一个字段，类型为字符串类型，最大长度为16
    update_time = models.DateTimeField(max_length=32)  # 创建一个字段，类型为字符串类型，最大长度为32
    province_name = models.CharField(max_length=50)
    city_name = models.CharField(max_length=50)
    confirm = models.IntegerField()
    confirm_add = models.IntegerField()
    heal = models.IntegerField()
    dead = models.IntegerField()