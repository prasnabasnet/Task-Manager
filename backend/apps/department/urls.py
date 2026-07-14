from django.urls import path

from apps.department.views import DepartmentViewSet

dept_list = DepartmentViewSet.as_view({"get": "list", "post": "create"})
dept_detail = DepartmentViewSet.as_view(
    {"get": "retrieve", "patch": "partial_update", "put": "update", "delete": "destroy"}
)

dept_projects = DepartmentViewSet.as_view({"get": "projects", "post": "projects"})

urlpatterns = [
    path("organizations/<int:oid>/departments/", dept_list, name="dept-list"),
    path(
        "organizations/<int:oid>/departments/<int:pk>/", dept_detail, name="dept-detail"
    ),
    path(
        "organizations/<int:oid>/departments/<int:pk>/projects/",
        dept_projects,
        name="dept-project-list",
    ),
]
