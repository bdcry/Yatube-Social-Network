from django import forms
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase
from django.urls import reverse
from posts.models import Comment, Follow, Group, Post, User
from yatube.settings import PAGINATOR_LIMIT

NEW_URL = reverse('new_post')
INDEX_URL = reverse('index')
SLUG = 'test_slug'
GROUP_URL = reverse('group_posts', args=[SLUG])
SLUG1 = 'test-slug'
GROUP_URL1 = reverse('group_posts', args=[SLUG1])
TESTUSER = 'TestTim'
USER_URL = reverse('profile', args=[TESTUSER])


class PostPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(
            username=TESTUSER,
            email="testtim@yandex.ru",
            password="141312zs",
        )
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)
        cls.guest_client = Client()
        cls.group = Group.objects.create(
            title='Заголовок тестовой задачи',
            description='Тестовый текст',
            slug=SLUG,
        )
        cls.group_no_post = Group.objects.create(
            title='Заголовок тестовой задачи',
            description='Тестовый текст!',
            slug=SLUG1,
        )
        cls.post = Post.objects.create(
            text="test text",
            author=cls.user,
            group=cls.group,
        )
        cls.AUTHOR_POST = reverse(
            'post',
            args=(cls.user.username, cls.post.id)
        )
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x01\x00\x01\x00\x00\x00\x00\x21\xf9\x04'
            b'\x01\x0a\x00\x01\x00\x2c\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02'
            b'\x02\x4c\x01\x00\x3b'
        )
        # Создаем пост с картинкой
        cls.uploaded = SimpleUploadedFile(
            'small.gif', small_gif, content_type='image/gif')

    def test_post_page_show_correct_context(self):
        """Страницa post сформированa с правильным контекстом."""
        response = self.authorized_client.get(NEW_URL)
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }

        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get(
                    'form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_pages_contains_paginator(self):
        author = User.objects.first()
        for post in range(PAGINATOR_LIMIT):
            Post.objects.create(
                text=PAGINATOR_LIMIT,
                author=author,
            )
        response = self.authorized_client.get(INDEX_URL)
        self.assertEqual(len(response.context['page']), PAGINATOR_LIMIT)

    def test_post_appear_on_all_pages(self):
        subscriptable_urls = [
            [INDEX_URL, self.guest_client],
            [GROUP_URL, self.guest_client],
            [USER_URL, self.guest_client],
            [self.AUTHOR_POST, self.guest_client],
        ]
        for url, client in subscriptable_urls:
            with self.subTest(url=url):
                response = client.get(url)
                if 'post' in response.context:
                    response_context_post = response.context['post']
                    self.assertEqual(response_context_post, self.post)
                elif 'page' in response.context:
                    response_context_page = response.context['page'][0]
                    self.assertEqual(response_context_page, self.post)
                    self.assertEqual(Post.objects.count(), 1)

    def test_post_dont_appear_in_alien_group(self):
        """Пост не появляется в другой группе"""
        response = self.authorized_client.get(GROUP_URL1)
        self.assertNotIn(self.post, response.context['page'])

    def test_image_everywhere(self):
        """Проверяет, что картинка есть на всех
        связанных страницах
        """
        # Ищем картинку на главной странице
        response = self.client.get(INDEX_URL)
        self.assertContains(
            response, self.uploaded, status_code=200, count=0,
            msg_prefix='Тэг не найден на главной странице',
            html=False
        )
        # На странице поста
        response = self.client.get(USER_URL)
        self.assertContains(
            response, self.uploaded, status_code=200, count=0,
            msg_prefix='Тэг не найден на странице профиля',
            html=False
        )
        # На странице группы
        response = self.client.get(GROUP_URL)
        self.assertContains(
            response, self.uploaded, status_code=200, count=0,
            msg_prefix='Тэг не найден на странице группы',
            html=False
        )

    def test_cache(self):
        self.guest_client.get(INDEX_URL)
        self.authorized_client.post(NEW_URL, {'text': 'Test text'})
        response = self.guest_client.get(INDEX_URL)
        self.assertNotContains(response, 'Test text')

    def test_comment(self):
        """
        Только авторизированный пользователь может комментировать посты.
        """
        comment = Comment.objects.create(
            post=self.post, text="First comment", author=self.user)
        response = self.client.post(f'/{self.user.username}/{self.post.pk}/')
        self.assertContains(response, comment.text)


class TestFollowSystem(TestCase):
    def setUp(self):
        self.client = Client()
        self.following = User.objects.create(
            username='TestFollowing', password='password')
        self.follower = User.objects.create(
            username='TestFollower', password='password')
        self.user = User.objects.create(username='user', password='password')
        self.post = Post.objects.create(author=self.following,
                                        text='FollowTest')
        self.client.force_login(self.follower)
        self.link = Follow.objects.filter(user=self.follower,
                                          author=self.following)

    def test_follow(self):
        """
        Авторизованный пользователь может подписываться на
        других пользователей.
        """
        response = self.client.get(reverse('profile_follow', kwargs={
            'username': self.following}), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(self.link.exists())
        self.assertEqual(1, Follow.objects.count())

    def test_unfollow(self):
        """
        Авторизованный пользователь может удалять
        других пользователей из подписок.
        """
        response = self.client.get(
            reverse('profile_unfollow',
                    kwargs={'username': self.following}),
            follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(0, Follow.objects.count())

    def test_follow_index(self):
        Follow.objects.create(user=self.follower, author=self.following)
        follow_index_url = reverse('follow_index')
        response = self.client.get(follow_index_url)
        self.assertContains(response, self.post.text)

        self.client.force_login(self.user)
        response = self.client.get(follow_index_url)
        self.assertNotContains(response, self.post.text)
