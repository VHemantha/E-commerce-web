from django.contrib import admin

from auctions.models import Allbids, Allcat, Comments, CreateL, Watchlist



# Register your models here.
admin.site.register(CreateL)
admin.site.register(Allbids)
admin.site.register(Watchlist)
admin.site.register(Allcat)
admin.site.register(Comments)