"""
    user input data will be haldled after validation.
    forms.py helps to validate the data more safely 
"""

from django.forms import ModelForm
from .models import Room

class RoomForm(ModelForm):
    class Meta:
        model = Room
        fields = '__all__'