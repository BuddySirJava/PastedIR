from rest_framework import serializers

from website.models import Language, Paste


class LanguageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Language
        fields = '__all__'

class PasteSerializer(serializers.ModelSerializer):
    lang = LanguageSerializer()
    class Meta:
        model = Paste
        fields = ['id', 'created', 'lang']

