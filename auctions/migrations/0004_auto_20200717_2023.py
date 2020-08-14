# Generated by Django 3.0.7 on 2020-07-18 00:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0003_auto_20200715_1539'),
    ]

    operations = [
        migrations.AlterField(
            model_name='auction_listing',
            name='start_time',
            field=models.DateTimeField(auto_now_add=True),
        ),
        migrations.AlterField(
            model_name='watchlist',
            name='listings',
            field=models.ManyToManyField(related_name='watch_ls', to='auctions.Auction_Listing'),
        ),
    ]