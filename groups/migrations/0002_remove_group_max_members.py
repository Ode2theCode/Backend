# Generated by Django 5.1.2 on 2024-11-26 08:37

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('groups', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='group',
            name='max_members',
        ),
    ]
