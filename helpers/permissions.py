from Shop.models import Shop
from Accounts.models import Company
from rest_framework import permissions

class IsCompanyAdmin(permissions.BasePermission):
    """
    Custom permission to check if the user is Authenticated
    Allows access if the user is authenticated and is the Admin of the Company.
    """

    def has_permission(self, request, view):
        company_id = view.kwargs["company_id"]

        if company_id:
            company_admin = (
                Company.objects.filter(id=company_id)
                .values_list("companyAdmin", flat=True)
                .first()
            )
            return request.user.is_authenticated and request.user.id == company_admin
        return False