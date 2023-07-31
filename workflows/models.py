from django.db import models
from utils.base_models import LogsMixin
from user_management.models import Features, User, UserGroup


class Workflow(LogsMixin):
    operation_choices = (
        ("CREATION", "CREATION"),
        ("UPDATION", "UPDATION"),
        ("DELETION", "DELETION"),
    )
    name = models.CharField(max_length=100)
    feature = models.ForeignKey(Features, on_delete=models.DO_NOTHING, related_name="workflow")
    action = models.CharField(max_length=10, null=True, blank=True, choices=operation_choices)
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING, related_name="workflow", null=True, blank=True)
    user_group = models.ForeignKey(UserGroup, on_delete=models.DO_NOTHING, related_name="workflow", null=True,
                                   blank=True)


class Hierarchy(LogsMixin):
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING, related_name="hierarchy")
    workflow = models.ForeignKey(Workflow, on_delete=models.DO_NOTHING, related_name="hierarchy")
    priority = models.IntegerField()
