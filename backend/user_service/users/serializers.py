from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.validators import RegexValidator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
import os
import certifi
from rest_framework import serializers
from django.db.models import Avg
logger = logging.getLogger(__name__)

User = get_user_model()
os.environ['SSL_CERT_FILE'] = certifi.where()

class UserSerializer(serializers.ModelSerializer):
    roles = serializers.ListField(child=serializers.ChoiceField(choices=User.ROLE_CHOICES), required=False)

    class Meta:
        model = User
        fields = ['id', 'username', 'surname', 'email', 'roles']