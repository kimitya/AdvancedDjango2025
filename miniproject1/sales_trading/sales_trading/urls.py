"""
URL configuration for sales_trading project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
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
from django.urls import path, include

from django.conf import settings
from django.conf.urls.static import static
from rest_framework_simplejwt.views import TokenRefreshView, TokenObtainPairView

from drf_yasg.views import get_schema_view
from drf_yasg import openapi

schema_view = get_schema_view(
    openapi.Info(
        title="Sales and Trading API",
        default_version="1.0.0",
        description="API for managing sales and trading of products",
    ),
    public=True,
    # url="http://127.0.0.1:8000/api",
)

urlpatterns = [
    path("admin/", admin.site.urls),

    path('api/users/', include('users.urls')),


    path('api/', include('products.urls')),

    path('api/trading/', include('trading.urls')),

    path('api/sales/', include('sales.urls')),
    path('api/swagger/schema/', schema_view.with_ui('swagger', cache_timeout=0), name='swagger-schema'),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
