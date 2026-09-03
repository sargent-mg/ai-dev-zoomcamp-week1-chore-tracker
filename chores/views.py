from datetime import date

from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from .forms import ChoreForm, HouseholdForm, PersonForm
from .models import Chore, ChoreAssignment, ChoreLog, Household, Person


def _session_key(household):
    return f"person_id:{household.slug}"


def _get_current_person(request, household):
    person_id = request.session.get(_session_key(household))
    return household.people.filter(id=person_id).first() if person_id else None


def household_create(request):
    if request.method == "POST":
        form = HouseholdForm(request.POST)
        if form.is_valid():
            household = form.save()
            return redirect("household_detail", slug=household.slug)
    else:
        form = HouseholdForm()
    return render(request, "chores/household_create.html", {"form": form})


def household_detail(request, slug):
    household = get_object_or_404(Household, slug=slug)
    context = {
        "household": household,
        "people": household.people.all(),
        "chores": household.chores.select_related("assignment__person"),
        "current_person": _get_current_person(request, household),
        "person_form": PersonForm(),
        "chore_form": ChoreForm(),
    }
    return render(request, "chores/household_detail.html", context)


def pick_person(request, slug, person_id):
    household = get_object_or_404(Household, slug=slug)
    person = get_object_or_404(Person, id=person_id, household=household)
    if request.method == "POST":
        request.session[_session_key(household)] = person.id
    return redirect("household_detail", slug=household.slug)


def add_person(request, slug):
    household = get_object_or_404(Household, slug=slug)
    if request.method == "POST":
        form = PersonForm(request.POST)
        if form.is_valid():
            person = form.save(commit=False)
            person.household = household
            person.save()
    return redirect("household_detail", slug=household.slug)


def add_chore(request, slug):
    household = get_object_or_404(Household, slug=slug)
    if request.method == "POST":
        form = ChoreForm(request.POST)
        if form.is_valid():
            chore = form.save(commit=False)
            chore.household = household
            chore.save()
    return redirect("household_detail", slug=household.slug)


def assign_chore(request, slug, chore_id):
    household = get_object_or_404(Household, slug=slug)
    chore = get_object_or_404(Chore, id=chore_id, household=household)
    if request.method == "POST":
        person_id = request.POST.get("person")
        if person_id:
            person = get_object_or_404(Person, id=person_id, household=household)
            ChoreAssignment.objects.update_or_create(chore=chore, defaults={"person": person})
        else:
            ChoreAssignment.objects.filter(chore=chore).delete()
    return redirect("household_detail", slug=household.slug)


def household_today(request, slug):
    household = get_object_or_404(Household, slug=slug)
    current_person = _get_current_person(request, household)
    today = timezone.localdate()

    logs_by_chore = {
        log.chore_id: log
        for log in ChoreLog.objects.filter(chore__household=household, date=today)
    }

    chore_rows = []
    for chore in household.chores.select_related("assignment__person"):
        assignment = getattr(chore, "assignment", None)
        assignee = assignment.person if assignment else None
        log = logs_by_chore.get(chore.id)
        chore_rows.append(
            {
                "chore": chore,
                "assignee": assignee,
                "log": log,
                "can_check_off": (
                    log is None
                    and current_person is not None
                    and assignee is not None
                    and assignee.id == current_person.id
                ),
            }
        )

    context = {
        "household": household,
        "current_person": current_person,
        "today": today,
        "chore_rows": chore_rows,
    }
    return render(request, "chores/household_today.html", context)


def check_off_chore(request, slug, chore_id):
    household = get_object_or_404(Household, slug=slug)
    chore = get_object_or_404(Chore, id=chore_id, household=household)
    current_person = _get_current_person(request, household)

    if request.method == "POST" and current_person is not None:
        assignment = getattr(chore, "assignment", None)
        if assignment is not None and assignment.person_id == current_person.id:
            ChoreLog.objects.get_or_create(
                chore=chore,
                date=timezone.localdate(),
                defaults={
                    "person": current_person,
                    "status": ChoreLog.Status.DONE,
                    "completed_at": timezone.now(),
                },
            )
    return redirect("household_today", slug=household.slug)


def household_history(request, slug):
    household = get_object_or_404(Household, slug=slug)
    current_person = _get_current_person(request, household)

    logs = (
        ChoreLog.objects.filter(chore__household=household)
        .select_related("chore", "person")
        .order_by("-date", "chore__name")
    )

    person_id = request.GET.get("person") or ""
    if person_id:
        logs = logs.filter(person_id=person_id)

    start = request.GET.get("start") or ""
    end = request.GET.get("end") or ""
    try:
        if start:
            logs = logs.filter(date__gte=date.fromisoformat(start))
        if end:
            logs = logs.filter(date__lte=date.fromisoformat(end))
    except ValueError:
        pass

    context = {
        "household": household,
        "current_person": current_person,
        "people": household.people.all(),
        "logs": logs,
        "selected_person": person_id,
        "start": start,
        "end": end,
    }
    return render(request, "chores/household_history.html", context)
