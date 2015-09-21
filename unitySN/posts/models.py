from django.db import models
from .compat import user_model_label,generic
from django.contrib.contenttypes.models import ContentType

try:
    from django.utils import timezone
    now = timezone.now
except ImportError:
    from datetime import datetime
    now = datetime.now


class Post(models.Model):

    author = models.ForeignKey(user_model_label, db_index=True)
    target_content_type = models.ForeignKey(ContentType, blank=True, null=True,
                                            related_name='target', db_index=True)
    target_object_id = models.CharField(max_length=255, blank=True, null=True, db_index=True)
    target = generic.GenericForeignKey('target_content_type',
                                       'target_object_id')
    post_visibility_content_type = models.ForeignKey(ContentType, blank=True, null=True,
                                                   related_name='post_visibility', db_index=True)
    post_visibility_object_id = models.CharField(max_length=255, blank=True, null=True, db_index=True)
    post_visibility = generic.GenericForeignKey('post_visibility_content_type',
                                              'apost_visibility_object_id')
    timestamp = models.DateTimeField(default=now, db_index=True)
    content = models.TextField()