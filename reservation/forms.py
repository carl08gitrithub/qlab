from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from lab.models import Lab
from reservation.models import Reservation

class ErrorStyle(forms.Form):
    def is_valid(self):
        valid = super().is_valid()
        for field in self.errors:
            if field in self.fields:
                existing_classes = self.fields[field].widget.attrs.get("class", "")
                if "input-error" not in existing_classes:
                    self.fields[field].widget.attrs["class"] = existing_classes + " input-error"
        return valid

class RegisterForm(UserCreationForm, ErrorStyle):
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            "class": "input input-bordered w-full",
        })
    )
    password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            "class": "input input-bordered w-full",
        })
    )
    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            "class": "input input-bordered w-full",
        })
    )

    class Meta:
        model = User
        fields = ("username", "password1", "password2")

class LoginForm(AuthenticationForm, ErrorStyle):
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            "class": "input input-bordered w-full",
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            "class": "input input-bordered w-full",
        })
    )

class ReservationRequestForm(forms.Form):
    lab = forms.ModelChoiceField(
        queryset=Lab.objects.all(),
        widget=forms.Select(attrs={"class": "select select-bordered w-full"})
    )
    date = forms.DateField(
        widget=forms.DateInput(attrs={"type": "date", "class": "input input-bordered w-full"})
    )
    start_time = forms.TimeField(
        widget=forms.TimeInput(attrs={"type": "time", "class": "input input-bordered w-full"})
    )
    end_time = forms.TimeField(
        widget=forms.TimeInput(attrs={"type": "time", "class": "input input-bordered w-full"})
    )

    def clean(self):
        cleaned = super().clean()
        lab = cleaned.get("lab")
        date = cleaned.get("date")
        start = cleaned.get("start_time")
        end = cleaned.get("end_time")

        if not all([lab, date, start, end]):
            return cleaned

        if start >= end:
            raise forms.ValidationError("End time must be later than start time.")

        overlapping = Reservation.objects.filter(
            lab=lab,
            date=date,
            status__in=["approved", "queued"],
            start_time__lt=end,
            end_time__gt=start,
        )

        if overlapping.exists():
            raise forms.ValidationError(
                "This time slot is already taken or overlaps with another reservation."
            )

        return cleaned
