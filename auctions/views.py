from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.db.models import Max
from django.contrib.auth.decorators import login_required

from .models import User, CreateL, Allbids, Watchlist, Comments, Allcat


def index(request):
    if request.method == "POST":
        bid = Allbids.objects.values("bids__id","user_b").annotate(Max("current_bid")).order_by("bids_id","-current_bid__max")
        print(bid)
        bid = create_max(bid)
        print(bid)
        List = CreateL.objects.all().values()
        users = User.objects.all().values()
        bid = winner(bid,users)
        boo = make_list(List,bid)
        return render(request, "auctions/index.html",{
        "list":boo,
        })
    
    bid = Allbids.objects.values("bids__id","user_b").annotate(Max("current_bid")).order_by("bids_id","-current_bid__max")
    if len(bid) == 0:
        return render(request, "auctions/index.html",{
    })
    bid = create_max(bid)
    List = CreateL.objects.all().values()
    users = User.objects.all().values()
    bid = winner(bid,users)
    boo = make_list(List,bid)
    return render(request, "auctions/index.html",{
        "list":boo,
    })


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


def create_listing(request):
    if request.method == 'POST':
        title = request.POST["title"]
        description = request.POST["description"]
        category = request.POST["category"]
        bid = int(request.POST["bid"])
        image=request.FILES["image"]
        user = User.objects.get(id = request.user.id)
        foo = CreateL(title = title, description=description, category=category,
        bid = bid, user_l=user, ima=image)
        foo.save()
        boo = Allbids(current_bid = bid, bids_id = foo.id, user_b=user)
        boo.save()
        baz = Allcat.objects.all().values()
        return HttpResponseRedirect(reverse("index"))
    baz = Allcat.objects.all().values()
    return render(request, "auctions/create.html",{
        "data":baz
    })

@login_required
def listing(request,id):
    if request.method == "POST":
        if 'close' in request.POST:
            doo = CreateL.objects.get(id=id)
            doo.status = "closed"
            doo.save()
            
        elif 'cmt' in request.POST:
            comment = request.POST["comment"]
            user = User.objects.get(id=request.user.id)
            listing = CreateL.objects.get(id=id)
            foo = Comments(comment=comment,item_id=listing,user_id=user)
            foo.save()
        else:
            my_bid = int(request.POST["bid"])
            boo = Allbids.objects.filter(bids_id=id).aggregate(Max('current_bid'))
            listing = CreateL.objects.get(id=id)
            user = User.objects.get(id = request.user.id)
            if len(boo) == 0:
                max_bid = 0
            else:
                max_bid = boo["current_bid__max"]
                if max_bid == None:
                    max_bid = 0
                    if int(max_bid) < int(my_bid) and max_bid != None:
                        foo = Allbids(bids_id=id, current_bid = my_bid, user_b=user)
                        foo.save()
            if my_bid > max_bid:
                foo = Allbids(bids_id=id, current_bid = my_bid, user_b=user)
                foo.save()
            else:
                return render (request, "auctions/invalidbid.html")

    bid = Allbids.objects.values("bids__id","user_b").annotate(Max("current_bid")).order_by("bids_id","-current_bid__max")
    bid = create_max(bid)
    listing = CreateL.objects.filter(id=id).values()
    users = User.objects.all().values()
    bid = winner(bid,users) 
    boo = make_list(listing,bid)
    user = User.objects.get(id = request.user.id)
    booz = Watchlist.objects.prefetch_related('list_id').filter(user=user).all().values()
    if len(booz) == 0:
        baz=boo
    else:
        baz = add_msg(boo,booz)
    comments = Comments.objects.filter(item_id = id, user_id = user).values()
    return render(request, "auctions/listing.html",{
        "listing":baz,
        "cmt":comments,
    })

@login_required
def watch_list(request):
    if request.method == "POST" and "remove" in request.POST:
        id = int(request.POST["id"])
        user = User.objects.get(id = request.user.id)
        foo = Watchlist.objects.get(list_id=id)
        foo.delete()
        bid = Allbids.objects.values("bids__id","user_b").annotate(Max("current_bid")).order_by("bids_id","-current_bid__max")
        bid = create_max(bid)
        listing = CreateL.objects.filter(id=id).values()
        users = User.objects.all().values()
        bid = winner(bid,users)
        boo = make_list(listing,bid)
        user = User.objects.get(id = request.user.id)    
        booz = Watchlist.objects.prefetch_related('list_id').filter(user=user).all().values()
        if len(booz) == 0:
            baz=None
        else:
            baz = add_msg(boo,booz)
        return render(request, "auctions/watchlist.html",{
            "List":baz
        })
    elif request.method == "POST" and "add" in request.POST:
        w_id =CreateL.objects.get(id=request.POST["id"]) 
        user = User.objects.get(id=request.user.id)
        foo = Watchlist(list_id = w_id, user = user)
        foo.save()

    #create queries to get Watchlist details for user
    bid = Allbids.objects.values("bids__id","user_b").annotate(Max("current_bid")).order_by("bids_id","-current_bid__max")
    bid = create_max(bid)
    listing = CreateL.objects.all().values()  
    users = User.objects.all().values()
    bid = winner(bid,users) 
    boo = make_list(listing,bid)
    user = User.objects.get(id = request.user.id)    
    booz = Watchlist.objects.prefetch_related('list_id').filter(user=user).all().values()

    if len(booz) == 0:
        baz=None
    else:
        baz = add_msg(boo,booz)
    return render(request, "auctions/watchlist.html",{
        "List":baz
    })

def category(request,category):
    if request.method == "POST":
        bid = Allbids.objects.values("bids__id","user_b").annotate(Max("current_bid")).order_by("bids_id","-current_bid__max")
        List = CreateL.objects.filter(category=category).values()
        users = User.objects.all().values()
        bid = winner(bid,users)
        boo = make_list(List,bid)
        return render(request, "auctions/category.html",{
        "list":boo,
        })
    
    bid = Allbids.objects.values("bids__id","user_b").annotate(Max("current_bid")).order_by("bids_id","-current_bid__max")
    bid = create_max(bid)
    List = CreateL.objects.filter(category=category).values()
    users = User.objects.all().values()
    bid = winner(bid,users)
    boo = make_list(List,bid)
    return render(request, "auctions/category.html",{
        "list":boo,
    })


def selectcat(request):

    allcat = Allcat.objects.all().values()
    print( allcat)
    return render(request, "auctions/allcat.html",{
        "allcat":allcat
    })


def make_list(list1,list2):
    '''List one should be Create Item list and List2 
    is bids'''
    Listall = []
    for i in range(len(list1)):
        boo = list1[i]["id"]
        for j in range(len(list2)):
            if list2[j]["bids__id"] == boo:
                List = {}
                List["id"]=(list1[i]["id"])
                List["title"]=(list1[i]["title"])
                List["description"]=(list1[i]["description"])
                List["category"]=(list1[i]["category"])
                List["user_id"]=list1[i]["user_l_id"]
                if not list2[j]["current_bid__max"]:
                    List["bid"] = list1[i]["bid"]
                    List["image"]=list1[i]["ima"]
                    List["status"]=list1[i]["status"]
                    List["username"]=list2[j]["username"]
                    Listall.append(List)
                else:
                    List["bid"]=(list2[j]["current_bid__max"])
                    List["image"]=list1[i]["ima"]
                    List["status"]=list1[i]["status"]
                    List["username"]=list2[j]["username"]
                    Listall.append(List)
    return Listall


def add_msg(list1,list2):
    """add a msg to list so it can
    detect the watchlist items"""
    Listall = []
    for i in range(len(list1)):
        boo = list1[i]["id"]
        for j in range(len(list2)):
            if list2[j]["list_id_id"] == boo:
                List = {}
                List["id"]=(list1[i]["id"])
                List["title"]=(list1[i]["title"])
                List["description"]=(list1[i]["description"])
                List["category"]=(list1[i]["category"])
                List["bid"] = list1[i]["bid"]
                List["msg"] = "msg"
                List["image"]=list1[i]["image"]
                List["user_id"]=list1[i]["user_id"]
                List["status"]=list1[i]["status"]
                List["username"]=list1[i]["username"]
                Listall.append(List)
            else:
                List = {}
                List["id"]=(list1[i]["id"])
                List["title"]=(list1[i]["title"])
                List["description"]=(list1[i]["description"])
                List["category"]=(list1[i]["category"])
                List["bid"] = list1[i]["bid"]
                List["image"]=list1[i]["image"]
                List["msg"] = "no"
                List["user_id"]=list1[i]["user_id"]
                List["status"]=list1[i]["status"]
                List["username"]=list1[i]["username"]
                Listall.append(List)
    return Listall   


def winner(list1,list2):
    """list1 is the max bid item"""
    Listall = []
    for i in range(len(list1)):
        boo = list1[i]["user_b"]
        for j in range(len(list2)):
            if list2[j]["id"] == boo:
                List = {}
                List["bids__id"]=(list1[i]["bids__id"])
                List["current_bid__max"]=(list1[i]["current_bid__max"])
                List["username"]=list2[j]["username"]
                Listall.append(List)
    return Listall


def create_max(list):
    max_val = list[0]["current_bid__max"]
    Listall = []
    List = {}
    List["bids__id"] = list[0]["bids__id"]
    List["user_b"] = list[0]["user_b"]
    List["current_bid__max"] = list[0]["current_bid__max"]
    Listall.append(List)
    for i in range(len(list) - 1):
        List = {}
        if  i == 0 and int(list[i]["bids__id"]) != int(list[i + 1]["bids__id"]):
                max_val = list[0]["current_bid__max"]
                List["bids__id"] = list[i + 1]["bids__id"]
                List["user_b"] = list[i + 1]["user_b"]
                List["current_bid__max"] = list[i + 1]["current_bid__max"]
                Listall.append(List)
        elif int(list[i]["bids__id"]) != int(list[i + 1]["bids__id"]):
                max_val = list[i + 1]["current_bid__max"]
                List["bids__id"] = list[i + 1]["bids__id"]
                List["user_b"] = list[i + 1]["user_b"]
                List["current_bid__max"] = list[i + 1]["current_bid__max"]
                Listall.append(List)

    return Listall

