from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.views.decorators.http import require_POST

from .forms import CreateListingForm
from .models import Bid, Category, Comment, Listing, User


def login_view(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect(reverse("index"))

    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            messages.success(request, f"<strong>Welcome, { username }!</strong>")

            return HttpResponseRedirect(reverse("index"))
        else:
            return render(
                request,
                "auctions/login.html",
                {"message": "Invalid username and/or password."},
            )
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect(reverse("index"))

    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        if not username:
            return render(
                request,
                "auctions/login.html",
                {"message": "A username must be provided."},
            )

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(
                request, "auctions/register.html", {"message": "Passwords must match."}
            )

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)  # type: ignore
            user.save()
        except IntegrityError:
            return render(
                request,
                "auctions/register.html",
                {"message": "Username already taken."},
            )
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")


def index(request):
    listings = Listing.objects.filter(active=True)
    categories = Category.objects.order_by("name").all()

    return render(
        request,
        "auctions/index.html",
        {
            "title": "Current Listings",
            "listings": listings,
            "categories": categories,
            "default_image": settings.MEDIA_URL + "/images/default.jpg",
        },
    )


def categories(request):
    categories = Category.objects.order_by("name").all()

    return render(
        request,
        "auctions/categories.html",
        {
            "categories": categories,
            "current_category": None,
        },
    )


def view_category(request, category_id):
    listings = Listing.objects.filter(category__pk=category_id).filter(active=True)
    categories = Category.objects.order_by("name").all()

    # Retrieve correct category name
    category_name = categories.filter(pk=category_id).first()

    if not category_name:
        messages.error(
            request,
            "<strong>Error:</strong>  The provided category does not exist!",
        )

        return HttpResponseRedirect(reverse("categories"))

    return render(
        request,
        "auctions/categories.html",
        {
            "title": category_name,
            "listings": listings,
            "categories": categories,
            "current_category": category_id,
            "default_image": settings.MEDIA_URL + "/images/default.jpg",
        },
    )


def create_listing(request):
    if request.method == "POST":
        form = CreateListingForm(request.POST, request.FILES)

        if form.is_valid():
            new_listing = form.save(commit=False)
            new_listing.user = request.user
            new_listing.save()

            return HttpResponseRedirect(
                reverse("view_listing", kwargs={"listing_id": new_listing.pk})
            )

        else:
            return render(
                request,
                "auctions/create_listing.html",
                {"form": form},
            )
    else:
        form = CreateListingForm()

    return render(request, "auctions/create_listing.html", {"form": form})


def view_listing(request, listing_id):
    # Retrieve existing listing to ensure this is a valid listing to bid on
    try:
        listing = Listing.objects.get(pk=listing_id)
        high_bid = listing.bids.order_by("price").last()  # type: ignore
        watching = listing.watchers.filter(id=request.user.id).first()

    except Listing.DoesNotExist:
        messages.error(
            request,
            "<strong>Error:</strong>  The provided auction listing does not exist!",
        )
        return HttpResponseRedirect(reverse("index"))

    return render(
        request,
        "auctions/view_listing.html",
        {
            "listing": listing,
            "high_bid": high_bid,
            "watching": watching,
            "default_image": settings.MEDIA_URL + "/images/default.jpg",
        },
    )


@login_required  # type: ignore
@require_POST
def create_bid(request, listing_id):
    # Retrieve existing listing to endure this is a valid listing to bid on
    listing = Listing.objects.filter(pk=listing_id).exclude(active=False).first()

    if not listing:
        messages.error(
            request,
            "<strong>Error:</strong>  The provided auction listing does not exist or is no longer active!",
        )
        return HttpResponseRedirect(reverse("index"))

    if listing.user == request.user:
        messages.error(
            request,
            "<strong>Error:</strong>  You aren't able to bid on your own items.",
        )
        return HttpResponseRedirect(
            reverse("view_listing", kwargs={"listing_id": listing_id})
        )

    # Retrieve any existing high bid and ensure that new bid is higher if one does exist
    high_bid = Bid.objects.filter(listing__id=listing_id).order_by("price").last()
    bid_amount = int(request.POST["bid_amount"])

    if high_bid and bid_amount <= high_bid.price:
        messages.error(
            request,
            f"<strong>Error:</strong>  Your bid needs to be at least { high_bid.price + 1 }!",
        )
        return HttpResponseRedirect(
            reverse("view_listing", kwargs={"listing_id": listing_id})
        )

    # Create and save the new bid object
    # TODO Should we also auto-watch the item here?
    new_bid = Bid()
    new_bid.listing = listing
    new_bid.price = bid_amount
    new_bid.user = request.user
    new_bid.save()

    messages.success(
        request, "<strong>Congratulations!</strong>  You are the new high bidder!"
    )
    return HttpResponseRedirect(
        reverse("view_listing", kwargs={"listing_id": listing_id})
    )


@login_required  # type: ignore
@require_POST
def create_comment(request, listing_id):
    # Retrieve existing listing to endure this is a valid listing to comment on
    listing = Listing.objects.filter(pk=listing_id).exclude(active=False).first()

    if not listing:
        messages.error(
            request,
            "<strong>Error:</strong>  The provided auction listing does not exist or is no longer active!",
        )
        return HttpResponseRedirect(reverse("index"))

    comment = request.POST["comment"].strip()

    if not comment:
        messages.error(
            request,
            f"<strong>Error:</strong>  Your comment needs to have some content!",
        )
        return HttpResponseRedirect(
            reverse("view_listing", kwargs={"listing_id": listing_id})
        )

    new_comment = Comment()
    new_comment.listing = listing
    new_comment.text = comment
    new_comment.user = request.user
    new_comment.save()

    messages.success(request, "Your message has been posted.")
    return HttpResponseRedirect(
        reverse("view_listing", kwargs={"listing_id": listing_id})
    )


@login_required  # type: ignore
def cancel_listing(request, listing_id):
    # Retrieve existing listing to endure this is a valid listing to comment on
    listing = Listing.objects.filter(pk=listing_id).exclude(active=False).first()

    errors = False

    if not listing:
        messages.error(
            request,
            "<strong>Error:</strong>  The provided auction listing does not exist or is no longer active!",
        )

        errors = True
        return HttpResponseRedirect(reverse("index"))

    if not listing.user == request.user:
        messages.error(
            request,
            "<strong>Error:</strong>  You are not able to cancel listings which you do not own.",
        )

        errors = True

    bid_count = listing.bids.count()  # type: ignore

    if bid_count:
        messages.error(
            request,
            "<strong>Error:</strong>  You are not able to cancel a listing with bids.",
        )

        errors = True

    if not errors:
        listing.active = False
        listing.save()

        messages.success(request, "Your listing has been cancelled.")

    return HttpResponseRedirect(
        reverse("view_listing", kwargs={"listing_id": listing_id})
    )


@login_required  # type: ignore
def accept_bid(request, listing_id):
    # Retrieve existing listing to endure this is a valid listing to comment on
    listing = Listing.objects.filter(pk=listing_id).exclude(active=False).first()

    errors = False

    if not listing:
        messages.error(
            request,
            "<strong>Error:</strong>  The provided auction listing does not exist or is no longer active!",
        )
        return HttpResponseRedirect(reverse("index"))

    if not listing.user == request.user:
        messages.error(
            request,
            "<strong>Error:</strong>  You are not able to cancel listings which you do not own.",
        )

        errors = True

    # Retrieve any existing high bid to ensure one exists and it is higher than the listing price
    high_bid = Bid.objects.filter(listing__id=listing_id).order_by("price").last()

    if not high_bid or high_bid.price <= listing.price:
        messages.error(
            request,
            "<strong>Error:</strong>  There must be bids on this listing and those bids must exceed the lsiting price.",
        )

        errors = True

    if not errors:
        listing.active = False
        listing.completed = True
        listing.save()

        messages.success(
            request, "<strong>Congratulations!</strong>  You have accepted an offer!"
        )

    return HttpResponseRedirect(
        reverse("view_listing", kwargs={"listing_id": listing_id})
    )


@login_required  # type: ignore
def watch(request, listing_id):
    # Retrieve existing listing to endure this is a valid listing to comment on
    listing = Listing.objects.filter(pk=listing_id).first()

    if not listing:
        messages.error(
            request,
            "<strong>Error:</strong>  The provided auction listing does not exist or is no longer active!",
        )
        return HttpResponseRedirect(reverse("index"))

    # Get watch status
    watching = listing.watchers.filter(id=request.user.id).first()

    if not watching:
        listing.watchers.add(request.user)

        messages.success(request, "You are now watching this item.")
    else:
        listing.watchers.remove(request.user)

        messages.success(request, "You are no longer watching this item.")

    listing.save()

    return HttpResponseRedirect(
        reverse("view_listing", kwargs={"listing_id": listing_id})
    )


@login_required  # type: ignore
def view_watchlist(request):
    # Create a list of listings watched by the current user
    watched_listings = request.user.watching.all()
    categories = Category.objects.order_by("name").all()

    return render(
        request,
        "auctions/view_cards.html",
        {
            "title": "Watched Listings",
            "listings": watched_listings,
            "categories": categories,
            "default_image": settings.MEDIA_URL + "/images/default.jpg",
        },
    )


@login_required  # type: ignore
def view_user_listings(request):
    # Collect a list of all listings created by the current user
    listings = Listing.objects.filter(user=request.user)
    categories = Category.objects.order_by("name").all()

    return render(
        request,
        "auctions/view_cards.html",
        {
            "title": "Your Listings",
            "listings": listings,
            "categories": categories,
            "default_image": settings.MEDIA_URL + "/images/default.jpg",
        },
    )
