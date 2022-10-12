from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render

from .forms import PostForm
from .models import Group, Post, User


def paginate(req, pag_post):
    paginator = Paginator(pag_post, settings.AMOUNT)
    page_number = req.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return page_obj


def index(request):
    template = 'posts/index.html'
    posts = Post.objects.select_related('group', 'author')

    page_obj = paginate(request, posts)

    context = {
        'posts': posts,
        'page_obj': page_obj,
    }
    return render(request, template, context)


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    posts = group.groups.select_related('group', 'author')

    page_obj = paginate(request, posts)

    template = 'posts/group_list.html'
    context = {
        'group': group,
        'posts': posts,
        'page_obj': page_obj,
    }
    return render(request, template, context)


def profile(request, username):
    author = get_object_or_404(User, username=username)
    posts_auth = author.posts.select_related('group', 'author')

    page_obj = paginate(request, posts_auth)

    context = {
        'author': author,
        'posts_auth': posts_auth,
        'page_obj': page_obj,
    }
    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):

    post = get_object_or_404(Post, pk=post_id)
    context = {
        'post': post,
        'posts_by': post.author.posts.all(),

    }
    return render(request, 'posts/post_detail.html', context)


@login_required
def post_create(request):
    form = PostForm(
        request.POST or None,
    )

    if form.is_valid():
        post = form.save(commit=False)

        post.author = request.user
        post.save()

        return redirect('posts:profile', post.author.username)

    return render(request, 'posts/create_post.html', {'form': form,
                  'is_edit': False})


@login_required
def post_edit(request, post_id):

    post = get_object_or_404(Post, pk=post_id)

    if post.author != request.user:
        return redirect('posts:index')

    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post
    )

    if request.method == 'POST':

        if form.is_valid():
            form.save()
            return redirect('posts:post_detail', post_id)

    return render(request, 'posts/create_post.html',
                  {'form': form, 'is_edit': True, 'post': post})
