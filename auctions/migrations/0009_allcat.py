# Generated by Django 4.1.1 on 2022-09-28 08:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0008_alter_comments_item_id_alter_comments_user_id_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='Allcat',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('category_name', models.CharField(max_length=256)),
            ],
        ),
    ]
