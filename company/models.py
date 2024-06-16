from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q

from erp.validators import validate_is_digit


# Create your models here.
class SingletonModel(models.Model):
    """Model for classes that only use one instance"""
    def save(self, *args, **kwargs):
        # Check that there is a new pk, but an instance already exists.
        # Note, if pk already exists it means we're modifying and not creating
        # an instance
        if not self.pk and self.__class__.objects.exists():
            raise ValidationError(
                f"An instance of {self.__class__.__name__} already exits"
            )
        else:
            return super(SingletonModel, self).save(*args, **kwargs)
        
    class Meta:
        # Don't save SingletonModel in DB
        abstract = True


class PersonModel(models.Model):
    """Create base information for Company, Client and Supplier"""
    tax_number = models.CharField(unique=True, max_length=11, validators=[
        validate_is_digit
    ])
    name = models.CharField(max_length=50)
    address = models.CharField(max_length=80)
    email = models.EmailField()
    phone = models.CharField(max_length=25, validators=[
        validate_is_digit
    ])
    
    class Meta:
        abstract = True
    
    def __str__(self):
        return f"{self.name} | {self.tax_number}"
    

class Company(PersonModel, SingletonModel):
    """Company information"""
    creation_date = models.DateField()
    closing_date = models.DateField()

    class Meta:
        verbose_name_plural = "Company"


class FinancialYear(models.Model):
    """Financial year of the company"""
    year = models.CharField(unique=True, max_length=4, validators=[
        validate_is_digit
    ])
    current = models.BooleanField(default=False)

    class Meta: 
        constraints = [
            models.UniqueConstraint(fields=["current"], condition=Q(current=True),
                name="unique_true_current_year"
            )
        ]

    def __str__(self):
        return f"{self.year}"
    
    
class Calendar(SingletonModel):
    """Set calendar limits"""
    starting_date = models.OneToOneField(Company, on_delete=models.CASCADE)
    ending_date = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Calendar"
    
    def __str__(self):
        return f"From {self.starting_date.creation_date} to {self.ending_date}."