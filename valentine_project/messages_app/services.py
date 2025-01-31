from django.core.mail import send_mail, BadHeaderError, get_connection
from django.conf import settings
import logging
import re
from email.utils import parseaddr

logger = logging.getLogger(__name__)

class EmailService:
    @staticmethod
    def validate_email(email):
        """Validate email format"""
        if not email:
            return False
        parsed_email = parseaddr(email)[1]
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, parsed_email))

    @staticmethod
    def validate_message_content(subject, body):
        """Validate message content"""
        if not subject:
            logger.error("Email validation failed: Empty subject")
            return False
        if not body:
            logger.error("Email validation failed: Empty body")
            return False
        if '\n' in subject or '\r' in subject:
            logger.error("Email validation failed: Potential header injection detected in subject")
            return False
        return True

    @staticmethod
    def send_valentine_email(recipient_email, recipient_name, message, is_custom=False):
        """Send Valentine's message via email with comprehensive error logging"""
        try:
            # Input validation with detailed logging
            if not recipient_email:
                error_msg = "Email validation failed: Empty recipient email"
                logger.error(error_msg)
                return False, error_msg

            if not recipient_name:
                error_msg = "Email validation failed: Empty recipient name"
                logger.error(error_msg)
                return False, error_msg

            if not message:
                error_msg = "Email validation failed: Empty message content"
                logger.error(error_msg)
                return False, error_msg

            if not EmailService.validate_email(recipient_email):
                error_msg = f"Email validation failed: Invalid format for {recipient_email}"
                logger.error(error_msg)
                return False, error_msg

            # Test SMTP connection before sending
            connection = get_connection()
            try:
                connection.open()
                logger.info("SMTP connection test successful")
            except Exception as e:
                error_msg = f"SMTP connection test failed: {str(e)}"
                logger.error(error_msg)
                return False, error_msg
            finally:
                connection.close()

            subject = f"❤️ A Special Valentine's Message for {recipient_name} ❤️"
            
            # Different email template for custom messages
            if is_custom:
                email_body = (
                    f"Dear {recipient_name},\n\n"
                    f"Someone special has written you a personal Valentine's message:\n\n"
                    f"{message}\n\n"
                    f"Happy Valentine's Day! 🌹\n\n"
                    f"Sent with love ❤️"
                )
            else:
                email_body = (
                    f"Dear {recipient_name},\n\n"
                    f"Someone special has sent you a Valentine's message:\n\n"
                    f"{message}\n\n"
                    f"Happy Valentine's Day! 🌹\n\n"
                    f"Sent with love ❤️"
                )

            if not EmailService.validate_message_content(subject, email_body):
                error_msg = "Message content validation failed"
                logger.error(error_msg)
                return False, error_msg

            # Send email
            sent = send_mail(
                subject=subject,
                message=email_body,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[recipient_email],
                fail_silently=False,
            )

            if not sent:
                error_msg = f"Email delivery failed for {recipient_email}"
                logger.error(error_msg)
                return False, error_msg

            logger.info(f"Valentine email sent successfully to {recipient_email}")
            return True, None

        except BadHeaderError as e:
            error_msg = f"Email header validation error: {str(e)}"
            logger.error(error_msg)
            return False, error_msg

        except Exception as e:
            error_msg = f"Unexpected error sending Valentine email: {str(e)}"
            logger.error(error_msg, exc_info=True)
            return False, error_msg

    @staticmethod
    def send_premium_request_notification(request):
        """Send notification to admins about new premium service request"""
        try:
            subject = f"New Premium Service Request #{request.id}"
            message = (
                f"A new premium service request has been received:\n\n"
                f"Contact Number: {request.contact_number}\n"
                f"Request Description:\n{request.request_description}\n\n"
                f"Please check the admin panel for more details and to process this request."
            )

            if not EmailService.validate_message_content(subject, message):
                error_msg = "Admin notification content validation failed"
                logger.error(error_msg)
                return False, error_msg

            sent = send_mail(
                subject=subject,
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[admin[1] for admin in settings.ADMINS],
                fail_silently=False,
            )

            if not sent:
                error_msg = "Failed to send admin notification"
                logger.error(error_msg)
                return False, error_msg

            logger.info(f"Admin notification sent for premium request #{request.id}")
            return True, None

        except Exception as e:
            error_msg = f"Error sending admin notification: {str(e)}"
            logger.error(error_msg, exc_info=True)
            return False, error_msg


class ValentineMessageSender:
    def __init__(self):
        self.email_service = EmailService()

    def send_message(self, valentine_message):
        """Send Valentine's message through email"""
        if not valentine_message:
            logger.error("No valentine message provided")
            return {'success': False, 'error': 'No message provided'}

        if not valentine_message.email:
            error_msg = "No email address provided"
            logger.warning("Email sending skipped: No email address provided")
            return {'success': False, 'error': error_msg}

        # Determine message content based on message type
        message_content = (
            valentine_message.custom_message 
            if valentine_message.message_type == 'custom' 
            else valentine_message.generated_message
        )

        success, error = self.email_service.send_valentine_email(
            valentine_message.email,
            valentine_message.recipient_name,
            message_content,
            is_custom=(valentine_message.message_type == 'custom')
        )

        logger.info(f"Message delivery completed - Success: {success}")
        return {'success': success, 'error': error}