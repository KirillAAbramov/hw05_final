from django.test import Client, TestCase


class AboutURLTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.urls = ['/about/author/', '/about/tech/']

    def test_about_app_urls(self):
        """Проверка url-адресов статичных страниц"""
        urls = self.urls
        for url in urls:
            with self.subTest(params=url):
                response = self.client.get(url)
                self.assertEqual(response.status_code, 200)

    def test_about_app_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон"""
        template_names = {
            '/about/author/': 'about/author.html',
            '/about/tech/': 'about/tech.html',
        }
        for url, template in template_names.items():
            with self.subTest(params=url):
                response = self.client.get(url)
                self.assertTemplateUsed(response, template)
