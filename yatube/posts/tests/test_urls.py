# posts/tests/test_urls.py
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from posts.models import Group, Post

User = get_user_model()


class StaticURLTests(TestCase):
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
        )

    def setUp(self):
        # Устанавливаем данные для тестирования
        # Создаём экземпляр клиента. Он неавторизован.
        self.guest_client = Client()
        # Создаем авторизованного пользователя
        self.authorized_client = Client()
        # Авторизуем пользователя
        self.authorized_client.force_login(self.post.author)

    # Проверка вызываемых шаблонов для каждого адреса

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        # Шаблоны по адресам
        templates_url_names = {
            '/': 'posts/index.html',
            '/create/': 'posts/create_post.html',
            '/group/test-slug/': 'posts/group_list.html',
            '/profile/test-author/': 'posts/profile.html',
            f'/posts/{self.post.pk}/': 'posts/post_detail.html',
            f'/posts/{self.post.pk}/edit/': 'posts/create_post.html',
        }
        for address, template in templates_url_names.items():
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertTemplateUsed(response, template)

    # Проверяем общедоступные страницы
    # как в correct_template

    def test_guestclient_urls(self):
        """Страницы доступны любому пользователю."""
        url_guest_names = {
            # главная страница
            '/',
            # страница группы
            '/group/test-slug/',
            # страница профиля
            '/profile/test-author/',
            # страница поста
            f'/posts/{self.post.pk}/',
        }
        # Отправляем запрос через client,
        # созданный в setUp()

        for address in url_guest_names:
            with self.subTest(address=address):
                response = self.guest_client.get(address)
                self.assertEqual(response.status_code, 200)

    # Проверяем доступность страниц для авторизованного пользователя

    def test_guestclient_urls(self):
        """Страницы доступны авторизованному пользователю."""
        url_auth_names = {
            '/',
            # страница создания поста
            '/create/',
            # всё те же
            '/group/test-slug/',
            '/profile/test-author/',
            f'/posts/{self.post.pk}/',
            # страница редактирования поста
            f'/posts/{self.post.pk}/edit/',
        }

        for address in url_auth_names:
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertEqual(response.status_code, 200)

    # Проверяем редиректы для неавторизованного пользователя

    def test_task_list_url_redirect_anonymous_on_admin_login(self):
        """Страницы /<page>/ перенаправит анонимного пользователя
        на страницу логина.
        """
        url_guest_names = {
            '/create/',
            f'/posts/{self.post.pk}/edit/',
        }
        # response = self.guest_client.get('/create/', follow=True)
        # self.assertRedirects(
        #     response, '/auth/login/?next=/create/')

        for address in url_guest_names:
            with self.subTest(address=address):
                response = self.guest_client.get(address)
                self.assertRedirects(response, f'/auth/login/?next={address}')
