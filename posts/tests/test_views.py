import shutil
import tempfile
from datetime import datetime as dt

from django import forms
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from posts.models import Group, Post, Follow

User = get_user_model()

settings.MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=settings.MEDIA_ROOT)
class ViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group = Group.objects.create(
            title='Заголовок тестовой группы',
            slug='testslug',
            description='Описание тестовой группы'
        )

        cls.author = User.objects.create(
            username='test_user'
        )

        cls.post = Post.objects.create(
            text='Текст для теста',
            pub_date=dt.now().date(),
            author=cls.author,
            group=cls.group
        )

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(settings.MEDIA_ROOT, ignore_errors=True)
        super().tearDownClass()

    def setUp(self):
        self.guest_client = Client()
        self.user = User.objects.create(username='TestUserName')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.author_authorized_client = Client()
        self.author_authorized_client.force_login(ViewsTest.author)

        self.reverse_index = reverse('index')
        self.reverse_group = reverse('group', kwargs={
            'slug': ViewsTest.group.slug
        })
        self.reverse_new_post = reverse('new_post')

    # Проверка используемых шаблонов(view-функции используют ожидаемые шаблоны)
    def test_page_uses_correct_template(self):
        """Какой шаблон будет вызван при обращении к
        view-классам через соответствующий name
        """
        cache.clear()
        templates_names = {
            'index.html': self.reverse_index,
            'group.html': self.reverse_group,
            'new_post.html': self.reverse_new_post,
        }

        for template, reverse_name in templates_names.items():
            with self.subTest(params=template):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    # Проверка передачи в шаблон правильного контекста
    def test_home_page_show_correct_context(self):
        """Шаблон страницы index сформирован с правильным контекстом"""
        cache.clear()
        response = self.guest_client.get(self.reverse_index)
        page_context = response.context.get('page')[0]
        self.assertEqual(page_context.text, ViewsTest.post.text)
        self.assertEqual(page_context.group.title, ViewsTest.group.title)
        self.assertEqual(page_context.author.username,
                         ViewsTest.post.author.username)
        self.assertEqual(page_context.pub_date.date(),
                         ViewsTest.post.pub_date.date())
        cache.clear()

    def test_group_posts_page_show_correct_context(self):
        """Шаблон страницы group сформирован с правильным контекстом"""
        response = self.guest_client.get(self.reverse_group)
        page_context = response.context.get('page')[0]
        group_context = response.context.get('group')
        self.assertEqual(group_context.title, ViewsTest.group.title)
        self.assertEqual(group_context.slug, ViewsTest.group.slug)
        self.assertEqual(group_context.description,
                         ViewsTest.group.description)
        self.assertEqual(page_context.text, ViewsTest.post.text)
        self.assertEqual(page_context.pub_date.date(),
                         ViewsTest.post.pub_date.date())
        self.assertEqual(page_context.author.username,
                         ViewsTest.post.author.username)

    def test_new_post_page_show_correct_context(self):
        """Шаблон страницы new_post сформирован с правильным контекстом"""
        response = self.authorized_client.get(self.reverse_new_post)
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField
        }
        for field_name, field_type in form_fields.items():
            with self.subTest(params=field_name):
                form_field = response.context.get('form').fields[field_name]
                self.assertIsInstance(form_field, field_type)

    def test_post_in_correct_group(self):
        """Пост попал в нужную группу"""
        response = self.authorized_client.get(self.reverse_group)
        self.assertEqual(len(response.context.get('page')), 1)

    def test_post_not_in_wrong_group(self):
        """Пост не попал в неправильную группу"""
        group = Group.objects.create(
            title='Заголовок неправильной группы',
            slug='wrong-testslug',
            description='Описание неправильной группы'
        )
        response = self.authorized_client.get(reverse(
            'group', kwargs={'slug': group.slug}))
        self.assertEqual(len(response.context.get('page')), 0)

    def test_profile_page_show_correct_context(self):
        """Шаблон страницы профайла пользователя сформирован
        с правильным контекстом
        """
        response = self.authorized_client.get(reverse('profile',
                                              args=[self.user.username]))
        response_author = self.author_authorized_client.get(
            reverse('profile', args=[ViewsTest.author.username]))
        page_context = response_author.context.get('page')[0]
        self.assertEqual(response.context.get('author').username,
                         self.user.username)
        self.assertEqual(page_context.text, ViewsTest.post.text)
        self.assertEqual(page_context.pub_date.date(),
                         ViewsTest.post.pub_date.date())

    def test_post_view_page_show_correct_context(self):
        """Шаблон страницы просмотра отдельного поста сформирован
        с правильным контекстом
        """
        response_author = self.author_authorized_client.get(
            reverse('post',
                    args=[ViewsTest.author.username, ViewsTest.post.id]))
        post_context = response_author.context.get('post')
        self.assertEqual(response_author.context.get('author').username,
                         ViewsTest.post.author.username)
        self.assertEqual(post_context.text, ViewsTest.post.text)
        self.assertEqual(post_context.pub_date.date(),
                         ViewsTest.post.pub_date.date())

    def test_post_edit_page_show_correct_context(self):
        """Шаблон страницы редактирования поста сформирован с правильным
        контекстом
        """
        response = self.author_authorized_client.get(
            reverse('post_edit',
                    args=[ViewsTest.author.username, ViewsTest.post.id]))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField
        }
        for field_name, field_type in form_fields.items():
            with self.subTest(params=field_name):
                form_field = response.context.get('form').fields[field_name]
                self.assertIsInstance(form_field, field_type)

    def test_image_in_context(self):
        """При выводе поста с картинкой изображение передается
        в словаре context
        """
        cache.clear()
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x01\x00'
            b'\x01\x00\x00\x00\x00\x21\xf9\x04'
            b'\x01\x0a\x00\x01\x00\x2c\x00\x00'
            b'\x00\x00\x01\x00\x01\x00\x00\x02'
            b'\x02\x4c\x01\x00\x3b'
        )
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )

        author = User.objects.create(
            username="Author_image"
        )

        group = Group.objects.create(
            title='Title',
            slug='slug',
            description='description'
        )

        post_with_image = Post.objects.create(
            text='text',
            pub_date=dt.now().date(),
            author=author,
            group=group,
            image=uploaded
        )

        reverse_names = [
            self.reverse_index,
            reverse('group', args=[group.slug]),
            reverse('profile', args=[author.username])
        ]

        for reverse_name in reverse_names:
            with self.subTest(params=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertEqual(response.context.get('page')[0].image,
                                 post_with_image.image)

        response_post = self.authorized_client.get(
            reverse('post', args=[author.username, post_with_image.id]))
        self.assertEqual(response_post.context.get('post').image,
                         post_with_image.image)

    def test_cache_index(self):
        """Тест кэша"""
        cache.clear()
        response1 = self.authorized_client.get(reverse('index'))
        Post.objects.create(
            text='Text Cache',
            author=ViewsTest.author
        )
        self.assertEqual(len(response1.context.get('page').object_list), 1)
        cache.clear()
        response2 = self.authorized_client.get(reverse('index'))
        self.assertEqual(len(response2.context.get('page').object_list), 2)

    def test_authorized_user_follows_other_users(self):
        """Авторизованный пользователь может подписываться на других"""
        user = User.objects.create(username='user')
        user_client = Client()
        user_client.force_login(user)

        author = User.objects.create(username='author')
        author_client = Client()
        author_client.force_login(author)

        follow = Follow.objects.count()

        Follow.objects.create(user=user, author=author)

        self.assertEqual(Follow.objects.count(), follow + 1)

    def test_authorized_user_unfollows_other_users(self):
        """Авторизованный пользователь может удалять пользователей
        из своих подписок
        """
        user = User.objects.create(username='user')
        user_client = Client()
        user_client.force_login(user)

        author = User.objects.create(username='author')
        author_client = Client()
        author_client.force_login(author)

        Follow.objects.create(user=user, author=author)
        follow = Follow.objects.count()
        Follow.objects.filter(user=user, author=author).delete()

        self.assertEqual(Follow.objects.count(), follow - 1)

    def test_new_post_in_news_feed(self):
        """Новая запись пользователя появляется в ленте тех,
        кто на него подписан и не появляется в ленте тех,
        кто на него не подписан
        """
        user1 = User.objects.create(username='user1')
        user_client1 = Client()
        user_client1.force_login(user1)

        user2 = User.objects.create(username='user2')
        user_client2 = Client()
        user_client2.force_login(user2)

        author = User.objects.create(username='author')

        post = Post.objects.create(author=author, text='text')
        Follow.objects.create(user=user1, author=author)

        response1 = user_client1.get(reverse('follow_index'))
        response2 = user_client2.get(reverse('follow_index'))

        self.assertIn(post, response1.context.get('page').object_list)
        self.assertNotIn(post, response2.context.get('page').object_list)
