from django.contrib.auth.models import AbstractUser
from django.db import models
from django.forms import ModelForm
from django.utils.translation import gettext_lazy as _


class User(AbstractUser):
    pass

    def __str__(self):
        return self.username

class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    description = models.CharField(max_length=500)

    def __str__(self):
        return f"{self.user}: {self.description}"

class Bid(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    bid = models.DecimalField(max_digits=10, decimal_places=2)
    time = models.TimeField(auto_now=True)

    def __str__(self):
        return f"user:{self.user} bid:{self.bid} time:{self.time}"

class Auction_Listing(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    category = models.CharField(default="No Category Listed", max_length=50)
    start_time = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField()
    title = models.CharField(max_length=100)
    image = models.URLField(blank=True, null=True)
    description = models.CharField(max_length=500)
    starting_bid = models.DecimalField(max_digits=10, decimal_places=2)
    bid = models.ForeignKey(Bid, blank=True, null=True, on_delete=models.CASCADE)
    comments = models.ManyToManyField(Comment, blank=True)
    winner = models.ForeignKey(User, blank=True, null=True, on_delete=models.CASCADE, related_name="win")

    def __str__(self):
        return f"user:{self.user} category:{self.category} start:{self.start_time} end:{self.end_time} title:{self.title} img:{self.image} description:{self.description} starting bid:{self.starting_bid} bid:{self.bid} winner:{self.winner}"


class Form(ModelForm):
    class Meta:
        model = Auction_Listing
        exclude = ['user', 'bid', 'comments', 'winner']
        labels = {
            'image': _('Image URL'),
            'starting_bid': _('Starting bid'),
        }
        help_texts = {
            'category': _('Max 50 characters'),
            'end_time': _('yyyy-mm-dd hh:mm:ss:ff'),
            'description': _('Max 500 characters'),
        }

class New_Bid(ModelForm):
    class Meta:
        model = Bid
        exclude = ['user', 'time']
        labels = {
            'bid': _('Bid'),
        }
        help_texts = {
            'bid': _('Please input bid $___.$$ greater than current bid')
        }

class New_Comment(ModelForm):
    class Meta:
        model = Comment
        exclude = ['user']
        labels = {
            'description': _('Comment'),
        }
        help_texts = {
            'description': _('Max 500 characters')
        }

class Watchlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    listings = models.ManyToManyField(Auction_Listing, related_name="watch_ls")