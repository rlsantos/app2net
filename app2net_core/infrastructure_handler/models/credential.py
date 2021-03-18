from django.db import models


class AccessType(models.Model):
    name = models.CharField(max_length=50)
    command = models.TextField()
    params = models.TextField(blank=True)
    uploadable = models.BooleanField(default=False)


class Credential(models.Model):
    username = models.CharField(max_length=50, blank=True)
    password = models.CharField(max_length=50, blank=True)
    key = models.FileField(upload_to='pvn_credentials', null=True, blank=True)
    access_type = models.ForeignKey(AccessType, on_delete=models.CASCADE, related_name="credentials")

    def connect(self):
        command = self.access_type.command

        for param in self.access_type.params.split():
            command.replace(f"${param}$", getattr(self, param))
