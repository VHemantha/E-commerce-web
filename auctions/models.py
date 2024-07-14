
from django.contrib.auth.models import AbstractUser
from django.db import models



class User(AbstractUser):
    pass


class CreateL(models.Model):
    title = models.CharField(max_length=128)
    description = models.CharField(max_length=512)
    category = models.CharField(max_length=128)
    bid = models.IntegerField()
    user_l = models.ForeignKey(User, on_delete=models.CASCADE)
    ima = models.ImageField(null=True, blank=True, upload_to='images/')
    status = models.CharField(max_length=64, default="active")

    
class Allbids(models.Model):
    current_bid = models.IntegerField()
    listing_id =  models.ForeignKey(CreateL, on_delete=models.CASCADE, name="bids")
    user_b = models.ForeignKey(User, on_delete=models.CASCADE)


class Watchlist(models.Model):
    list_id =  models.ForeignKey(CreateL, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)


class Comments(models.Model):
    comment = models.CharField(max_length=256)
    item_id = models.ForeignKey(CreateL, on_delete=models.CASCADE)
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)

class Allcat(models.Model):
    category_name = models.CharField(max_length=256)