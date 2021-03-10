from django.test import Client, TestCase
from django.urls import reverse


class AboutViewsTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.reverse_names = [
            reverse('about:author'),
            reverse('about:tech')
        ]

    def test_about_app_pages_accessible_by_name(self):
        """URL, генерируемый при помощи reverse доступен"""
        reverse_names = self.reverse_names
        for name in reverse_names:
            with self.subTest(params=name):
                response = self.client.get(name)
                self.assertEqual(response.status_code, 200)

    def test_about_app_pages_uses_correct_template(self):
        """При запросе при помощи reverse применяется
        правильный шаблон, соответствующий странице
        """
        template_names = {
            'about/author.html': reverse('about:author'),
            'about/tech.html': reverse('about:tech'),
        }
        for template, reverse_name in template_names.items():
            with self.subTest(params=template):
                response = self.client.get(reverse_name)
                self.assertTemplateUsed(response, template)
