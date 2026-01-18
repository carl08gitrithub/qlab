from django.db.models import Max
from .models import Reservation

def slot_taken(lab, date, start, end):
    return Reservation.objects.filter(
        lab=lab,
        date=date,
        status='approved',
        start_time__lt=end,
        end_time__gt=start
    ).exists()


def add_to_queue(student, lab, date, start, end):
    return Reservation.objects.create(
        student=student,
        lab=lab,
        date=date,
        start_time=start,
        end_time=end,
        status='queued'
    )


def promote_next_in_queue(lab, date):
    next_in_queue = Reservation.objects.filter(
        lab=lab,
        date=date,
        status='queued'
    ).order_by('queue_position').first()
    if next_in_queue:
        next_in_queue.status = 'approved'
        next_in_queue.save()