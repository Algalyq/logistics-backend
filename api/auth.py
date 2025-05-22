from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.response import Response

class CustomAuthToken(ObtainAuthToken):
    """
    Custom token view that includes the user role in the response
    """
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        
        token, created = Token.objects.get_or_create(user=user)
        
        # Role is now directly on the user model
        role = user.role
        return Response({
            'token': token.key,
            'user_id': user.pk,
            'email': user.email,
            'role': role,
            'username': user.username,
            'first_name': user.first_name,
            'last_name': user.last_name
        })
