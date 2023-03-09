from django.test import Client, TestCase
from django.urls import reverse
from django import forms

from ..models import User, Group, Post
from ..consts import POSTS_NUMBERS


USERNAME = 'author'
SLUG = 'slug'
ANOTHER_SLUG = 'another_slug'
TEXT = 'Тут какой-то текст:)'


class PostPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username=USERNAME)
        cls.group = Group.objects.create(slug=SLUG)
        cls.another_group = Group.objects.create(slug=ANOTHER_SLUG)
        cls.post = Post.objects.create(
            text=TEXT, author=cls.user, group=cls.group
        )
        cls.url_address_map = {
            'index': reverse('posts:index'),
            'group_list': reverse(
                'posts:group_list', kwargs={'slug': cls.group.slug}
            ),
            'profile': reverse(
                'posts:profile', kwargs={'username': cls.user.username}
            ),
            'post_detail': reverse(
                'posts:post_detail', kwargs={'post_id': cls.post.id}
            ),
            'create': reverse('posts:create'),
            'edit': reverse(
                'posts:edit', kwargs={'post_id': f'{cls.post.id}'}
            ),
            'another_group_list': reverse(
                'posts:group_list', kwargs={'slug': cls.another_group.slug}
            )
        }

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""

        templates_pages_names = {
            self.url_address_map['index']: 'posts/index.html',
            self.url_address_map['group_list']: 'posts/group_list.html',
            self.url_address_map['profile']: 'posts/profile.html',
            self.url_address_map['post_detail']: 'posts/post_detail.html',
            self.url_address_map['create']: 'posts/create.html',
            self.url_address_map['edit']: 'posts/create.html'
        }

        for reverse_name, template in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def check_context(self, post):
        self.assertEqual(post.text, self.post.text)
        self.assertEqual(post.author, self.post.author)
        self.assertEqual(post.group, self.post.group)

    def test_index_pages_show_correct_context(self):
        """Шаблон index сформирован с правильным контекстом."""
        response = self.authorized_client.get(self.url_address_map['index'])
        post = response.context['page_obj'][0]
        self.check_context(post)

    def test_group_posts_pages_show_correct_context(self):
        """Шаблон group_post сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            self.url_address_map['group_list']
        )
        post = response.context['page_obj'][0]
        self.check_context(post)
        group = response.context['group']
        self.assertEqual(group.slug, self.group.slug)

    def test_profile_pages_show_correct_context(self):
        """Шаблон group_post сформирован с правильным контекстом."""
        response = self.authorized_client.get(self.url_address_map['profile'])
        post = response.context['page_obj'][0]
        self.check_context(post)
        self.assertEqual(post.author, self.user)

    def test_post_detail_pages_show_correct_context(self):
        """Шаблон post_detail сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            self.url_address_map['post_detail']
        )
        post = response.context['post']
        self.check_context(post)

    def test_post_create_show_correct_context(self):
        """Шаблон post_create сформирован с правильным контекстом."""
        response = self.authorized_client.get(self.url_address_map['create'])
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_post_edit_show_correct_context(self):
        """Шаблон post_edit сформирован с правильным контекстом."""
        response = self.authorized_client.get(self.url_address_map['edit'])
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_post_doesnt_appear_in_another_group(self):
        """Проверка, что пост не попал в другую группу."""
        response = self.authorized_client.get(
            self.url_address_map['another_group_list']
        )
        posts = response.context['page_obj']
        self.assertEqual(len(posts), 0)


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='author')
        cls.group = Group.objects.create(slug='slug')
        cls.SECOND_PAGE_COUNT = 3
        posts_lst = []
        for i in range(POSTS_NUMBERS + cls.SECOND_PAGE_COUNT):
            posts_lst.append(
                Post(
                    text='Тут много-много-много текста :)',
                    author=cls.user,
                    group=cls.group,
                )
            )
        Post.objects.bulk_create(posts_lst)

        cls.url_address_lst = [
            reverse('posts:index'),
            reverse('posts:group_list', kwargs={'slug': cls.group.slug}),
            reverse('posts:profile', kwargs={'username': cls.user.username})
        ]

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_first_and_second_pages_contain_correct_records(self):
        for url_address in self.url_address_lst:
            response = self.client.get(url_address)
            self.assertEqual(
                len(response.context['page_obj']), POSTS_NUMBERS
            )
            response = self.client.get(url_address + '?page=2')
            self.assertEqual(
                len(response.context['page_obj']), self.SECOND_PAGE_COUNT
            )
