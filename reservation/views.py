from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from lab.models import Lab
from django.contrib import admin
from .models import Reservation
from .services import slot_taken, add_to_queue, promote_next_in_queue
from django.contrib.admin.views.decorators import staff_member_required
from .forms import RegisterForm, ReservationRequestForm
from datetime import timedelta
from django.utils.timezone import now


def register(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user) 
            return redirect('login')
    else:
        form = RegisterForm()

    return render(request, 'registration/register.html', {
        'form': form
    })

@login_required
def reservation_schedule(request):
    today = now().date()
    start_of_week = today - timedelta(days=today.weekday()) 

    week = []
    for i in range(7):
        day = start_of_week + timedelta(days=i)
        day_reservations = Reservation.objects.filter(
            date=day,
            status__in=['queued', 'approved']
        ).select_related('lab', 'student')

        week.append({
            'date': day,
            'reservations': day_reservations
        })

    return render(
        request,
        'reservation/reservation_schedule.html',
        {
            'week': week
        }
    )

@login_required
def dashboard(request):
    reservations = Reservation.objects.filter(student=request.user)
    labs = Lab.objects.all()

    return render(request, 'reservation/dashboard.html', {
        'reservations': reservations,
        'labs': labs
    })


@login_required
def request_lab(request):
    if request.method == "POST":
        form = ReservationRequestForm(request.POST)
        if form.is_valid():
            lab = form.cleaned_data["lab"]
            date = form.cleaned_data["date"]
            start = form.cleaned_data["start_time"]
            end = form.cleaned_data["end_time"]

            add_to_queue(request.user, lab, date, start, end)

            return redirect("dashboard")
    else:
        form = ReservationRequestForm()

    return render(
        request,
        "reservation/request.html",
        {"form": form}
    )
    
@staff_member_required
def manage_reservations(request):
    reservations = Reservation.objects.order_by('date', 'start_time', 'queue_position')
    
    if request.method == 'POST':
        res_id = request.POST['reservation_id']
        action = request.POST['action']
        res = Reservation.objects.get(id=res_id)

        if action == 'approve':
            res.status = 'approved'
            res.save()
        elif action == 'disapprove':
            res.status = 'disapproved'
            res.save()
  
            next_in_queue = Reservation.objects.filter(
                lab=res.lab, date=res.date, status='queued'
            ).order_by('queue_position').first()
            if next_in_queue:
                next_in_queue.status = 'approved'
                next_in_queue.save()
        elif action == 'finish':
            res.status = 'finished'
            res.save()

            next_in_queue = Reservation.objects.filter(
                lab=res.lab, date=res.date, status='queued'
            ).order_by('queue_position').first()
            if next_in_queue:
                next_in_queue.status = 'approved'
                next_in_queue.save()

@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    list_display = ('student', 'lab', 'date', 'start_time', 'end_time', 'status', 'queue_position')
    list_filter = ('status', 'lab', 'date')
    ordering = ('date', 'start_time', 'queue_position')
    search_fields = ('student__username', 'lab__name')

    actions = ['approve_reservations', 'disapprove_reservations', 'finish_reservations']

    def approve_reservations(self, request, queryset):
        for res in queryset.filter(status='queued'):
            res.status = 'approved'
            res.save()
    approve_reservations.short_description = "Approve selected reservations"

    def disapprove_reservations(self, request, queryset):
        for res in queryset:
            res.status = 'disapproved'
            res.save()
            promote_next_in_queue(res.lab, res.date)
    disapprove_reservations.short_description = "Disapprove selected reservations"

    def finish_reservations(self, request, queryset):
        for res in queryset.filter(status='approved'):
            res.status = 'finished'
            res.save()
            promote_next_in_queue(res.lab, res.date)
    finish_reservations.short_description = "Finish selected reservations"