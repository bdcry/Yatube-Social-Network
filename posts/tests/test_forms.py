from django.test import Client, TestCase
from django.urls import reverse
from posts.models import Group, Post, User

SLUG = 'test_slug'
NEW_URL = reverse('new_post')


class StaticCreateFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(
            username='TestTim',
            email="testtim@gmail.com",
            password="1234tim")
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)
        cls.group = Group.objects.create(
            slug=SLUG,
            title='testtitle',
            description='testcription'
        )
        cls.post = Post.objects.create(
            text='test text',
            author=cls.user,
            group=cls.group
        )
        cls.EDIT_AUTHOR = reverse(
            'post_edit',
            args=(cls.user.username, cls.post.id)
        )

    def test_create_new_post(self):
        """При отправке формы создаётся новая запись в базе данных."""
        group = Group.objects.create(
            title='testgroup1',
            slug='test_group1',
        )
        counter = Post.objects.count()
        form_data = {
            'text': 'Тестовый текст',
            'author': self.user,
            'group': group.id,
        }
        self.authorized_client.post(
            NEW_URL,
            data=form_data,
            follow=True
        )
        self.assertEqual(Post.objects.count(), counter + 1)
        self.assertEqual(Post.objects.count(), 2)
        post_new = Post.objects.exclude(id=self.post.id)[0]
        self.assertEqual(post_new.text, form_data['text'])
        self.assertEqual(post_new.group.id, form_data['group'])
        self.assertEqual(self.user, self.post.author)

    def test_edit_post(self):
        """Изменение поста его изменяет в БД"""
        group = Group.objects.create(
            title='testgroup2',
            slug='test_group2',
        )
        post_count = Post.objects.count()
        form_data = {
            'text': 'тестовый текст',
            'group': group.id,
        }
        self.authorized_client.post(
            self.EDIT_AUTHOR,
            data=form_data, follow=True)
        post_edit = Post.objects.first()
        self.assertEqual(Post.objects.count(), post_count)
        self.assertEqual(post_edit.text, form_data['text'])
        self.assertEqual(post_edit.author, self.user)
        self.assertEqual(post_edit.group, group)
