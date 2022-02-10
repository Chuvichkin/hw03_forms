from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Post, Group, User
from .forms import PostForm
# from datetime import datetime
# from django.utils import timezone
NUM_OF_POSTS = 10


def index(request):
    text = 'Последние обновления на сайте'
    post_list = Post.objects.all()
    paginator = Paginator(post_list, NUM_OF_POSTS)
    # Из URL извлекаем номер запрошенной страницы - это значение параметра page
    page_number = request.GET.get('page')
    # Получаем набор записей для страницы с запрошенным номером
    page_obj = paginator.get_page(page_number)
    # Отдаем в словаре контекста
    context = {'page_obj': page_obj, 'text': text}
    template = 'posts/index.html'
    return render(request, template, context)


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    post_list = group.posts.all()
    paginator = Paginator(post_list, NUM_OF_POSTS)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'page_obj': page_obj,
        'group': group,
    }
    return render(request, 'posts/group_list.html', context)


def profile(request, username):
    profile = get_object_or_404(User, username=username)
    post_list = (
        Post.objects.select_related("author", "group")
        .filter(author=profile)
        .order_by("-pub_date")
        .all()
    )
    posts_count = post_list.count()
    paginator = Paginator(post_list, NUM_OF_POSTS)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'profile': profile,
        'posts_count': posts_count,
        'page_obj': page_obj,
    }
    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    context = {'post': post}
    return render(request, 'posts/post_detail.html', context)


@login_required
def post_create(request):
    if request.method == "POST":
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            return redirect('posts:profile', post.author)
        return render(request, 'posts/create_post.html', {'form': form})
    else:
        form = PostForm()
    return render(request, 'posts/create_post.html', {'form': form})


"""def post_edit(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    is_edit = True
    if request.method == "POST":
        form = PostForm(request.POST, instance=post)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            return redirect('posts:post_detail', pk=post_id)
        form = PostForm(instance=post)
    return render(request, 'posts/create_post.html', {'form': form,
    'is_edit': is_edit})"""


"""def post_edit(request, username, post_id):
    # Редактирование поста
    post = get_object_or_404(Post, id=post_id)
    # проверка, что текущий юзер и автор поста совпадают
    if request.user == post.author:
        if request.method == "POST":
            form = PostForm(
                request.POST or None,
                files=request.FILES or None,
                instance=post
            )
            if form.is_valid():
                post = form.save(commit=False)
                post.author = request.user
                post.save()
                return redirect("post", username=username, post_id=post_id)
        else:
            form = PostForm(instance=post)
        return render(request, "new_post.html", {"form": form, "post": post})
    return redirect("post", username=username, post_id=post_id)"""


@login_required
def post_edit(request, post_id):
    is_edit = True
    post = get_object_or_404(Post, pk=post_id)
    if post.author == request.user:
        form = PostForm(request.POST or None,
                        files=request.FILES or None, instance=post)
        if form.is_valid():
            post = form.save()
            return redirect('posts:post_detail', post.pk)
        form = PostForm(instance=post)
        return render(request, "posts/create_post.html",
                      {'form': form, "is_edit": is_edit})
    else:
        return redirect('posts:post_detail', post.pk)
