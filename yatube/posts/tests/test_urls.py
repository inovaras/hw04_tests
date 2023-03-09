from django.test import TestCase, Client

from ..models import Group, Post, User


USERNAME = 'author'
SLUG = 'some_slug'
TEXT = 'Проверочный текст'


class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username=USERNAME)
        cls.group = Group.objects.create(slug=SLUG)
        cls.post = Post.objects.create(
            text=TEXT, author=cls.user, group=cls.group
        )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        template_url_name = (
            (f'/group/{self.group.slug}/', 'posts/group_list.html'),
            (f'/profile/{self.user.username}/', 'posts/profile.html'),
            (f'/posts/{self.post.id}/', 'posts/post_detail.html'),
            ('/create/', 'posts/create.html'),
            (f'/posts/{self.post.id}/edit/', 'posts/create.html'),
        )

        for address, template in template_url_name:
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertTemplateUsed(response, template)
