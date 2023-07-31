from rest_framework import viewsets
from bulk_update_management.bulk_update_controller import *
from utils.base_authentication import JWTAuthentication
from utils.base_permission import *

bulk_update_controller = BulkUpdateController()
bulk_import_controller = BulkImportController()
excel_preview_controller = ExcelPreviewController()
template_controller = GetTemplateController()


class BulkUpdateView(viewsets.ModelViewSet):
    """
    Endpoints for Bulk Update functionality.
    """
    authentication_classes = (JWTAuthentication,)
    permission_classes = (FeatureBasedPermission,)

    def update(self, request):
        return bulk_update_controller.update(request)


class ImportView(viewsets.ModelViewSet):

    authentication_classes = (JWTAuthentication,)
    permission_classes = (FeatureBasedPermission,)

    def create(self, request):
        return bulk_import_controller.create(request)


class ExcelPreviewAPI(viewsets.ModelViewSet):
    """
    Endpoints to preview import file.
    """

    authentication_classes = (JWTAuthentication,)
    permission_classes = (FeatureBasedPermission,)

    def create_preview(self, request):
        return excel_preview_controller.preview(request)


class GetTemplateAPI(viewsets.ModelViewSet):
    """
    Endpoints for downloading template.
    """

    authentication_classes = (JWTAuthentication,)
    permission_classes = (FeatureBasedPermission,)

    def get_template(self, request):
        return template_controller.template(request)
