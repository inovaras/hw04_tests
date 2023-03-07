from django.test import Client, TestCase
from django.urls import reverse

from ..forms import PostForm
from ..models import Group, Post, User


class PostCreateFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='author')
        cls.group = Group.objects.create(slug='slug')
        cls.post = Post.objects.create(
            text='Тут какой-то текст:)', author=cls.user, group=cls.group
        )
        cls.form = PostForm()

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_create_post(self):
        """Валидная форма создает новый пост."""
        posts_count = Post.objects.count()
        form_data = {'text': 'Тестовый заголовок', 'group': self.group.pk}
        response = self.authorized_client.post(
            reverse('posts:create'), data=form_data, follow=True
        )
        self.assertRedirects(
            response,
            reverse('posts:profile', kwargs={'username': self.user.username}),
        )
        self.assertEqual(Post.objects.count(), posts_count + 1)

        self.assertTrue(
            Post.objects.filter(
                text=form_data['text'], group=form_data['group']
            ).exists()
        )

    def test_edit_post(self):
        """Валидная форма правит существующий пост"""

        posts_count = Post.objects.count()
        form_data = {'text': 'Тестовый заголовок', 'group': self.group.pk}
        response = self.authorized_client.post(
            reverse('posts:edit', kwargs={'post_id': self.post.id}),
            data=form_data,
            follow=True,
        )
        self.assertRedirects(
            response,
            reverse('posts:post_detail', kwargs={'post_id': self.post.id}),
        )
        self.assertEqual(Post.objects.count(), posts_count)

        self.assertTrue(
            Post.objects.filter(
                text=form_data['text'], group=form_data['group']
            ).exists()
        )
