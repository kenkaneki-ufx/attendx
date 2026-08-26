from django.db import models
from django.utils import timezone
import secrets


class QRCodeSession(models.Model):
    """QR Code Session model for tracking QR code generation and expiry."""
    lecture = models.ForeignKey(
        'lectures.Lecture',
        on_delete=models.CASCADE,
        related_name='qr_sessions'
    )
    token = models.CharField(max_length=64, unique=True)
    secret_key = models.CharField(max_length=128)
    qr_image_path = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    is_active = models.BooleanField(default=True)
    regeneration_count = models.SmallIntegerField(default=0)

    class Meta:
        verbose_name = 'QR Code Session'
        verbose_name_plural = 'QR Code Sessions'
        ordering = ['-created_at']

    def __str__(self):
        return f"QR Session for {self.lecture} (Token: {self.token[:8]}...)"

    @classmethod
    def generate_token(cls):
        """Generate a cryptographically secure token."""
        return secrets.token_urlsafe(32)

    @classmethod
    def generate_secret(cls):
        """Generate a secret key for additional security."""
        return secrets.token_hex(64)

    @classmethod
    def create_session(cls, lecture, expiry_seconds=60):
        """Create a new QR code session for a lecture."""
        # Deactivate any existing active sessions for this lecture
        cls.objects.filter(lecture=lecture, is_active=True).update(is_active=False)

        token = cls.generate_token()
        secret = cls.generate_secret()
        expires_at = timezone.now() + timezone.timedelta(seconds=expiry_seconds)

        session = cls.objects.create(
            lecture=lecture,
            token=token,
            secret_key=secret,
            expires_at=expires_at,
            is_active=True
        )
        return session

    def is_expired(self):
        """Check if the QR code session has expired."""
        return timezone.now() > self.expires_at

    def deactivate(self):
        """Deactivate the QR code session."""
        self.is_active = False
        self.save(update_fields=['is_active'])

    def regenerate(self, expiry_seconds=60):
        """Regenerate the QR code session with new token."""
        self.deactivate()
        new_session = QRCodeSession.create_session(
            self.lecture, expiry_seconds
        )
        new_session.regeneration_count = self.regeneration_count + 1
        new_session.save(update_fields=['regeneration_count'])
        return new_session

    def get_absolute_url(self):
        return f"/qr/session/{self.pk}/"
