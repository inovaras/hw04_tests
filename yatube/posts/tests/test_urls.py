from django.test import TestCase, Client

from ..models import Group, Post, User


USERNAME = 'author'
SLUG = 'some_slug'
TEXT = 'some text'


class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username=USERNAME)
        cls.group = Group.objects.create(slug=SLUG)
        cls.post = Post.objects.create(
            text=TEXT, author=cls.user, group=cls.group
        )
        cls.access_url_address_map = {
            '/': 'all',
            f'/group/{cls.group.slug}/': 'all',
            f'/profile/{cls.user.username}/': 'all',
            f'/posts/{cls.post.id}/': 'all',
            '/create/': 'authorized',
            f'/posts/{cls.post.id}/edit/': 'author',
        }
        cls.template_url_name = {
            f'/group/{cls.group.slug}/': 'posts/group_list.html',
            f'/profile/{cls.user.username}/': 'posts/profile.html',
            f'/posts/{cls.post.id}/': 'posts/post_detail.html',
            '/create/': 'posts/create.html',
            f'/posts/{cls.post.id}/edit/': 'posts/create.html'
        }

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""

        for address, template in self.template_url_name.items():
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertTemplateUsed(response, template)

    def test_url_access_for_authorized_only(self):
        """Страницы, доступные только авторизованным пользователям"""
        for address, access, in self.access_url_address_map.items():
            if access == 'authorized':
                with self.subTest(address=address):
                    response = self.authorized_client.get(address)
                    self.assertEqual(response.status_code, 200)
