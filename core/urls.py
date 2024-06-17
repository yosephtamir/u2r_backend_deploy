import json
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from drf_yasg.generators import OpenAPISchemaGenerator
from django.conf import settings
from django.conf.urls.static import static

version = "v1"

class CustomSchemaGenerator(OpenAPISchemaGenerator):
    def get_schema(self, request=None, public=False):
        schema = super().get_schema(request, public)
        schema.schemes = ['http', 'https'] if settings.DEBUG else ['https']
        # print(json.dumps(schema, indent=4))
        if hasattr(schema, 'paths'):
            for path, path_item in schema.paths.items():
                for method, operation in path_item.items():
                    if 'tags' in operation:
                        operation['tags'] = [tag.capitalize() if tag.lower() == "marketplace" else tag for tag in operation['tags']]
                        operation['tags'] = [tag.capitalize() if tag.lower() == "shops" else tag for tag in operation['tags']]
        return schema

schema_view = get_schema_view(
    openapi.Info(
        title="Int-B2B Project API",
        default_version=version,
        description="API Documentation for the Int-B2B API",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="support@int.gmail.com"),
        license=openapi.License(name="Int-B2B License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
    generator_class=CustomSchemaGenerator
)

urlpatterns = [
    path('admin/', admin.site.urls),

    # DRF-Swagger URLs
    path(f'api/{version}/swagger<format>/', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path(f'api/{version}/swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path(f'api/{version}/redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),

    # URLconfs
    path(f'api/{version}/', include('Accounts.urls')),
    path(f'api/{version}/', include('MarketPlace.urls')),
    path(f'api/{version}/', include('Shop.urls')),
]    

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
