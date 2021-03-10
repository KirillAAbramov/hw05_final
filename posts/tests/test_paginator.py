import string
from datetime import datetime as dt

from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Group, Post

User = get_user_model()


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group = Group.objects.create(
            title='Test Group',
            slug='testslug',
            description='Описание тестовой группы'
        )

        cls.author = User.objects.create(
            username='Test User'
        )

        for i in range(1, 16):
            cls.post = Post.objects.create(
                text=f'TestText{i}',
                pub_date=dt.now().date(),
                author=cls.author,
                group=cls.group
            )

    def setUp(self):
        self.unauth_client = Client()
        cache.clear()

    def test_first_page_contains_ten_records(self):
        """Тест на проверку количества постов на первой странице,
        их должно быть 10
        """
        list_of_pages = [
            reverse('index'),
            reverse('group', kwargs={'slug': PaginatorViewsTest.group.slug})
        ]
        for item in list_of_pages:
            with self.subTest(params=item):
                response = self.unauth_client.get(item)
                self.assertEqual(
                    len(response.context.get('page').object_list), 10
                )

    def test_second_page_contains_five_records(self):
        """Тест на проверку количества постов на второй странице,
        их должно быть 5
        """
        list_of_pages = [
            reverse('index'),
            reverse('group', kwargs={'slug': PaginatorViewsTest.group.slug})
        ]
        for item in list_of_pages:
            with self.subTest(params=item):
                response = self.unauth_client.get(item + '?page=2')
                self.assertEqual(
                    len(response.context.get('page').object_list), 5
                )

    def test_index_page_show_correct_context(self):
        """Содержимое постов на странице соответствует ожиданиям"""
        response = self.unauth_client.get(reverse('index'))
        for i in range(10):
            with self.subTest(params=i):
                page_context = response.context.get('page').object_list[i]
                posts_text = page_context.text
                posts_author = page_context.author.username
                posts_pub_date = page_context.pub_date.date()
                text = PaginatorViewsTest.post.text.rstrip(string.digits)
                self.assertEqual(posts_text, text + f'{15-i}')
                self.assertEqual(posts_author,
                                 PaginatorViewsTest.author.username)
                self.assertEqual(posts_pub_date,
                                 PaginatorViewsTest.post.pub_date.date())
