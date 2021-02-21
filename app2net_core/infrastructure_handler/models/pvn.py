from django.db import models
from django.contrib.auth import get_user_model


class Pvn(models.Model):
    name = models.CharField(max_length=100)
    owner = models.ManyToManyField(get_user_model(), verbose_name="PVN Owner", related_name="pvns")

    def __str__(self):
        return f"{self.name}"