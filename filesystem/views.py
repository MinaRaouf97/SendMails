from email.message import EmailMessage
from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.parsers import JSONParser
import os

from .serializers import UserSerializer, FileSerializer
from .models import User,Files
from django.views import View

from django.contrib.auth import authenticate, login
from rest_framework.decorators import permission_classes

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import AuthenticationFailed

from django.conf import settings
from django.http import HttpResponse, Http404

from django.contrib.sites.shortcuts import get_current_site

from .utils import account_activation_token
from django.urls import reverse
from django.core.mail import EmailMessage
from django.utils.encoding import force_bytes, force_str, DjangoUnicodeDecodeError
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode

from rest_framework import status


from django.shortcuts import render, redirect

from upload_validator import FileTypeValidator
import magic

# Create your views here.


#register API
class RegisterView(APIView):
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        instance = serializer.save()
        instance_id = instance.id
        current_site = get_current_site(request)
        email_body = {
                    'user': instance,
                    'domain': current_site.domain,
                    'uid': urlsafe_base64_encode(force_bytes(instance_id)),
                    'token': account_activation_token.make_token(instance),
                }

        link = reverse('activate', kwargs={
                    'uidb64': email_body['uid'], 'token': email_body['token']})
        print(link)

        email_subject = 'Activate your account'

        activate_url = 'http://'+current_site.domain+link
        
        print(activate_url)


        email = EmailMessage(
                    email_subject,
                    'Hi '+instance.username + ', Please the link below to activate your account \n'+activate_url,
                    'noreply@semycolon.com',
                    [instance.email],
                )

        print(instance.email)
        
        email.send(fail_silently=False)
        
        return Response(serializer.data)
    
class VerificationView(View):
    def get(self, request, uidb64, token):
        try:
            id = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=id)

            if not account_activation_token.check_token(user, token):
                return redirect('login'+'?message='+'User already activated')

            if user.is_login_activated:
                return redirect('login')
            user.is_active = True
            user.is_login_activated = True
            
            user.save()

            return redirect('login')

        except Exception as ex:
            pass

        return redirect('login')

#sign up page
def signUpPage(request):
    return render(request,'signUp.html')

    
#Login API
class LoginView(APIView):
    def post(self, request):
        email = request.data['email']
        password = request.data['password']
        username = request.data['username']

        user = User.objects.filter(email=email).first()

        if user is None:
            raise AuthenticationFailed('User not found!')

        if not user.check_password(password):
            raise AuthenticationFailed('Incorrect password!')
        
        if not user.is_login_activated:
            raise AuthenticationFailed('Account not activated!')

        response = Response()
        
        user = User.objects.filter(id=user.id).first()
        serializer = UserSerializer(user)

        user=authenticate(
            request,
            username=username,
            password=password,
    
        )
        login(request,user)
        request.session['username']=user.username    
        request.session['user']=user.username


        response.data = {
            'user': serializer.data,
        }
        return response
#login page 
def loginPage(request):
    return render(request,'login.html')


def uploadPage(request):
    return render(request,'uploadFile.html')

@api_view(['POST'])
def uploadFileAPI(request):
    if request.user.is_authenticated and request.method == 'POST':
        # validator = FileTypeValidator(
        #         allowed_types=['application/msword'],
        #         allowed_extensions=['.doc', '.docx']
        #     )
        if request.user.is_operation:
            serializer = FileSerializer(data=request.FILES)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
        else:
            content = {'please move along': 'nothing to see here'}
            return Response(content, status=status.HTTP_401_UNAUTHORIZED)

@api_view(['GET'])   
def listAllFilesAPI(request):
    
    if request.user.is_authenticated and request.method == 'GET':
        files = Files.objects.all().order_by('-id')
        serializer = FileSerializer(files, many=True)
        return Response(serializer.data)

def allFilesPage(request):
    return render(request,'allFiles.html')


@api_view(['GET'])    
def downloadAPI(request, path):
    
    file_path = os.path.join(settings.MEDIA_ROOT, path)
    print(file_path)
    if os.path.exists(file_path):
        with open(file_path, 'rb') as fh:
            response = HttpResponse(fh.read(), content_type="application/vnd.ms-excel")
            response['Content-Disposition'] = 'inline; filename=' + os.path.basename(file_path)
            return response
    raise Http404