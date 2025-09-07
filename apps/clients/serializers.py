from rest_framework import serializers
from .models import Client, ClientSite, ClientDocument


class ClientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Client
        fields = '__all__'


class ClientSiteSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClientSite
        fields = '__all__'


class ClientDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClientDocument
        fields = '__all__'
