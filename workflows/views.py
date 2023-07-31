from rest_framework import viewsets
from utils.base_authentication import JWTAuthentication
from utils.base_permission import FeatureBasedPermission
from workflows.serializers import WrokflowSerializer
from workflows.controllers import WorkflowController

workflow_controller = WorkflowController()


class WorkflowListingView(viewsets.ModelViewSet):
    """
    Endpoints for Module CRUDs.
    """
    authentication_classes = (JWTAuthentication,)
    permission_classes = (FeatureBasedPermission,)
    serializer_class = WrokflowSerializer

    def get(self, request):
        return workflow_controller.get_workflow(request)

    def create(self, request):
        return workflow_controller.create_workflow(request)

    def update(self, request):
        return workflow_controller.update_workflow(request)

    def destroy(self, request):
        return workflow_controller.delete_workflow(request)
