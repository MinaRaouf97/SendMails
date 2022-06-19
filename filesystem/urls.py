from django.urls import path,re_path
from .views import VerificationView,LoginView,loginPage,uploadPage,uploadFileAPI,listAllFilesAPI,allFilesPage,downloadAPI,RegisterView,signUpPage
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('api/login/', LoginView.as_view() , name="login_api"),
    path('login',loginPage,name="login"),
    path('api/signup/', RegisterView.as_view()),
    path('signup',signUpPage),
    path('uploadfile',uploadPage ),
    path('api/uploadfile/',uploadFileAPI),
    path('api/listfiles/',listAllFilesAPI),
    path('allfiles',allFilesPage),
    path('activate/<uidb64>/<token>',
         VerificationView.as_view(), name='activate'),
    re_path(r'^api/download/(?P<path>.+)$',downloadAPI)
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
