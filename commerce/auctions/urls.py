from django.conf import settings
from django.conf.urls.static import static
from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("create", views.create_listing, name="create_listing"),
    path("listing/<int:listing_id>", views.view_listing, name="view_listing"),
    path("bid/<int:listing_id>", views.create_bid, name="create_bid"),
    path("comment/<int:listing_id>", views.create_comment, name="create_comment"),
    path("cancel/<int:listing_id>", views.cancel_listing, name="cancel_listing"),
    path("accept/<int:listing_id>", views.accept_bid, name="accept_bid"),
    path("categories", views.categories, name="categories"),
    path("category/<int:category_id>", views.view_category, name="view_category"),
    path("watch/<int:listing_id>", views.watch, name="watch"),
    path("watchlist/", views.view_watchlist, name="view_watchlist"),
    path("lsitings/", views.view_user_listings, name="view_user_listings"),
]

# Add URL for serving media files
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
