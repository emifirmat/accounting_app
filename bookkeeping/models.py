from django.db import models, IntegrityError
from django.db.models import Sum, Q

from erp.validators import validate_is_digit


# Create your models here.
class Chart_category(models.Model):
    """Category: assets, liabiities, etc"""
    code = models.CharField(max_length=2, unique=True, validators=[
        validate_is_digit
    ])
    name = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.code} {self.name}"    
    
    def save(self, *args, **kwargs):
        # Fill code with 0
        self.code = self.code.zfill(2)
        return super(Chart_category, self).save(*args, **kwargs)

class Chart_account(models.Model):
    """Account: Cash, banks, etc"""
    code = models.CharField(max_length=6, validators=[validate_is_digit])
    name = models.CharField(max_length=50)
    category = models.ForeignKey(Chart_category, on_delete=models.CASCADE)
    allocable = models.BooleanField()

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["code", "category"],
                name="unique_code")
        ]
    
    def __str__(self):
        return f"{self.category.code}{self.code} {self.name}"
    

class Entry(models.Model):
    """Bookkeeping entries"""
    number = models.PositiveIntegerField()
    date = models.DateTimeField(auto_now_add=True)
    account = models.ForeignKey(Chart_account, on_delete=models.PROTECT)
    description = models.CharField(max_length=80)
    debit = models.DecimalField(max_digits=15, decimal_places=2)
    credit = models.DecimalField(max_digits=15, decimal_places=2)
    last_line = models.BooleanField()
    locked = models.BooleanField(default=False)

    class Meta:
        verbose_name_plural = "Entries"

    def __str__(self):
        return f"{self.number} | {self.date}"
    
    def save(self, *args, **kwargs):
        """Control that in each entry, the credit and debit are the same"""
        if self.last_line == True:
            full_entry = self.__class__.objects.filter(number=self.number)
            total_debit = float(full_entry.aggregate(
                Sum("debit"))["debit__sum"]) + float(self.debit)
            total_credit = float(full_entry.aggregate(
                Sum("credit"))["credit__sum"]) + float(self.credit)

            if round(total_credit,2) != round(total_debit, 2):
                for instance in full_entry:
                    instance.delete()
                raise IntegrityError("Debit must be equal to credit")
            else:
                self.locked = True
            
        return super(Entry, self).save(*args, **kwargs)    