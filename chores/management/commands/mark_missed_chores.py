from datetime import date, timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from chores.models import Chore, ChoreLog


class Command(BaseCommand):
    help = "Mark assigned chores with no log for the given date (default: yesterday) as missed."

    def add_arguments(self, parser):
        parser.add_argument(
            "--date",
            type=str,
            default=None,
            help="ISO date (YYYY-MM-DD) to mark missed chores for. Defaults to yesterday.",
        )

    def handle(self, *args, **options):
        if options["date"]:
            target_date = date.fromisoformat(options["date"])
        else:
            target_date = timezone.localdate() - timedelta(days=1)

        chores = Chore.objects.select_related("assignment__person").exclude(logs__date=target_date)

        created = 0
        for chore in chores:
            assignment = getattr(chore, "assignment", None)
            if assignment is None:
                continue
            ChoreLog.objects.create(
                chore=chore,
                person=assignment.person,
                date=target_date,
                status=ChoreLog.Status.MISSED,
            )
            created += 1

        self.stdout.write(self.style.SUCCESS(f"Marked {created} chore(s) as missed for {target_date}."))
