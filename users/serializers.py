from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from users.models import Payment


class PhoneTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        # Меняем username на phone
        attrs['username'] = attrs.get('phone')
        return super().validate(attrs)


class PaymentsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = '__all__'
