# posts/tests/test_views.py
from django import forms
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from posts.models import Group, Post

User = get_user_model()
# self.client.get(reverse('имя_приложения:name')) - reverse


def fobj_assertE(f_obj, slf):
    post_text_0 = f_obj.text
    post_author_0 = f_obj.author
    post_group_0 = f_obj.group

    slf.assertEqual(post_text_0, slf.post.text)
    slf.assertEqual(post_author_0, slf.post.author)
    slf.assertEqual(post_group_0, slf.post.group)


def field_check(resp, slf):
    # Словарь ожидаемых типов полей формы:
    # указываем, объектами какого класса должны быть поля формы
    form_fields = {
        'text': forms.fields.CharField,
        'group': forms.fields.ChoiceField,
    }
    # Проверяем, что типы полей формы в словаре context
    # соответствуют ожиданиям
    for value, expected in form_fields.items():
        with slf.subTest(value=value):
            form_field = resp.context.get('form').fields.get(value)
            slf.assertIsInstance(form_field, expected)


class PostsPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        # Создадим запись в БД для проверки доступности адреса task/test-slug/
        cls.user = User.objects.create_user(username='test-author')

        cls.group = Group.objects.create(
            title='Тестовый заголовок',
            slug='test-slug',
            description='Тестовое описание'
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый текст',
            group=cls.group
        )
        cls.group_other = Group.objects.create(
            title='Тестовый другой заголовок',
            slug='test-other-slug',
            description='Тестовое другое описание'
        )   # без постов

    def setUp(self):
        # Устанавливаем данные для тестирования
        # Создаём экземпляр клиента. Он неавторизован.
        self.guest_client = Client()
        # Создаем авторизованного пользователя
        self.authorized_client = Client()
        # Авторизуем пользователя
        self.authorized_client.force_login(self.post.author)

#

#
    # Проверяем используемые шаблоны
    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        # Собираем в словарь пары "имя_html_шаблона: reverse(name)"
        templates_pages_names = {
            reverse('posts:index'): 'posts/index.html',
            reverse('posts:post_create'): 'posts/create_post.html',
            reverse('posts:group_list', kwargs={'slug': 'test-slug'}
                    ): 'posts/group_list.html',
            reverse('posts:profile', kwargs={'username': 'test-author'}
                    ): 'posts/profile.html',
            reverse('posts:post_detail', kwargs={'post_id': self.post.pk}
                    ): 'posts/post_detail.html',
            reverse('posts:post_edit', kwargs={'post_id':
                    self.post.pk}): 'posts/create_post.html',
        }
        # Проверяем, что при обращении к name вызывается соответствующий шаблон
        for reverse_name, template in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    # Проверка контекста страниц

    # Главна страница
    def test_index_page_show_correct_context(self):
        """Шаблон index сформирован с правильным контекстом."""
        response = self.guest_client.get(reverse('posts:index'))
        # Взяли первый элемент из списка и проверили, что его содержание
        # совпадает с ожидаемым
        first_object = response.context['page_obj'][0]
        fobj_assertE(first_object, self)

    # Страница группы

    def test_group_list_page_show_correct_context(self):
        """Шаблон group_list сформирован с правильным контекстом."""
        response = self.guest_client.get(reverse('posts:group_list',
                                         kwargs={'slug': 'test-slug'}))

        first_object = response.context['page_obj'][0]
        fobj_assertE(first_object, self)

    # Страница профиля

    def test_profile_page_show_correct_context(self):
        """Шаблон profile сформирован с правильным контекстом."""
        response = self.guest_client.get(reverse('posts:profile',
                                         kwargs={'username': 'test-author'}))

        first_object = response.context['page_obj'][0]
        fobj_assertE(first_object, self)

    # Страница поста

    def test_post_detail_page_show_correct_context(self):
        """Шаблон post_detail сформирован с правильным контекстом."""
        response = self.guest_client.get(reverse('posts:post_detail',
                                         kwargs={'post_id': self.post.pk}))

        first_object = response.context['post']
        fobj_assertE(first_object, self)

    # Страница создания поста

    def test_create_show_correct_context(self):
        """Шаблон create_post сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:post_create'))
        field_check(response, self)

    # Страница редактирования поста

    def test_create_edit_show_correct_context(self):
        """Шаблон create_post(edit) сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:post_edit',
                                              kwargs={'post_id': self.post.pk})
                                              )
        field_check(response, self)

#   Поста не существует в другой группе
    def test_post_showes_correct(self):
        """Другая группа осталась пуста."""
        response = self.guest_client.get(
            reverse('posts:group_list', kwargs={'slug': 'test-other-slug'}))

        self.assertFalse(response.context['page_obj'])

# Пажинатор


class PaginatorViewsTest(TestCase):
    # Здесь создаются фикстуры: клиент и 13 тестовых записей.
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        # Создадим запись в БД для проверки доступности адреса task/test-slug/
        cls.user = User.objects.create_user(username='test-author')

        cls.group = Group.objects.create(
            title='Тестовый заголовок',
            slug='test-slug',
            description='Тестовое описание'
        )
        for i in range(13):
            cls.post = (Post.objects.create(
                author=cls.user,
                text=f'Тестовый текст {i}',
                group=cls.group
            ))

    def setUp(self):
        # Устанавливаем данные для тестирования
        # Создаём экземпляр клиента. Он неавторизован.
        self.guest_client = Client()
        # Создаем авторизованного пользователя
        self.authorized_client = Client()
        # Авторизуем пользователя
        self.authorized_client.force_login(self.post.author)

    def test_first_secomd_pages(self):
        index_list = {
            reverse('posts:index'): 'first',
            reverse('posts:group_list', kwargs={'slug': 'test-slug'}): 'first',
            reverse('posts:profile', kwargs={
                'username': 'test-author'}): 'first',

            (reverse('posts:index') + '?page=2'): 'second',
            (reverse('posts:group_list', kwargs={
                'slug': 'test-slug'}) + '?page=2'): 'second',
            (reverse('posts:profile', kwargs={
                'username': 'test-author'}) + '?page=2'): 'second',

        }
        for reverse_name, f_or_sec in index_list.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                if f_or_sec == 'first':
                    indicator = 10
                else:
                    indicator = 3
                self.assertEqual(len(response.context['page_obj']), indicator)
