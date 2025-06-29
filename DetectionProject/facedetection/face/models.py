from django.db import models
from datetime import date


class Criminal(models.Model):
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
    ]

    first_name = models.CharField(max_length=100)
    middle_name = models.CharField(max_length=100, blank=True, null=True)
    last_name = models.CharField(max_length=100)
    dob = models.DateField()
    age = models.IntegerField()
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)

    def save(self, *args, **kwargs):
        today = date.today()
        self.age = today.year - self.dob.year - ((today.month, today.day) < (self.dob.month, self.dob.day))
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class CriminalImage(models.Model):
    criminal = models.ForeignKey(Criminal, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='criminal_images/')

    def __str__(self):
        return f"Image for {self.criminal.first_name} {self.criminal.last_name}"