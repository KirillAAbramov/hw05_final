# Generated by Django 2.2.6 on 2021-03-12 11:37

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0009_auto_20210312_1126'),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name='follow',
            name='unique_subscriber',
        ),
    ]
