from django.core.management.base import BaseCommand
from django.utils import timezone
from messages_app.models import ValentineMessage
from messages_app.services import ValentineMessageSender
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Send scheduled Valentine\'s messages'

    def handle(self, *args, **kwargs):
        now = timezone.now()
        
        # Get all pending messages scheduled for sending
        messages = ValentineMessage.objects.filter(
            status='pending',
            scheduled_for__lte=now
        )

        sender = ValentineMessageSender()
        
        for message in messages:
            try:
                logger.info(f"Processing Valentine message ID: {message.id}")
                
                # Send the message
                result = sender.send_message(message)
                
                # Update message status based on results
                if result['email'] or result['sms']:
                    message.status = 'sent'
                    success_methods = []
                    if result['email']:
                        success_methods.append('email')
                    if result['sms']:
                        success_methods.append('SMS')
                    logger.info(f"Message ID {message.id} sent successfully via {', '.join(success_methods)}")
                else:
                    message.status = 'failed'
                    logger.error(f"Message ID {message.id} failed to send via any method")
                
                message.save()
                
            except Exception as e:
                logger.error(f"Error processing message ID {message.id}: {str(e)}")
                message.status = 'failed'
                message.save()

        self.stdout.write(
            self.style.SUCCESS(f'Processed {messages.count()} Valentine messages')
        )