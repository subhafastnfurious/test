# Generated by Django 2.0.5 on 2018-07-01 11:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='officespace',
            name='public',
            field=models.BooleanField(default=True),
        ),
    ]
