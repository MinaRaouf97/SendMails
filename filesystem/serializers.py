from dataclasses import fields
from pyexpat import model
from rest_framework import serializers
from .models import User, Files

class FileSerializer(serializers.ModelSerializer):
	class Meta:
		model = Files
		fields ='__all__'
  
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'
        
    def create(self, validated_data):
        password = validated_data.pop('password', None)
        instance = self.Meta.model(**validated_data)
        if password is not None:
            instance.set_password(password)
            
        instance.save()
        return instance