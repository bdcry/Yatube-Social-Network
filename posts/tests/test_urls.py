from random import randint
from uuid import uuid1

from django.test import Client, TestCase
from django.urls import reverse
from posts.models import Group, Post, User

NEW_URL = reverse('new_post')
INDEX_URL = reverse('index')
SLUG = 'test_slug'
GROUP_URL = reverse('group_posts', args=[SLUG])
LOGIN_URL = reverse('login')
TESTUSER = 'TestTim'
USER_URL = reverse('profile', args=[TESTUSER])
AUTHOR_URL = reverse('about:author')
TECH_URL = reverse('about:tech')


class StaticURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(
            username=TESTUSER,
            email='testtim@yandex.ru',
            password='141312zs',
        )
        cls.group = Group.objects.create(
            title='Заголовок тестовой задачи',
            description='Тестовый текст',
            slug=SLUG,
        )
        cls.post = Post.objects.create(
            text='Текст тестового поста',
            pub_date='28 Jan 2021',
            author=cls.user,
            group=cls.group,
        )
        cls.user_not_author = User.objects.create(
            username='Oleg',
            email='oleg2002@yandex.ru',
            password='2020123',
        )
        cls.EDIT_AUTHOR = reverse(
            'post_edit',
            args=(cls.user.username, cls.post.id)
        )
        cls.AUTHOR_POST = reverse(
            'post',
            args=(cls.user.username, cls.post.id)
        )
        cls.authorized_author = Client()
        cls.authorized_client_user = Client()
        cls.authorized_author.force_login(cls.user)
        cls.authorized_client_user.force_login(cls.user_not_author)
        cls.guest_client = Client()

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_urls_name = {
            INDEX_URL: 'index.html',
            GROUP_URL: 'group.html',
            NEW_URL: 'new.html',
            self.EDIT_AUTHOR: 'new.html',
            self.AUTHOR_POST: 'post.html'
        }
        for url, template in templates_urls_name.items():
            with self.subTest(url=url):
                self.assertTemplateUsed(
                    self.authorized_author.get(url),
                    template)

    def test_exit_status(self):
        urls_clients = [
            [INDEX_URL, self.guest_client, 200],
            [GROUP_URL, self.guest_client, 200],
            [NEW_URL, self.guest_client, 302],
            [USER_URL, self.guest_client, 200],
            [self.AUTHOR_POST, self.guest_client, 200],
            [self.EDIT_AUTHOR, self.guest_client, 302],
            [AUTHOR_URL, self.guest_client, 200],
            [TECH_URL, self.guest_client, 200],
            [INDEX_URL, self.authorized_author, 200],
            [GROUP_URL, self.authorized_author, 200],
            [NEW_URL, self.authorized_author, 200],
            [USER_URL, self.authorized_author, 200],
            [self.AUTHOR_POST, self.authorized_author, 200],
            [self.EDIT_AUTHOR, self.authorized_author, 200],
            [AUTHOR_URL, self.authorized_author, 200],
            [TECH_URL, self.authorized_author, 200],
            [AUTHOR_URL, self.authorized_client_user, 200],
            [TECH_URL, self.authorized_client_user, 200],
        ]
        for url, client, code in urls_clients:
            with self.subTest(url=url):
                self.assertEqual(client.get(url).status_code, code)

    def test_redirects_for_guest_and_authorized_client(self):
        redirects = [
            [NEW_URL, self.guest_client, f'{LOGIN_URL}?next={NEW_URL}'],
            [self.EDIT_AUTHOR, self.guest_client,
             f'{LOGIN_URL}?next={self.EDIT_AUTHOR}'],
            [self.EDIT_AUTHOR, self.authorized_client_user, self.AUTHOR_POST],
        ]
        for url, client, redirect_url in redirects:
            with self.subTest(url=url):
                self.assertRedirects(client.get(url), redirect_url)

    def test_in_routes_url(self):
        routes_url = {
            INDEX_URL: '/',
            NEW_URL: '/new/',
            GROUP_URL: f'/group/{SLUG}/',
            AUTHOR_URL: '/about/author/',
            TECH_URL: '/about/tech/',
            USER_URL: f'/{TESTUSER}/',
            self.AUTHOR_POST: f'/{TESTUSER}/{self.post.id}/',
            self.EDIT_AUTHOR: f'/{TESTUSER}/{self.post.id}/edit/',
        }
        for url_reversed, url in routes_url.items():
            self.assertEqual(url, url_reversed)

    def test_404(self):
        user404 = str(uuid1())[:5]
        id404 = randint(1000, 2000)
        response = StaticURLTests.guest_client.get(
            reverse('post', args=[user404, id404])
        )
        self.assertEqual(response.status_code, 404)
