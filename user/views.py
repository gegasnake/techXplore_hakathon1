import requests
from rest_framework import status
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import AllowAny

from user.models import CustomUser
from user.serializers import RegisterSerializer
from techXplore_hakathon1.settings import CLOUDFLARE_SECRET_KEY
from rest_framework.response import Response


class RegisterView(CreateAPIView):
    queryset = CustomUser.objects.all()
    permission_classes = [AllowAny]
    serializer_class = RegisterSerializer

    def create(self, request, *args, **kwargs):
        captcha_response = request.data.get("cf-turnstile-response")
        data = {
            "secret": CLOUDFLARE_SECRET_KEY,
            "response": captcha_response
        }
        response = requests.post("https://challenges.cloudflare.com/turnstile/v0/siteverify", data=data)
        result = response.json()

        if not result.get("success"):
            return Response({"detail": "Invalid CAPTCHA."}, status=status.HTTP_400_BAD_REQUEST)

        return super().create(request, *args, **kwargs)




