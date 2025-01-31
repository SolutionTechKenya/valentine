from celery import shared_task
from django.utils import timezone
from .models import ValentineMessage
from .services import ValentineMessageSender
import logging
import json
import traceback

logger = logging.getLogger(__name__)

@shared_task(bind=True)
def send_scheduled_messages(self):
    """Periodic task to check and send scheduled messages via email"""
    try:
        current_time = timezone.now()
        logger.info(f"[Celery Task] Checking for pending messages at {current_time}")
        
        # Get pending messages that are due
        pending_messages = ValentineMessage.objects.filter(
            status='pending',
            scheduled_for__lte=current_time
        )
        
        if not pending_messages.exists():
            logger.info("[Celery Task] No pending messages found for current time.")
            return "No pending messages found for current time."
        
        message_count = pending_messages.count()
        logger.info(f"[Celery Task] Found {message_count} pending messages to send.")
        
        for message in pending_messages:
            try:
                logger.info(f"[Celery Task] Processing message {message.id} scheduled for {message.scheduled_for}")
                message.status = 'processing'
                message.save(update_fields=["status"])
                
                # Queue the message for immediate processing
                generate_and_schedule_message.apply_async(
                    args=[message.id],
                    countdown=0
                )
            except Exception as e:
                logger.error(f"[Celery Task] Error queueing message {message.id}: {str(e)}")
                message.status = 'failed'
                message.error_details = {
                    'error': str(e),
                    'stage': 'queueing',
                    'timestamp': timezone.now().isoformat(),
                    'traceback': traceback.format_exc()
                }
                message.save(update_fields=["status", "error_details"])
        
        return f"{message_count} messages scheduled for sending."
    
    except Exception as e:
        logger.error(f"[Celery Task] Failed to execute scheduled messages: {str(e)}", exc_info=True)
        return f"Error: {str(e)}"

@shared_task(bind=True)
def generate_and_schedule_message(self, message_id):
    """Generate and send a scheduled Valentine message via email."""
    message = None
    try:
        # Fetch and validate the message
        message = ValentineMessage.objects.get(id=message_id)
        
        # Log initial state
        logger.info(f"Starting to process message {message_id} - Current status: {message.status}")
        
        if message.status != "processing":
            logger.warning(f"Message {message_id} is not in processing status. Current status: {message.status}")
            return False
        
        # Validate email requirement for email delivery
        if message.send_email and not message.email:
            logger.error(f"Message {message_id} requires email delivery but has no email address")
            message.status = 'failed'
            message.error_details = {
                'error': 'No email address provided for email delivery',
                'timestamp': timezone.now().isoformat(),
                'stage': 'validation'
            }
            message.save(update_fields=["status", "error_details"])
            return False
        
        # Validate WhatsApp requirement for WhatsApp delivery
        if message.send_whatsapp and not message.phone_number:
            logger.error(f"Message {message_id} requires WhatsApp delivery but has no phone number")
            message.status = 'failed'
            message.error_details = {
                'error': 'No phone number provided for WhatsApp delivery',
                'timestamp': timezone.now().isoformat(),
                'stage': 'validation'
            }
            message.save(update_fields=["status", "error_details"])
            return False
        
        # Log message details
        logger.info(f"""
        Processing valentine message:
        ID: {message.id}
        Email: {message.email}
        Phone: {message.phone_number}
        Recipient: {message.recipient_name}
        Delivery Method: {message.delivery_method}
        Message Length: {len(message.generated_message) if message.generated_message else 0}
        Scheduled For: {message.scheduled_for}
        Current Status: {message.status}
        """)
            
        # Send the message
        sender = ValentineMessageSender()
        result = sender.send_message(message)
        
        # Log the raw result
        logger.info(f"Send result for message {message_id}: {json.dumps(result, indent=2)}")
        
        # Extract success status and error details
        success = result.get('success', False)
        error = result.get('error')
        
        logger.info(f"Success value for message {message_id}: {success}, type: {type(success)}")
        
        # Update message status based on success
        if success is True:
            logger.info(f"Message {message_id} sent successfully - Updating status to 'sent'")
            message.status = "sent"
            message.error_details = None
            message.save(update_fields=["status", "error_details"])
            logger.info(f"Status successfully updated to 'sent' for message {message_id}")
        else:
            logger.warning(f"Message {message_id} delivery failed - Result: {result}")
            message.status = "failed"
            message.error_details = {
                'error': error or "Unknown error occurred",
                'timestamp': timezone.now().isoformat(),
                'stage': 'delivery',
                'result': result
            }
            message.save(update_fields=["status", "error_details"])
            logger.info(f"Status updated to 'failed' for message {message_id}")
        
        logger.info(f"Message {message_id} processing completed - Final Status: {message.status}")
        return success
    
    except ValentineMessage.DoesNotExist:
        logger.error(f"Message {message_id} does not exist!")
        return False
    
    except Exception as e:
        error_msg = f"Error processing message {message_id}: {str(e)}"
        logger.error(error_msg, exc_info=True)
        
        if message:
            try:
                message.status = 'failed'
                message.error_details = {
                    'error': str(e),
                    'type': type(e).__name__,
                    'timestamp': timezone.now().isoformat(),
                    'stage': 'processing',
                    'traceback': traceback.format_exc()
                }
                message.save(update_fields=["status", "error_details"])
                logger.info(f"Status updated to 'failed' for message {message_id} due to processing error")
            except Exception as save_error:
                logger.error(f"Failed to update message status: {str(save_error)}", exc_info=True)
        
        return False