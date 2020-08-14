from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.shortcuts import render
from django.urls import reverse

from .models import *

from django.utils import timezone


def index(request):
    listings = Auction_Listing.objects.all()
    return render(request, "auctions/index.html", {'listings': listings})


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")


@login_required(redirect_field_name='create', login_url='/login')
def get_listing(request):
    # POST request
    if request.method == "POST":
        # Create form with request data
        form = Form(request.POST)

        # If form is valid
        if form.is_valid():
            l = form.save(commit=False)
            l.user = request.user
            l.bid = None
            l.save()

            return HttpResponseRedirect('/')
    
    # GET or other methods
    else:
        form = Form(initial={'user': request.user, 'bid': None})
    return render(request, 'auctions/create.html', {'form': form})


def listing(request, listing_id):
    # GET request
    if request.method == "GET":
        listing = Auction_Listing.objects.get(id=listing_id)
        now = timezone.now()
        if listing.end_time < now:
            try:
                listing.winner = listing.bid.user
                listing.save()
            except AttributeError:
                n = User.objects.get(username='None')
                listing.winner = n 
                listing.save()
        
        listing = Auction_Listing.objects.get(id=listing_id)
        comments = listing.comments.all()
        new_bid = New_Bid(initial={'user': request.user})
        new_comment = New_Comment(initial={'user': request.user})
        return render(request, 'auctions/listing.html', {'listing': listing, 'comments': comments, 'new_bid': new_bid, 'new_comment': new_comment})

    # POST request/new bid or comment/watchlist changes
    if request.method == "POST":
        if 'new_bid' in request.POST:
            form = New_Bid(request.POST)
        if 'new_comment' in request.POST:
            form = New_Comment(request.POST)

        listing = Auction_Listing.objects.get(id=listing_id)
        if 'close' in request.POST:
            if listing.bid is None:
                u = User.objects.get(username='None')
                listing.winner = u
            else: 
                listing.winner = listing.bid.user
            listing.save()
            listing = Auction_Listing.objects.get(id=listing_id)
            comments = listing.comments.all()
            new_bid = New_Bid(initial={'user': request.user})
            new_comment = New_Comment(initial={'user': request.user})
            return render(request, 'auctions/listing.html', {'listing': listing, 'comments': comments, 'new_bid': new_bid, 'new_comment': new_comment})

        if 'watch' in request.POST:
            try:
                Watchlist.objects.get(user=request.user)
            except Watchlist.DoesNotExist:
                a = Watchlist(user=request.user)
                a.save()
            try: 
                w = Watchlist.objects.filter(user=request.user).get(listings=listing_id)
            except Watchlist.DoesNotExist:
                a = Watchlist.objects.get(user=request.user)
                a.listings.add(listing)
                a.save()
                ls = Watchlist.objects.filter(user=request.user).values_list('listings', flat=True)
                listings = Auction_Listing.objects.filter(id__in=ls)
                return render(request, 'auctions/watchlist.html', {'listings': listings})
    
            w.listings.remove(listing)
            ls = Watchlist.objects.filter(user=request.user).values_list('listings', flat=True)
            listings = Auction_Listing.objects.filter(id__in=ls)
            return render(request, 'auctions/watchlist.html', {'listings': listings})

        if form.is_valid():
            if 'new_bid' in request.POST:
                if listing.bid is None:
                    sb = listing.starting_bid
                    if form.cleaned_data['bid'] < sb:
                        raise Http404("Invalid: bid must be greater than or equal to starting bid")
                else:
                    cb = listing.bid.bid
                    if form.cleaned_data['bid'] <= cb:
                        raise Http404("Invalid: bid must be greater than current bid")
                b = Bid(user=request.user, bid=form.cleaned_data['bid'])
                b.save()
                listing.bid = b
                listing.save()
            if 'new_comment' in request.POST:
                c = Comment(user=request.user, description=form.cleaned_data['description'])
                c.save()
                listing.comments.create(user=request.user, description=form.cleaned_data['description'])
            comments = listing.comments.all()
            new_bid = New_Bid(initial={'user': request.user})
            new_comment = New_Comment(initial={'user': request.user})
            return render(request, 'auctions/listing.html', {'listing': listing, 'comments': comments, 'new_bid': new_bid, 'new_comment': new_comment})

        if listing is not None:
            comments = listing.comments.all()
            new_bid = New_Bid(initial={'user': request.user})
            new_comment = New_Comment(initial={'user': request.user})
            return render(request, 'auctions/listing.html', {'listing': listing, 'comments': comments, 'new_bid': new_bid, 'new_comment': new_comment})
        else:
            raise Http404("No such listing")


def categories(request):
    all_categories = list(Auction_Listing.objects.values_list('category', flat=True).distinct())
    return render(request, "auctions/categories.html", {'categories': all_categories})


def category(request, c):
    # GET request
    if request.method == "GET":
        category = Auction_Listing.objects.filter(category=c)
        if category is None: 
            return Http404('No such category')
        listings = Auction_Listing.objects.filter(category=c)
        return render(request, 'auctions/category.html', {'category': c, 'listings': listings})


def watchlist(request):
    # GET request/view all watchlists
    if request.method == "GET":
        ls = Watchlist.objects.filter(user=request.user).values_list('listings', flat=True)
        listings = Auction_Listing.objects.filter(id__in=ls)
        return render(request, 'auctions/watchlist.html', {'listings': listings})