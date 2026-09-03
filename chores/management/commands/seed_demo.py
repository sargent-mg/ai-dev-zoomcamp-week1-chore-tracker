from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from chores.models import Chore, ChoreAssignment, ChoreLog, Household, Person


class Command(BaseCommand):
    help = "Create a demo household with people, chores, assignments, and a few days of history."

    def handle(self, *args, **options):
        household, created = Household.objects.get_or_create(name="Demo Household")
        if not created:
            self.stdout.write(f"Reusing existing household: {household.name} ({household.slug})")

        mom, _ = Person.objects.get_or_create(household=household, name="Mom")
        dad, _ = Person.objects.get_or_create(household=household, name="Dad")
        kid, _ = Person.objects.get_or_create(household=household, name="Kid")

        dishes, _ = Chore.objects.get_or_create(household=household, name="Dishes")
        trash, _ = Chore.objects.get_or_create(household=household, name="Take out trash")
        laundry, _ = Chore.objects.get_or_create(household=household, name="Laundry")

        ChoreAssignment.objects.update_or_create(chore=dishes, defaults={"person": mom})
        ChoreAssignment.objects.update_or_create(chore=trash, defaults={"person": dad})
        ChoreAssignment.objects.update_or_create(chore=laundry, defaults={"person": kid})

        today = timezone.localdate()
        for days_ago, status in [(1, ChoreLog.Status.DONE), (2, ChoreLog.Status.MISSED), (3, ChoreLog.Status.DONE)]:
            log_date = today - timedelta(days=days_ago)
            ChoreLog.objects.get_or_create(
                chore=dishes,
                date=log_date,
                defaults={
                    "person": mom,
                    "status": status,
                    "completed_at": timezone.now() if status == ChoreLog.Status.DONE else None,
                },
            )

        self.stdout.write(self.style.SUCCESS(f"Demo household ready at /h/{household.slug}/"))
