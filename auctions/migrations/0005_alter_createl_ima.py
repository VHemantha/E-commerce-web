# Generated by Django 4.1.1 on 2022-09-24 05:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0004_alter_createl_ima'),
    ]

    operations = [
        migrations.AlterField(
            model_name='createl',
            name='ima',
            field=models.ImageField(blank=True, null=True, upload_to='images/'),
        ),
    ]
