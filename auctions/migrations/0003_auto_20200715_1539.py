# Generated by Django 3.0.7 on 2020-07-15 19:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0002_auto_20200714_1009'),
    ]

    operations = [
        migrations.AlterField(
            model_name='watchlist',
            name='listings',
            field=models.ManyToManyField(null=True, related_name='watch_ls', to='auctions.Auction_Listing'),
        ),
    ]
