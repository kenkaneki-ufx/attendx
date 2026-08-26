from django.contrib.auth import get_user_model
from django.core import mail
from django.core.cache import cache
from django.test import TestCase, override_settings
from django.urls import reverse

from apps.accounts.services import AuthService

Faculty = get_user_model()


class LoginViewTest(TestCase):
    """Tests for the login view."""

    def setUp(self):
        cache.clear()  # isolate login rate-limit state between tests
        self.login_url = reverse('accounts:login')
        self.faculty = Faculty.objects.create_user(
            username='testuser', email='test@test.com',
            password='testpass123', first_name='Test', last_name='User',
            employee_id='TST001'
        )

    def test_login_page_loads(self):
        """Test login page loads correctly."""
        response = self.client.get(self.login_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Login')

    def test_login_success(self):
        """Test successful login redirects to dashboard."""
        response = self.client.post(self.login_url, {
            'username': 'testuser',
            'password': 'testpass123',
        })
        self.assertEqual(response.status_code, 302)
        self.assertIn('/dashboard/', response.url)
        self.assertTrue(response.wsgi_request.user.is_authenticated)

    def test_login_failure(self):
        """Test failed login shows error and does not authenticate."""
        response = self.client.post(self.login_url, {
            'username': 'testuser',
            'password': 'wrongpass',
        })
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.wsgi_request.user.is_authenticated)

    def test_authenticated_redirect(self):
        """Test authenticated user is redirected from login."""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(self.login_url)
        self.assertEqual(response.status_code, 302)

    def test_successful_login_clears_attempts(self):
        """A successful login resets the failure counter for the IP."""
        AuthService.record_failed_login('127.0.0.1')
        self.assertEqual(AuthService.get_attempts('127.0.0.1'), 1)
        self.client.post(self.login_url, {
            'username': 'testuser',
            'password': 'testpass123',
        })
        self.assertEqual(AuthService.get_attempts('127.0.0.1'), 0)


class LoginRateLimitTest(TestCase):
    """Tests for brute-force rate limiting on login."""

    def setUp(self):
        cache.clear()  # isolate login rate-limit state between tests
        self.login_url = reverse('accounts:login')
        self.faculty = Faculty.objects.create_user(
            username='testuser', email='test@test.com',
            password='testpass123', first_name='Test', last_name='User',
            employee_id='TST001'
        )

    @override_settings(ATTENDX_MAX_LOGIN_ATTEMPTS=3)
    def test_lockout_after_max_failed_attempts(self):
        """Login is blocked after exceeding the failure threshold."""
        for _ in range(3):
            self.client.post(self.login_url, {
                'username': 'testuser',
                'password': 'wrongpass',
            })

        # Middleware should now redirect away from login for this IP.
        response = self.client.post(self.login_url, {
            'username': 'testuser',
            'password': 'testpass123',
        })
        self.assertEqual(response.status_code, 302)
        self.assertIn('/accounts/login/', response.url)
        self.assertTrue(AuthService.is_locked_out('127.0.0.1'))

    @override_settings(ATTENDX_MAX_LOGIN_ATTEMPTS=3)
    def test_lockout_blocks_valid_credentials(self):
        """Even valid credentials are rejected while locked out."""
        for _ in range(3):
            self.client.post(self.login_url, {
                'username': 'testuser',
                'password': 'wrongpass',
            })
        response = self.client.post(self.login_url, {
            'username': 'testuser',
            'password': 'testpass123',
        })
        self.assertEqual(response.status_code, 302)
        self.assertFalse(response.wsgi_request.user.is_authenticated)


class LogoutViewTest(TestCase):
    """Tests for the logout view."""

    def setUp(self):
        self.faculty = Faculty.objects.create_user(
            username='testuser', email='test@test.com',
            password='testpass123', first_name='Test', last_name='User',
            employee_id='TST001'
        )

    def test_logout_post(self):
        """POST logout logs out and redirects to login."""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post(reverse('accounts:logout'))
        self.assertEqual(response.status_code, 302)
        self.assertIn('/accounts/login/', response.url)
        self.assertFalse(response.wsgi_request.user.is_authenticated)

    def test_logout_requires_post(self):
        """GET logout is rejected (CSRF-safe POST only)."""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('accounts:logout'))
        self.assertEqual(response.status_code, 405)
        self.assertTrue(response.wsgi_request.user.is_authenticated)


class ProfileViewTest(TestCase):
    """Tests for the profile view."""

    def setUp(self):
        self.faculty = Faculty.objects.create_user(
            username='testuser', email='test@test.com',
            password='testpass123', first_name='Test', last_name='User',
            employee_id='TST001'
        )

    def test_profile_requires_login(self):
        """Profile requires authentication."""
        response = self.client.get(reverse('accounts:profile'))
        self.assertEqual(response.status_code, 302)

    def test_profile_loads_for_authenticated(self):
        """Profile loads for authenticated user."""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('accounts:profile'))
        self.assertEqual(response.status_code, 200)

    def test_profile_update(self):
        """Profile edit persists changes."""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post(reverse('accounts:profile'), {
            'first_name': 'Updated',
            'last_name': 'User',
            'email': 'test@test.com',
            'phone': '9876543210',
        })
        self.assertEqual(response.status_code, 302)
        self.faculty.refresh_from_db()
        self.assertEqual(self.faculty.first_name, 'Updated')
        self.assertEqual(self.faculty.phone, '9876543210')


class ChangePasswordViewTest(TestCase):
    """Tests for the change password view."""

    def setUp(self):
        self.faculty = Faculty.objects.create_user(
            username='testuser', email='test@test.com',
            password='testpass123', first_name='Test', last_name='User',
            employee_id='TST001'
        )

    def _post(self, old, new, confirm):
        return self.client.post(reverse('accounts:change_password'), {
            'old_password': old,
            'new_password': new,
            'confirm_password': confirm,
        })

    def test_change_password_success(self):
        """Correct old password changes to the new one."""
        self.client.login(username='testuser', password='testpass123')
        response = self._post('testpass123', 'newpass456', 'newpass456')
        self.assertEqual(response.status_code, 302)
        self.faculty.refresh_from_db()
        self.assertTrue(self.faculty.check_password('newpass456'))

    def test_change_password_wrong_old(self):
        """Wrong old password is rejected."""
        self.client.login(username='testuser', password='testpass123')
        response = self._post('wrongold', 'newpass456', 'newpass456')
        self.assertEqual(response.status_code, 200)
        self.faculty.refresh_from_db()
        self.assertTrue(self.faculty.check_password('testpass123'))

    def test_change_password_mismatch(self):
        """Mismatched confirmation is rejected."""
        self.client.login(username='testuser', password='testpass123')
        response = self._post('testpass123', 'newpass456', 'different789')
        self.assertEqual(response.status_code, 200)
        self.faculty.refresh_from_db()
        self.assertTrue(self.faculty.check_password('testpass123'))


class ForgotPasswordViewTest(TestCase):
    """Tests for the forgot password flow."""

    def setUp(self):
        self.faculty = Faculty.objects.create_user(
            username='testuser', email='test@test.com',
            password='testpass123', first_name='Test', last_name='User',
            employee_id='TST001'
        )
        self.url = reverse('accounts:forgot_password')

    def test_forgot_password_page_loads(self):
        """Forgot password page renders."""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_forgot_password_sends_email(self):
        """A reset email is sent for a known account."""
        response = self.client.post(self.url, {'email': 'test@test.com'})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn('reset', mail.outbox[0].subject.lower())
        self.assertIn('reset-password', mail.outbox[0].body)

    def test_forgot_password_unknown_email_no_leak(self):
        """Unknown emails get the same generic response (no enumeration)."""
        response = self.client.post(self.url, {'email': 'nobody@nowhere.com'})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(len(mail.outbox), 0)


class ResetPasswordViewTest(TestCase):
    """Tests for the password reset completion flow."""

    def setUp(self):
        self.faculty = Faculty.objects.create_user(
            username='testuser', email='test@test.com',
            password='testpass123', first_name='Test', last_name='User',
            employee_id='TST001'
        )

    def _reset_url(self):
        uidb64, token = AuthService.get_reset_link(self.faculty)
        return reverse('accounts:reset_password', kwargs={'uidb64': uidb64, 'token': token})

    def test_reset_password_success(self):
        """Valid token + matching passwords resets the password."""
        url = self._reset_url()
        response = self.client.post(url, {
            'new_password': 'brandnew789',
            'confirm_password': 'brandnew789',
        })
        self.assertEqual(response.status_code, 302)
        self.assertIn('/accounts/login/', response.url)
        self.faculty.refresh_from_db()
        self.assertTrue(self.faculty.check_password('brandnew789'))

    def test_reset_password_invalid_token(self):
        """An invalid token is rejected and the password is unchanged."""
        uidb64, _ = AuthService.get_reset_link(self.faculty)
        url = reverse('accounts:reset_password', kwargs={'uidb64': uidb64, 'token': 'bad-token'})
        response = self.client.post(url, {
            'new_password': 'brandnew789',
            'confirm_password': 'brandnew789',
        })
        self.assertEqual(response.status_code, 302)
        self.faculty.refresh_from_db()
        self.assertTrue(self.faculty.check_password('testpass123'))

    def test_reset_password_unknown_user(self):
        """A reset link for a non-existent user is rejected."""
        url = reverse('accounts:reset_password', kwargs={'uidb64': 'abc123', 'token': 'token'})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)

    def test_reset_password_mismatch(self):
        """Mismatched confirmation passwords are rejected."""
        url = self._reset_url()
        response = self.client.post(url, {
            'new_password': 'brandnew789',
            'confirm_password': 'different999',
        })
        self.assertEqual(response.status_code, 200)
        self.faculty.refresh_from_db()
        self.assertTrue(self.faculty.check_password('testpass123'))
