# Generated by Django 3.0.7 on 2021-05-17 04:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mysite', '0008_health'),
    ]

    operations = [
        migrations.AddField(
            model_name='health',
            name='phone',
            field=models.CharField(default=123456789, max_length=20),
            preserve_default=False,
        ),
    ]
