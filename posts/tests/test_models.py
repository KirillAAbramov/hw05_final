from django.contrib.auth import get_user_model
from django.test import TestCase

from posts.models import Group, Post

User = get_user_model()


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.author = User.objects.create(
            username='test_user'
        )

        cls.group = Group.objects.create(
            title='Название тестируемой группы',
            slug='слаг тестируемой группы',
            description='Описание тестируемой группы'
        )

        cls.post = Post.objects.create(
            text='Текст для теста',
            author=cls.author,
            group=cls.group
        )

    def test_post_verbose_name(self):
        """verbose_name в полях модели post совпадает с ожидаемым"""
        post = PostModelTest.post
        field_verboses = {
            'text': 'Текст',
            'group': 'Группа',
        }
        for key, value in field_verboses.items():
            with self.subTest(params=key):
                self.assertEqual(post._meta.get_field(key).verbose_name, value)

    def test_post_help_text(self):
        """help_text в полях модели post совпадает с ожидаемым"""
        post = PostModelTest.post
        field_help_texts = {
            'text': 'Поле для текста записи',
            'group': 'Группа, в которую можно добавить запись',
        }
        for key, value in field_help_texts.items():
            with self.subTest(params=key):
                self.assertEqual(post._meta.get_field(key).help_text, value)

    def test_group_verbose_name(self):
        """verbose_name в полях модели group совпадает с ожидаемым"""
        group = PostModelTest.group
        verbose = group._meta.get_field('title').verbose_name
        self.assertEqual(verbose, 'Название группы')

    def test_group_help_text(self):
        """help_text в полях модели group совпадает с ожидаемым"""
        group = PostModelTest.group
        help_text = group._meta.get_field('title').help_text
        self.assertEqual(help_text, 'Выберите группу')

    def test_str_post(self):
        """корректность отображения значения поля __str__ в модели post"""
        post = PostModelTest.post
        expected_object_name = post.text
        self.assertEqual(expected_object_name, str(post))

    def test_str_group(self):
        """корректность отображения значения поля __str__ в модели group"""
        group = PostModelTest.group
        expected_object_name = group.title
        self.assertEqual(expected_object_name, str(group))
