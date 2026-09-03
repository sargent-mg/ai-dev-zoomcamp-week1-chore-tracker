from django.urls import path

from . import views

urlpatterns = [
    path("", views.household_create, name="household_create"),
    path("h/<slug:slug>/", views.household_detail, name="household_detail"),
    path("h/<slug:slug>/identify/<int:person_id>/", views.pick_person, name="pick_person"),
    path("h/<slug:slug>/people/add/", views.add_person, name="add_person"),
    path("h/<slug:slug>/chores/add/", views.add_chore, name="add_chore"),
    path("h/<slug:slug>/chores/<int:chore_id>/assign/", views.assign_chore, name="assign_chore"),
    path("h/<slug:slug>/today/", views.household_today, name="household_today"),
    path("h/<slug:slug>/chores/<int:chore_id>/check-off/", views.check_off_chore, name="check_off_chore"),
    path("h/<slug:slug>/history/", views.household_history, name="household_history"),
]
