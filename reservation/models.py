from django.db import models
from django.contrib.auth.models import User
from lab.models import Lab
from django.db.models import Max

class Reservation(models.Model):
    STATUS_CHOICES = [
        ('queued', 'Queued'),
        ('approved', 'Approved'),
        ('disapproved', 'Disapproved'),
        ('finished', 'Finished'),
    ]

    lab = models.ForeignKey(Lab, on_delete=models.CASCADE)
    student = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='queued'
    )
    queue_position = models.IntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['date', 'start_time', 'queue_position']

    def save(self, *args, **kwargs):
        # Assign queue_position if queued
        if self.status == 'queued' and self.queue_position is None:
            last_pos = Reservation.objects.filter(
                lab=self.lab,
                date=self.date,
                status='queued'
            ).aggregate(Max('queue_position'))['queue_position__max']
            self.queue_position = 1 if last_pos is None else last_pos + 1
        elif self.status != 'queued':
            self.queue_position = None

        super().save(*args, **kwargs)
