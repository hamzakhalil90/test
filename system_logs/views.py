from system_logs.logs_controller import AuditLogsController
from rest_framework import viewsets
from rest_framework.permissions import IsAdminUser
from utils.base_authentication import *

logs_controller = AuditLogsController()


class AuditLogsAPIView(viewsets.ModelViewSet):
    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAdminUser,)

    def get(self, request):
        return logs_controller.get_logs(request)
    
    def destroy(self, request):
        return logs_controller.delete_logs(request)


