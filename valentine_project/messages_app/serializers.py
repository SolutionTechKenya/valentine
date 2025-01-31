from rest_framework import serializers
from .models import ValentineMessage, PremiumServiceRequest

class ValentineMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ValentineMessage
        fields = '__all__'
        
    def validate(self, data):
        print(f"Validating data: {data}")  # Debug print
        return data

class PremiumServiceRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = PremiumServiceRequest
        fields = '__all__'  # Include all model fields