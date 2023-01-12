# Auctions!
## CS50w Project 2 - Commerce

This is a small project build for [Harvard's CS50 Web Programming course](https://cs50.harvard.edu/web/2020/) hosted by [edX](https://www.edx.org/).  The requirement was to:

>Design an eBay-like e-commerce auction site that will allow users to post auction listings, place bids on listings, comment on those listings, and add listings to a “watchlist.”

This was to be done primarily using [Django](https://www.djangoproject.com/) and [Bootstrap](https://getbootstrap.com/).

## Screenshots

### Authentication

The site uses standard Django auth to control access to features such as creating and bidding on listings, managing your watchlist, and interacting with other users through listing comments.

![Auth](Images/Auth.png?raw=true)

### Active Listings

The landing page will present users, authenticated or not, with the current active listings.

![Active Listings](Images/ActiveListings.png?raw=true)

### Listing Page

Details for individual listings, as well as functionality mentioned earlier and listing owner control to awarding or cancel a listing, are available on the listing page.

![Listing Page](Images/ListingView.png?raw=true)

### Categories

Each listing can be assigned a category which is displayed on the Current Listing page cards as well as can be used to filter listings.

![Categories](Images/Categories.png?raw=true)





