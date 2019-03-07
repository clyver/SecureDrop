# Generated by Django 2.1.7 on 2019-03-06 05:16

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Drop',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('uuid', models.UUIDField()),
                ('text', models.TextField()),
                ('created_on', models.DateTimeField(auto_now_add=True)),
                ('last_retrieved_on', models.DateTimeField(blank=True, null=True)),
                ('updated_on', models.DateTimeField(auto_now=True)),
            ],
        ),
    ]
