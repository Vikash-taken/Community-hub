from django.contrib.auth import authenticate, login, logout
from django.core import paginator
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db import IntegrityError
from django.db.models import (
    Count,
    DurationField,
    ExpressionWrapper,
    F,
    FloatField,
    Q,
)
from django.db.models.functions import Cast
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.template.loader import render_to_string
from django.utils import timezone

from .models import Comment, Community, Post, User, Vote


def index(request):
    # calculate the upvote an downvote of post
    posts = Post.objects.annotate(
        upvote_count=Count("votes", filter=Q(votes__direction=1)),
        downvote_count=Count("votes", filter=Q(votes__direction=-1)),
    )

    # check if user is requestion certain group
    group_id = request.GET.get("group_id")
    if group_id:
        posts = posts.filter(community_id=group_id)

    now = timezone.now()

    # arranging data according to popularity
    posts = (
        posts.annotate(
            net_vote=F("vote_score"),
            time_diff=ExpressionWrapper(
                now - F("post_created"), output_field=DurationField()
            ),
        )
        .annotate(
            escaped_time_hours=Cast(F("time_diff"), FloatField()) / 1000000.0 / 3600.0
        )
        .annotate(
            hotness=ExpressionWrapper(
                F("vote_score") / (F("escaped_time_hours") + 2.0),
                output_field=FloatField(),
            )
        )
        .order_by("-hotness", "-post_created")
    )

    # sending data 10 at a time
    # paginatior spilts data in different pages each containing 10
    paginator = Paginator(posts, 10)
    page_number = request.GET.get("page", 1)

    try:
        page_obj = paginator.page(page_number)
    except (EmptyPage, PageNotAnInteger):
        if request.headers.get("x-requested-with") == "XMLHttpRequest":
            return JsonResponse({"html": "", "has_next": False})
        page_obj = paginator.page(1)

    if request.headers.get("x-requested-with") == "XMLHttpRequest":
        html = render_to_string(
            "network/post_list.html", {"posts": page_obj}, request=request
        )
        return JsonResponse({"html": html, "has_next": page_obj.has_next()})

    # Get all the commmunities
    communities = Community.objects.all()

    return render(
        request,
        "network/index.html",
        {
            "posts": page_obj,
            "communities": communities,
            "has_next": page_obj.has_next(),
        },
    )


def view_comment(request, post_id):
    # For Upvote and Downvote of Comment
    post = get_object_or_404(Post, pk=post_id)
    comments = (
        post.comments.annotate(
            upvote_count=Count("votes", filter=Q(votes__direction=1)),
            downvote_count=Count("votes", filter=Q(votes__direction=-1)),
        )
        .annotate(comment_score=F("upvote_count") - F("downvote_count"))
        .order_by("-comment_score", "-comment_created")
    )

    # Pagination: Sepeting comments in small parts
    paginator = Paginator(comments, 20)
    page_number = request.GET.get("page", 1)
    page_obj = paginator.get_page(page_number)

    # Look for API calls
    if request.headers.get("x-requested-with") == "XMLHttpRequest":
        html = render_to_string(
            "network/comment_list.html",
            {"comments": page_obj, "post": post},
            request=request,
        )
        return JsonResponse({"html": html, "has_next": page_obj.has_next()})

    return render(request, "network/post.html", {"comments": page_obj, "post": post})


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return redirect("network:index")
        else:
            return render(
                request,
                "network/login.html",
                {"message": "Invalid username or password."},
            )
    else:
        return render(request, "network/login.html")


def logout_view(request):
    logout(request)
    return redirect("network:index")


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure that username and email are provided
        if not username or not email:
            return render(
                request,
                "network/register.html",
                {"message": "Username and Emanil field should not be empty"},
            )

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(
                request,
                "network/register.html",
                {"message": "Passwords must match."},
            )

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(
                request,
                "network/register.html",
                {"message": "Username already taken."},
            )
        login(request, user)
        return redirect("network:index")
    else:
        return render(request, "network/register.html")
