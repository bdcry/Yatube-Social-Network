from django.test import Client, TestCase
from posts.models import Group, Post, User


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.guest_client = Client()
        cls.user = User.objects.create(username='TestTim')

        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)

        cls.group = Group.objects.create(
            title='Тестовый заголовок',
            slug='test-group'
        )
        cls.post = Post.objects.create(
            text='Тестовый текст',
            author=PostModelTest.user,
            group=PostModelTest.group,
        )

    def test_verbose_name(self):
        """verbose_name в полях совпадает с ожидаемым."""
        post = PostModelTest.post
        field_verboses = {
            'group': 'group',
            'text': 'text',
        }
        for value, expected in field_verboses.items():
            with self.subTest(value=value):
                self.assertEqual(
                    post._meta.get_field(value).verbose_name, expected)

    def test_help_text(self):
        """help_text в полях совпадает с ожидаемым."""
        post = PostModelTest.post
        field_help_texts = {
            'text': '',
        }
        for value, expected in field_help_texts.items():
            with self.subTest(value=value):
                self.assertEqual(
                    post._meta.get_field(value).help_text, expected)

    def test_post_str_is_equal_to_text(self):
        """В поле __str__ объекта Post написано
           верное значение.
        """
        task = PostModelTest.post
        self.assertEqual(task.__str__(), task.text[:15])

    def test_group_str_is_equal_to_text(self):
        """В поле __str__ объекта Group написано
           верное значение.
        """
        task = Group.objects.first()
        self.assertEqual(task.__str__(), task.title)
