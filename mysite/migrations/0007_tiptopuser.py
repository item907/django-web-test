# Generated by Django 3.0.7 on 2020-06-29 05:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mysite', '0006_bcoexrate'),
    ]

    operations = [
        migrations.CreateModel(
            name='TiptopUser',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('account', models.CharField(max_length=20)),
                ('password', models.CharField(max_length=20)),
                ('name', models.CharField(max_length=20)),
                ('c_date', models.DateField()),
            ],
        ),
    ]
