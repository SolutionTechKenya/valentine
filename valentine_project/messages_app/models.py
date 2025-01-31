from django.db import models
from django.core.exceptions import ValidationError

class ValentineMessage(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('sent', 'Sent'),
        ('failed', 'Failed'),
    ]

    RELATIONSHIP_CHOICES = [
        ('girlfriend', 'Girlfriend'),
        ('boyfriend', 'Boyfriend'),
        ('spouse', 'Spouse'),
        ('crush', 'Crush'),
        ('friend', 'Friend'),
        ('colleague', 'Colleague'),
        ('boss', 'Boss'),
        ('friend_with_benefits', 'Friend With Benefits'),
    ]

    DELIVERY_METHOD_CHOICES = [
        ('email', 'Email Only'),
        ('whatsapp', 'WhatsApp Only'),
        ('email_whatsapp', 'Email and WhatsApp'),
    ]

    MESSAGE_TYPE_CHOICES = [
        ('generated', 'AI Generated'),
        ('custom', 'Custom Written'),
    ]

    sender_name = models.CharField(
        max_length=255,
        help_text="Name of the person sending the message"
    )

    email = models.EmailField(
        blank=True,
        null=True,
        help_text="Email address where the message will be sent"
    )

    phone_number = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        help_text="WhatsApp number in international format (e.g., +254XXXXXXXXX)"
    )

    phone_country = models.CharField(
        max_length=2,
        default='KE',
        help_text="ISO 3166-1 alpha-2 country code (e.g., KE, US, GB)"
    )

    delivery_method = models.CharField(
        max_length=20,
        choices=DELIVERY_METHOD_CHOICES,
        default='whatsapp',
        help_text="How the message should be delivered"
    )

    recipient_name = models.CharField(
        max_length=255,
        help_text="Name of the person receiving the message"
    )

    relationship = models.CharField(
        max_length=20,
        choices=RELATIONSHIP_CHOICES,
        help_text="Relationship with the recipient"
    )

    message_type = models.CharField(
        max_length=10,
        choices=MESSAGE_TYPE_CHOICES,
        default='generated',
        help_text="Type of message (AI generated or custom written)"
    )

    description = models.TextField(
        blank=True,
        null=True,
        help_text="What you love about the recipient (for generated messages)"
    )

    custom_message = models.TextField(
        blank=True,
        null=True,
        help_text="Custom written message"
    )

    generated_message = models.TextField(
        blank=True,
        null=True,
        help_text="AI-generated Valentine's message"
    )

    scheduled_for = models.DateTimeField(
        help_text="When the message should be sent"
    )

    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='pending',
        help_text="Current status of the message"
    )

    error_details = models.JSONField(
        null=True,
        blank=True,
        help_text="Detailed error information if sending failed"
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="When the message was created"
    )

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', 'scheduled_for']),
            models.Index(fields=['created_at']),
        ]

    def clean(self):
        """Validate message delivery requirements."""
        super().clean()
        
        if 'whatsapp' in self.delivery_method:
            if not self.phone_number:
                raise ValidationError({'phone_number': "WhatsApp number is required for WhatsApp delivery."})
            if not self.phone_number.startswith('+'):
                raise ValidationError({'phone_number': "WhatsApp number must include country code (e.g., +254XXXXXXXXX)."})
        
        if 'email' in self.delivery_method and not self.email:
            raise ValidationError({'email': "Email address is required for email delivery."})

        # Validate message type requirements
        if self.message_type == 'generated' and not self.description:
            raise ValidationError({'description': "Description is required for generated messages."})
        elif self.message_type == 'custom' and not self.custom_message:
            raise ValidationError({'custom_message': "Custom message is required for custom message type."})

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Message from {self.sender_name} to {self.recipient_name}"

    @property
    def is_sent(self):
        return self.status == 'sent'

    @property
    def is_pending(self):
        return self.status == 'pending'

    @property
    def is_failed(self):
        return self.status == 'failed'

    @property
    def send_email(self):
        return 'email' in self.delivery_method

    @property
    def send_whatsapp(self):
        return 'whatsapp' in self.delivery_method


class PremiumServiceRequest(models.Model):
    STATUS_CHOICES = [
        ('new', 'New'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled')
    ]

    request_description = models.TextField(
        help_text="Description of the special service requested"
    )

    contact_number = models.CharField(
        max_length=20,
        help_text="Contact number of the requester"
    )

    status = models.CharField(
        max_length=15,
        choices=STATUS_CHOICES,
        default='new',
        help_text="Current status of the premium service request"
    )

    admin_notes = models.TextField(
        blank=True,
        null=True,
        help_text="Internal notes for administrators"
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="When the request was created"
    )

    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="When the request was last updated"
    )

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return f"Premium Request #{self.id} - {self.status}"