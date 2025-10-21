from django.test import TestCase
from django.urls import reverse
from lessons.models import CustomUser
from django.contrib.auth.models import Group
from lessons.forms import EditAdminForm


class AdminListTest(TestCase):
    fixtures = ['lessons/tests/fixtures/default_user.json', 'lessons/tests/fixtures/other_users.json']

    def setUp(self):
        self.url = reverse('admin_list')
        self.user = CustomUser.objects.get(email='johndoe@example.org')
        director, created = Group.objects.get_or_create(name='Director')
        director.user_set.add(self.user)
        self.other_user = CustomUser.objects.get(email="janedoe@example.org")
        admin, created = Group.objects.get_or_create(name='Admin')
        admin.user_set.add(self.other_user)
        self.toggle_admin = {'super_admin': self.other_user.email}
        self.remove = {'delete': self.other_user.email}
        self.edit = {'edit': self.other_user.email}

    def test_admin_list_url(self):
        self.assertEqual(self.url, '/director/')

    def test_get_admin_list_with_valid_id(self):
        self.client.login(email=self.user.email, password='Password123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'admin_list.html')

    def test_get_admin_list_with_invalid_id(self):
        self.client.login(email=self.other_user.email, password='Password123')
        response = self.client.get(self.url)
        redirect_url = reverse('administrators')
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_get_admin_list_redirects_when_not_logged_in(self):
        redirect_url = reverse('log_in')
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_get_admin_list_shows_only_admins(self):
        self.client.login(email=self.user.email, password='Password123')
        self._create_test_admins(0, 10)
        self._create_test_users(11, 15)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'admin_list.html')
        self.assertEqual(len(response.context['admin']), 10+1)
        for user_id in range(0,10):
            self.assertContains(response, f'user{user_id}@test.org')
            self.assertContains(response, f'First{user_id}')
            self.assertContains(response, f'Last{user_id}')
            user = CustomUser.objects.get(email=f'user{user_id}@test.org')

    def test_edit_admin(self):
        self.client.login(email = self.user.email, password='Password123')
        response = self.client.post(self.url, self.edit, follow = True)
        response_url = reverse('edit_user', kwargs={'user_id': self.other_user.id})
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'edit_user.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, EditAdminForm))

    def test_delete_admin(self):
        self.client.login(email = self.user.email, password='Password123')
        users_before = CustomUser.objects.count()
        response = self.client.post(self.url, self.remove, follow = True)
        users_after = CustomUser.objects.count()
        response_url = reverse('admin_list')
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'admin_list.html')
        self.assertEqual(users_before, users_after+1)

    def test_make_super_admin(self):
        self.client.login(email = self.user.email, password='Password123')
        response = self.client.post(self.url, self.toggle_admin, follow = True)
        response_url = reverse('admin_list')
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'admin_list.html')
        self.assertTrue(self.other_user.groups.filter(name = "Director").exists())

    def test_remove_super_admin(self):
        self.client.login(email = self.user.email, password='Password123')
        director, created = Group.objects.get_or_create(name='Director')
        director.user_set.add(self.other_user)
        response = self.client.post(self.url, self.toggle_admin, follow = True)
        response_url = reverse('admin_list')
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'admin_list.html')
        self.assertFalse(self.other_user.groups.filter(name = "Director").exists())

    def _create_test_admins(self, start, user_count):
        for user_id in range(start, user_count):
            new_admin = CustomUser.objects.create_user(email=f'user{user_id}@test.org',
                                                       password='Password123',
                                                       first_name=f'First{user_id}',
                                                       last_name=f'Last{user_id}',
                                                       )
            admin, created = Group.objects.get_or_create(name='Admin')
            admin.user_set.add(new_admin)

    def _create_test_users(self, start, user_count):
        for user_id in range(start, user_count):
            new_admin = CustomUser.objects.create_user(email=f'user{user_id}@test.org',
                                                       password='Password123',
                                                       first_name=f'First{user_id}',
                                                       last_name=f'Last{user_id}',
                                                       )
