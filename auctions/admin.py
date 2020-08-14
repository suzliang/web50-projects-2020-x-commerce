from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import *

class Auction_ListingAdmin(admin.ModelAdmin):
    filter_horizontal = ("comments",)

class WatchlistAdmin(admin.ModelAdmin):
    filter_horizontal = ("listings",)

admin.site.register(User, UserAdmin)
admin.site.register(Auction_Listing, Auction_ListingAdmin)
admin.site.register(Bid)
admin.site.register(Comment)
admin.site.register(Watchlist, WatchlistAdmin)