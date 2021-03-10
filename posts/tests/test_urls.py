from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.test import Client, TestCase

from posts.models import Group, Post

User = get_user_model()


class URLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.group = Group.objects.create(
            title='Тестовый заголовок',
            slug='testslug',
            description='Описание тестовой группы'
        )

        cls.author = User.objects.create(
            username='AuthorName'
        )

        cls.post = Post.objects.create(
            text='text',
            group=cls.group,
            author=cls.author
        )

    def setUp(self):
        self.guest_client = Client()
        self.user = User.objects.create(username='TestUserName')
        self.not_author_authorized_client = Client()
        self.not_author_authorized_client.force_login(self.user)
        self.author_authorized_client = Client()
        self.author_authorized_client.force_login(URLTests.author)

        self.pages = [
            '/',
            '/group/{0}/'.format(URLTests.group.slug),
            '/new/',
            '/{0}/'.format(self.user.username),
            '/{0}/{1}/'.format(URLTests.post.author.username, URLTests.post.id)
        ]

        self.url_edit = '/{0}/{1}/edit/'.format(URLTests.post.author.username,
                                                URLTests.post.id)

    # Проверка доступности страниц
    def test_pages_urls(self):
        """проверка url-адресов страниц"""
        pages = self.pages
        for page in pages:
            with self.subTest(params=page):
                response = self.not_author_authorized_client.get(page)
                self.assertEqual(response.status_code, 200)

    # Проверка редиректа для неавторизованного пользователя
    def test_new_post_page_redirect_unauthorized_user(self):
        """Страница по адресу /new/ перенаправит анонимного
        пользователя на страницу /auth/login/
        """
        response = self.guest_client.get('/new/', follow=True)
        self.assertRedirects(response, '/auth/login/?next=/new/')

    # Проверка вызываемых шаблонов для каждого URL-адреса кроме /edit/
    def test_url_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон"""
        cache.clear()
        templates_names = {
            '/': 'index.html',
            '/group/{0}/'.format(URLTests.group.slug): 'group.html',
            '/new/': 'new_post.html',
            '/{0}/'.format(self.user.username): 'profile.html',
            '/{0}/{1}/'.format(URLTests.post.author.username,
                               URLTests.post.id): 'post.html',
        }
        for url, template in templates_names.items():
            with self.subTest(params=url):
                response = self.not_author_authorized_client.get(url)
                self.assertTemplateUsed(response, template)

    def test_url_post_edit_page(self):
        """Проверка доступности страницы редактирования поста"""
        response_anonymous = self.guest_client.get(self.url_edit)
        response_author = self.author_authorized_client.get(self.url_edit)
        response_not_author = self.not_author_authorized_client.get(
            self.url_edit)
        self.assertEqual(response_anonymous.status_code, 302)
        self.assertEqual(response_author.status_code, 200)
        self.assertEqual(response_not_author.status_code, 302)

    def test_post_edit_page_uses_correct_template(self):
        """Проверка шаблона, который вызывается для страницы редактирования"""
        response = self.author_authorized_client.get(self.url_edit)
        self.assertTemplateUsed(response, 'new_post.html')

    def test_post_edit_page_redirect_for_not_authors(self):
        """Проверка работы редиректа для тех у кого нет права
        доступа к странице
        """
        response_anonymous = self.guest_client.get(self.url_edit, follow=True)
        response_not_author = self.not_author_authorized_client.get(
            self.url_edit)
        self.assertRedirects(response_anonymous, '/auth/login/?next=/'
                                                 'AuthorName/1/edit/')
        self.assertRedirects(response_not_author, '/AuthorName/1/')

    def test_server_return_404_if_page_not_found(self):
        """Сервер должен возвращать код 404, если страница не найдена"""
        wrong_url = '/wrong_url/'
        response = self.guest_client.get(wrong_url)
        self.assertEqual(response.status_code, 404)
