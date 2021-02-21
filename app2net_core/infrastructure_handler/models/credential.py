from django.db import models


class AccessType(models.Model):
    name = models.CharField(max_length=50)
    command = models.TextField()
    params = models.TextField(blank=True)
    uploadable = models.BooleanField(default=False)


class Credential(models.Model):
    username = models.CharField(max_length=50, null=True)
    password = models.CharField(max_length=50, null=True)
    key = models.FileField(upload_to='pvn_credentials', null=True)
    access_type = models.ForeignKey(AccessType, on_delete=models.CASCADE, related_name="credentials")
