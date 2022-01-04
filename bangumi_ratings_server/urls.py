"""bangumi_ratings_server URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
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
from django.contrib import admin
from django.urls import path
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate

from graphene_django.views import GraphQLView

from bangumi_ratings_backend.admin import admin_site

def health_check_view(request):
    return HttpResponse("OK")

def authentication(request):
    print(request.GET)
    user = authenticate(username=request.GET['username'], password=request.GET['password'])
    if user is not None:
        return HttpResponse("OK")
    else:
        return HttpResponse("Unauthorized", status=401)


urlpatterns = [
    path('health_check', health_check_view),
    path('authenticate', authentication),
    path('admin/', admin.site.urls),
    path('bangumi-ratings-server-admin/', admin_site.urls),
    path('graphql', csrf_exempt(GraphQLView.as_view(graphiql=True))),
]
