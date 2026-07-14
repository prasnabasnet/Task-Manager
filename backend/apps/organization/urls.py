from django.urls import path

from apps.organization.views import OrganizationViewSet

org_list = OrganizationViewSet.as_view({"get": "list", "post": "create"})
org_detail = OrganizationViewSet.as_view(
    {"get": "retrieve", "put": "update", "patch": "partial_update", "delete": "destroy"}
)

urlpatterns = [
    path("organizations/", org_list, name="organization-list"),
    path("organizations/<int:pk>/", org_detail, name="organization-detail"),
]
