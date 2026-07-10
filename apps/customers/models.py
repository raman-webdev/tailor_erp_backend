from django.db import models
from ..common.models import BaseModel

# Create your models here.

class Customer(BaseModel):
    name = models.CharField(max_length=255)
