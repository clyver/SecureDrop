# Generated by Django 2.1.7 on 2019-03-06 05:21

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('dropper', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='drop',
            name='uuid',
            field=models.UUIDField(default=uuid.uuid4),
        ),
    ]
