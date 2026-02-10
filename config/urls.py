"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

from config import settings
from user.views import logout_view, register_user, profile, ban_user
from voting.views import index, save_vote, create_voting, report, report_history, report_review, voting
from voting.views import statistics


urlpatterns = ([
    path('admin/', admin.site.urls),
    path('accounts/', include('django.contrib.auth.urls')),

    path('', index, name='main'),
    path('logout/', logout_view, name='logout'),
    path('registration/', register_user, name='registration'),
    path('voting/<int:voting_id>/', voting, name='voting'),
    path('voting/<int:voting_id>/vote', save_vote, name='add_vote'),
    path('create_voting/', create_voting, name='create_voting'),
    path('profile/<str:nickname>/', profile, name='profile'),
    path('report/<int:voting_id>/', report, name='report'),
    path('report_history/', report_history, name='report_history'),
    path('report_review/<int:report_id>/', report_review, name='report_review'),
    path('delete_voting/<int:report_id>/', report_review, name='delete_voting'),
    path('ban_user/<int:user_id>/', ban_user, name='ban_user'),
    path('close_report/<int:report_id>/', report_review, name='close_report'),
    path('statistics/', statistics, name='statistics'),

] )

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
