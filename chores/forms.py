from django import forms

from .models import Chore, Household, Person


class HouseholdForm(forms.ModelForm):
    class Meta:
        model = Household
        fields = ["name"]


class PersonForm(forms.ModelForm):
    class Meta:
        model = Person
        fields = ["name"]


class ChoreForm(forms.ModelForm):
    class Meta:
        model = Chore
        fields = ["name"]
