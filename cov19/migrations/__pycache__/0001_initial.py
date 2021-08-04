# Generated by Django 3.2.4 on 2021-06-22 08:59

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='details',
            fields=[
                ('id', models.IntegerField(primary_key=True, serialize=False)),
                ('update_time', models.DateTimeField(max_length=32)),
                ('province_name', models.CharField(max_length=50)),
                ('city_name', models.CharField(max_length=50)),
                ('confirm', models.IntegerField()),
                ('confirm_add', models.IntegerField()),
                ('heal', models.IntegerField()),
                ('dead', models.IntegerField()),
            ],
        ),
    ]