from django.contrib import admin

from .models import Bid, Category, Comment, Listing, User

# Register your models here.
class WatcherInline(admin.TabularInline):
    model = Listing.watchers.through


class UserAdmin(admin.ModelAdmin):
    inlines = [
        WatcherInline,
    ]


admin.site.register(User, UserAdmin)


class ListingAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "description",
        "image",
        "price",
        "user",
        "active",
        "completed",
        "created_at",
        "updated_at",
    )
    inlines = [
        WatcherInline,
    ]
    exclude = ("watchers",)


admin.site.register(Listing, ListingAdmin)


class BidAdmin(admin.ModelAdmin):
    list_display = ("listing", "price", "user", "created_at")


admin.site.register(Bid, BidAdmin)


class CommentAdmin(admin.ModelAdmin):
    list_display = ("listing", "text", "user", "created_at")


admin.site.register(Comment, CommentAdmin)


class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "icon", "description", "hex_color_code")


admin.site.register(Category, CategoryAdmin)
