from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import include, path
from django.views.generic import RedirectView


urlpatterns = [
    path("", RedirectView.as_view(url="/facial/", permanent=False)),
    path("facial/admin/", admin.site.urls),
    path("facial/login/", auth_views.LoginView.as_view(template_name="registration/login.html"), name="login"),
    path("facial/logout/", auth_views.LogoutView.as_view(next_page="/facial/login/"), name="logout"),
    path("facial/", include("apps.attendance.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
