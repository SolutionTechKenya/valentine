from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.renderers import JSONRenderer
from rest_framework.permissions import AllowAny
from django.http import HttpResponse
from .models import ValentineMessage, PremiumServiceRequest
from .serializers import ValentineMessageSerializer, PremiumServiceRequestSerializer
from .tasks import generate_and_schedule_message
from datetime import datetime
import pytz
import logging
import random

logger = logging.getLogger(__name__)

class PremiumRequestViewSet(viewsets.ModelViewSet):
    queryset = PremiumServiceRequest.objects.all()
    serializer_class = PremiumServiceRequestSerializer

class ValentineMessageViewSet(viewsets.ModelViewSet):
    queryset = ValentineMessage.objects.all()
    serializer_class = ValentineMessageSerializer
    permission_classes = [AllowAny]
    renderer_classes = [JSONRenderer]

    templates = {
        'spouse': [
            "My beloved {recipient_name},💖\n\n"
            "After all our time together, my love for you only grows stronger. 🌹\n"
            "{description}\n\n"
            "You are my soulmate, my best friend, and my everything. 💑\n"
            "Thank you for being the most amazing spouse.\n\n"
            "HAPPY VALENTINE'S DAY! 💕\n\n"
            "Forever yours,\n{sender_name}",
        ]
    }

    def _generate_template_message(self, sender_name, recipient_name, relationship, description):
        try:
            relationship_templates = self.templates.get(relationship.lower(), self.templates['spouse'])
            template = random.choice(relationship_templates)
            message = template.format(
                sender_name=sender_name,
                recipient_name=recipient_name,
                description=description
            )
            return message
        except Exception as e:
            logger.error(f"Error generating template message: {str(e)}")
            return (
                f"Dear {recipient_name},\n\n"
                f"Happy Valentine's Day! {description}\n\n"
                f"With love,\n{sender_name}"
            )

    def create(self, request, *args, **kwargs):
        try:
            logger.debug(f"Incoming request data: {request.data}")
            valentines_day = datetime(2025, 2, 14, 12, 0, 0, tzinfo=pytz.UTC)
            data = request.data.copy()
            data['scheduled_for'] = valentines_day

            try:
                generated_message = self._generate_template_message(
                    data['sender_name'],
                    data['recipient_name'],
                    data['relationship'],
                    data['description']
                )
                data['generated_message'] = generated_message
                logger.info("Successfully generated Valentine's message using template")
            except Exception as e:
                logger.error(f"Error generating message with template: {e}")
                data['generated_message'] = (
                    f"Dear {data['recipient_name']},\n\n"
                    f"Happy Valentine's Day!\n\n"
                    f"With love,\n{data['sender_name']}"
                )

            logger.debug(f"Modified data: {data}")
            serializer = self.get_serializer(data=data)

            if not serializer.is_valid():
                logger.error(f"Serializer validation errors: {serializer.errors}")
                return Response({
                    "message": "Validation failed",
                    "errors": serializer.errors
                }, status=400)

            message = serializer.save()
            logger.info(f"Successfully created message with ID: {message.id}")
            generate_and_schedule_message.delay(message.id)
            logger.info(f"Scheduled message processing task for message ID: {message.id}")

            return Response({
                "message": "Valentine message scheduled successfully",
                "data": serializer.data,
                "preview": data['generated_message']
            }, status=201)

        except Exception as e:
            logger.error(f"Error creating message: {str(e)}", exc_info=True)
            return Response({
                "message": str(e),
                "type": str(type(e).__name__)
            }, status=500)
