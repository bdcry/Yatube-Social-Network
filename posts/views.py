from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator
from .models import Post, Group, User, Comment, Follow
from .forms import PostForm, CommentForm
from yatube.settings import PAGINATOR_LIMIT


def index(request):
    post_list = Post.objects.all()
    paginator = Paginator(post_list, PAGINATOR_LIMIT)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    context = {
        'page': page,
        'paginator': paginator,
    }
    return render(request, 'index.html', context)


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    posts_list = group.posts.all()
    paginator = Paginator(posts_list, PAGINATOR_LIMIT)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    context = {
        'page': page,
        'paginator': paginator,
        'group': group
    }
    return render(request, 'group.html', context)


@login_required
def new_post(request):
    form = PostForm(request.POST or None)
    if not form.is_valid():
        return render(request, 'new.html', {'form': form})
    new_form = form.save(commit=False)
    new_form.author = request.user
    new_form.save()
    return redirect('index')
    context = {
        'form': form,
        'post': True,
    }
    return render(request, 'new.html', context)


def profile(request, username):
    author = get_object_or_404(User, username=username)
    post_list = author.posts.all()
    paginator = Paginator(post_list, PAGINATOR_LIMIT)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)

    if request.user.is_authenticated:
        following = author.following.filter(user=request.user).exists()
        return render(request, "profile.html", {
            'author': author,
            'page': page, 'paginator': paginator, 'following': following})
    return render(request, "profile.html", {
        'author': author, 'page': page, 'paginator': paginator})


def post_view(request, username, post_id):
    username = get_object_or_404(User, username=username)
    post = get_object_or_404(Post, pk=post_id)
    count = Post.objects.filter(
        author=username).select_related('author').count()
    form = CommentForm(request.POST)
    comment = Comment.objects.filter(post=post_id)
    context = {
        'post': post,
        'author': post.author,
        'count': count,
        'comments': comment,
        'form': form
    }
    return render(request, 'post.html', context)


@login_required
def post_edit(request, username, post_id):
    post = get_object_or_404(
        Post,
        id=post_id,
        author__username=username,
    )
    if request.user != post.author:
        return redirect('post', username=username, post_id=post_id)
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post
    )
    if form.is_valid():
        form.save()
        return redirect('post', username=post.author, post_id=post_id)
    return render(request, 'new.html', {'form': form, 'post': post})


def page_not_found(request, exception):
    return render(
        request,
        "misc/404.html",
        {"path": request.path},
        status=404
    )


def server_error(request):
    return render(request, "misc/500.html", status=500)


@login_required
def add_comment(request, post_id, username):
    post = get_object_or_404(Post, pk=post_id)
    form = CommentForm(request.POST)
    if request.method == 'POST':
        if form.is_valid():
            form = form.save(commit=False)
            form.author = request.user
            form.post = post
            form.save()
            return redirect('post', username, post_id)
        return render(request, 'comments.html', {'form': form})
    return render(request, 'comments.html', {'form': form, 'post': post})


@login_required
def follow_index(request):
    follows = Follow.objects.filter(user=request.user).values('author')
    following_list = Post.objects.filter(
        author_id__in=follows).order_by("-pub_date")
    paginator = Paginator(following_list, PAGINATOR_LIMIT)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(request, 'follow.html', {
        'page': page, 'paginator': paginator})

@login_required
def profile_follow(request, username):
    user = get_object_or_404(User, username=username)
    if request.user != user:
        Follow.objects.get_or_create(user=request.user, author=user)
        return redirect('profile', username)
    return redirect('profile', username)

@login_required
def profile_unfollow(request, username):
    user = get_object_or_404(User, username=username)
    Follow.objects.filter(user=request.user).filter(author=user).delete()
    return redirect('profile', username)