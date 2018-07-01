from rest_framework import serializers

from core.models import OfficeSpace


class OfficeSpaceSerializer(serializers.ModelSerializer):
    """ TODO: provide Meta """
    class Meta:
        model = OfficeSpace
        fields = '__all__'
