from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/', include('accounts.urls')),         # if accounts has its own URLs
    path('api/teams/', include('teams.urls')),           # if teams has its own URLs
    path('api/projects/', include('projects.urls')),     # if projects has its own URLs
    path('api/tasks/', include('tasks.urls')),           # if tasks has its own URLs
    path('api/contributions/', include('contributions.urls')),
    path('api/analytics/', include('analytics.urls')),   # you'll create this next
    path('api/notifications/', include('notifications.urls')), # you'll create this next
]