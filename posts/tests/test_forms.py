import shutil
import tempfile

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from posts.forms import PostForm
from posts.models import Comment, Group, Post

User = get_user_model()

settings.MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=settings.MEDIA_ROOT)
class NewPostFormTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.group = Group.objects.create(
            title='Заголовок тестовой группы',
            slug='testslug',
            description='Описание тестовой группы'
        )

        cls.author = User.objects.create(
            username='Test User'
        )

        cls.form = PostForm()

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(settings.MEDIA_ROOT, ignore_errors=True)
        super().tearDownClass()

    def setUp(self):
        self.auth_client = Client()
        self.auth_client.force_login(NewPostFormTest.author)

    def test_new_post(self):
        """Проверка формы добавления нового поста"""
        posts_count = Post.objects.count()

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

        form_data = {
            'text': 'Текст для теста формы',
            'author': NewPostFormTest.author,
            'group': NewPostFormTest.group.id,
            'image': uploaded,
        }

        response = self.auth_client.post(
            reverse('new_post'),
            data=form_data,
            follow=True,
        )

        self.assertRedirects(response, reverse('index'))
        self.assertEqual(Post.objects.count(), posts_count + 1)
        self.assertTrue(
            Post.objects.filter(
                text='Текст для теста формы',
                author=NewPostFormTest.author,
                group=NewPostFormTest.group,
            ).exists()
        )

    def test_edit_post(self):
        """Проверка формы редактирования поста"""
        self.post = Post.objects.create(
            text='Текст',
            author=NewPostFormTest.author
        )

        form_data = {
            'text': 'Текст изменился',
            'author': NewPostFormTest.author,
        }

        response_edit = self.auth_client.post(
            reverse('post_edit', args=[NewPostFormTest.author.username,
                    self.post.id]),
            data=form_data,
            follow=True
        )

        self.post.refresh_from_db()

        self.assertRedirects(response_edit, reverse('post',
                             args=[NewPostFormTest.author.username,
                                   self.post.id]))
        self.assertTrue(
            Post.objects.filter(
                text='Текст изменился',
                author=NewPostFormTest.author
            ).exists()
        )
        self.assertFalse(
            Post.objects.filter(
                text='Текст',
                author=NewPostFormTest.author
            ).exists()
        )

    def test_only_authorized_user_comment_posts(self):
        """Только авторизированный пользователь может комментировать посты"""
        user1 = User.objects.create(username='user1')
        user_client1 = Client()
        user_client1.force_login(user1)

        user_client2 = Client()

        author = User.objects.create(username='author')
        user2 = User.objects.create(username='user2')

        post = Post.objects.create(
            text='Text',
            author=author
        )

        form_data = {
            'text': 'Comment for Text',
            'author': user2,
            'post': post,
        }

        comment_count1 = Comment.objects.count()
        user_client1.post(reverse('add_comment',
                          args=[author.username, post.id]),
                          data=form_data)

        self.assertEqual(Comment.objects.count(), comment_count1 + 1)

        comment_count2 = Comment.objects.count()
        user_client2.post(reverse('add_comment',
                          args=[author.username, post.id]),
                          data=form_data)

        self.assertNotEqual(Comment.objects.count(), comment_count2 + 1)
