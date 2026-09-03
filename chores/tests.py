from datetime import timedelta

from django.core.management import call_command
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from .models import Chore, ChoreAssignment, ChoreLog, Household, Person


class MarkMissedChoresTests(TestCase):
    def setUp(self):
        self.household = Household.objects.create(name="Test House")
        self.person = Person.objects.create(household=self.household, name="Mom")
        self.chore = Chore.objects.create(household=self.household, name="Dishes")
        ChoreAssignment.objects.create(chore=self.chore, person=self.person)
        self.yesterday = timezone.localdate() - timedelta(days=1)

    def test_marks_unlogged_assigned_chore_as_missed(self):
        call_command("mark_missed_chores")
        log = ChoreLog.objects.get(chore=self.chore, date=self.yesterday)
        self.assertEqual(log.status, ChoreLog.Status.MISSED)
        self.assertEqual(log.person, self.person)

    def test_does_not_overwrite_existing_log(self):
        ChoreLog.objects.create(
            chore=self.chore, person=self.person, date=self.yesterday, status=ChoreLog.Status.DONE
        )
        call_command("mark_missed_chores")
        log = ChoreLog.objects.get(chore=self.chore, date=self.yesterday)
        self.assertEqual(log.status, ChoreLog.Status.DONE)

    def test_skips_unassigned_chores(self):
        unassigned = Chore.objects.create(household=self.household, name="Vacuum")
        call_command("mark_missed_chores")
        self.assertFalse(ChoreLog.objects.filter(chore=unassigned).exists())

    def test_explicit_date_argument(self):
        target = self.yesterday - timedelta(days=5)
        call_command("mark_missed_chores", date=target.isoformat())
        log = ChoreLog.objects.get(chore=self.chore, date=target)
        self.assertEqual(log.status, ChoreLog.Status.MISSED)


class CheckOffChoreViewTests(TestCase):
    def setUp(self):
        self.household = Household.objects.create(name="Test House")
        self.mom = Person.objects.create(household=self.household, name="Mom")
        self.kid = Person.objects.create(household=self.household, name="Kid")
        self.chore = Chore.objects.create(household=self.household, name="Dishes")
        ChoreAssignment.objects.create(chore=self.chore, person=self.mom)

    def _identify_as(self, person):
        self.client.post(
            reverse("pick_person", kwargs={"slug": self.household.slug, "person_id": person.id})
        )

    def test_assigned_person_can_check_off_own_chore(self):
        self._identify_as(self.mom)
        self.client.post(
            reverse("check_off_chore", kwargs={"slug": self.household.slug, "chore_id": self.chore.id})
        )
        log = ChoreLog.objects.get(chore=self.chore, date=timezone.localdate())
        self.assertEqual(log.status, ChoreLog.Status.DONE)
        self.assertEqual(log.person, self.mom)

    def test_other_person_cannot_check_off_chore(self):
        self._identify_as(self.kid)
        self.client.post(
            reverse("check_off_chore", kwargs={"slug": self.household.slug, "chore_id": self.chore.id})
        )
        self.assertFalse(ChoreLog.objects.filter(chore=self.chore).exists())

    def test_unidentified_visitor_cannot_check_off_chore(self):
        self.client.post(
            reverse("check_off_chore", kwargs={"slug": self.household.slug, "chore_id": self.chore.id})
        )
        self.assertFalse(ChoreLog.objects.filter(chore=self.chore).exists())

    def test_cannot_double_check_off(self):
        self._identify_as(self.mom)
        url = reverse("check_off_chore", kwargs={"slug": self.household.slug, "chore_id": self.chore.id})
        self.client.post(url)
        first_log = ChoreLog.objects.get(chore=self.chore)
        self.client.post(url)
        self.assertEqual(ChoreLog.objects.filter(chore=self.chore).count(), 1)
        self.assertEqual(ChoreLog.objects.get(chore=self.chore).completed_at, first_log.completed_at)


class SessionIdentificationTests(TestCase):
    def setUp(self):
        self.household = Household.objects.create(name="Test House")
        self.mom = Person.objects.create(household=self.household, name="Mom")

    def test_picking_a_person_persists_across_requests(self):
        self.client.post(
            reverse("pick_person", kwargs={"slug": self.household.slug, "person_id": self.mom.id})
        )
        response = self.client.get(
            reverse("household_detail", kwargs={"slug": self.household.slug})
        )
        self.assertEqual(response.context["current_person"], self.mom)

    def test_no_person_identified_by_default(self):
        response = self.client.get(
            reverse("household_detail", kwargs={"slug": self.household.slug})
        )
        self.assertIsNone(response.context["current_person"])

    def test_identification_is_scoped_per_household(self):
        other_household = Household.objects.create(name="Other House")
        self.client.post(
            reverse("pick_person", kwargs={"slug": self.household.slug, "person_id": self.mom.id})
        )
        response = self.client.get(
            reverse("household_detail", kwargs={"slug": other_household.slug})
        )
        self.assertIsNone(response.context["current_person"])


class HouseholdCreateViewTests(TestCase):
    def test_get_renders_empty_form(self):
        response = self.client.get(reverse("household_create"))
        self.assertEqual(response.status_code, 200)
        self.assertIsNone(response.context["form"].instance.pk)

    def test_valid_post_creates_household_and_redirects(self):
        response = self.client.post(reverse("household_create"), {"name": "The Testers"})
        household = Household.objects.get(name="The Testers")
        self.assertRedirects(response, reverse("household_detail", kwargs={"slug": household.slug}))

    def test_invalid_post_does_not_create_household(self):
        response = self.client.post(reverse("household_create"), {"name": ""})
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Household.objects.exists())


class AddPersonViewTests(TestCase):
    def setUp(self):
        self.household = Household.objects.create(name="Test House")

    def test_valid_post_creates_person(self):
        self.client.post(
            reverse("add_person", kwargs={"slug": self.household.slug}), {"name": "Dad"}
        )
        self.assertTrue(Person.objects.filter(household=self.household, name="Dad").exists())

    def test_invalid_post_does_not_create_person(self):
        self.client.post(reverse("add_person", kwargs={"slug": self.household.slug}), {"name": ""})
        self.assertFalse(Person.objects.filter(household=self.household).exists())

    def test_get_does_not_create_person(self):
        self.client.get(reverse("add_person", kwargs={"slug": self.household.slug}))
        self.assertFalse(Person.objects.filter(household=self.household).exists())


class AddChoreViewTests(TestCase):
    def setUp(self):
        self.household = Household.objects.create(name="Test House")

    def test_valid_post_creates_chore(self):
        self.client.post(
            reverse("add_chore", kwargs={"slug": self.household.slug}), {"name": "Vacuum"}
        )
        self.assertTrue(Chore.objects.filter(household=self.household, name="Vacuum").exists())

    def test_invalid_post_does_not_create_chore(self):
        self.client.post(reverse("add_chore", kwargs={"slug": self.household.slug}), {"name": ""})
        self.assertFalse(Chore.objects.filter(household=self.household).exists())

    def test_get_does_not_create_chore(self):
        self.client.get(reverse("add_chore", kwargs={"slug": self.household.slug}))
        self.assertFalse(Chore.objects.filter(household=self.household).exists())


class AssignChoreViewTests(TestCase):
    def setUp(self):
        self.household = Household.objects.create(name="Test House")
        self.mom = Person.objects.create(household=self.household, name="Mom")
        self.kid = Person.objects.create(household=self.household, name="Kid")
        self.chore = Chore.objects.create(household=self.household, name="Dishes")
        self.other_household = Household.objects.create(name="Other House")
        self.stranger = Person.objects.create(household=self.other_household, name="Stranger")

    def _assign_url(self):
        return reverse("assign_chore", kwargs={"slug": self.household.slug, "chore_id": self.chore.id})

    def test_valid_post_creates_assignment(self):
        self.client.post(self._assign_url(), {"person": self.mom.id})
        assignment = ChoreAssignment.objects.get(chore=self.chore)
        self.assertEqual(assignment.person, self.mom)

    def test_valid_post_replaces_existing_assignment(self):
        ChoreAssignment.objects.create(chore=self.chore, person=self.mom)
        self.client.post(self._assign_url(), {"person": self.kid.id})
        self.assertEqual(ChoreAssignment.objects.filter(chore=self.chore).count(), 1)
        assignment = ChoreAssignment.objects.get(chore=self.chore)
        self.assertEqual(assignment.person, self.kid)

    def test_empty_post_deletes_assignment(self):
        ChoreAssignment.objects.create(chore=self.chore, person=self.mom)
        self.client.post(self._assign_url(), {"person": ""})
        self.assertFalse(ChoreAssignment.objects.filter(chore=self.chore).exists())

    def test_person_from_other_household_rejected(self):
        response = self.client.post(self._assign_url(), {"person": self.stranger.id})
        self.assertEqual(response.status_code, 404)
        self.assertFalse(ChoreAssignment.objects.filter(chore=self.chore).exists())


class HouseholdTodayViewTests(TestCase):
    def setUp(self):
        self.household = Household.objects.create(name="Test House")
        self.mom = Person.objects.create(household=self.household, name="Mom")
        self.dishes = Chore.objects.create(household=self.household, name="Dishes")
        self.trash = Chore.objects.create(household=self.household, name="Trash")
        ChoreAssignment.objects.create(chore=self.dishes, person=self.mom)

    def _identify_as(self, person):
        self.client.post(
            reverse("pick_person", kwargs={"slug": self.household.slug, "person_id": person.id})
        )

    def _rows_by_chore(self, response):
        return {row["chore"].id: row for row in response.context["chore_rows"]}

    def test_pending_chore_shows_can_check_off_for_assignee(self):
        self._identify_as(self.mom)
        response = self.client.get(reverse("household_today", kwargs={"slug": self.household.slug}))
        row = self._rows_by_chore(response)[self.dishes.id]
        self.assertIsNone(row["log"])
        self.assertTrue(row["can_check_off"])

    def test_logged_chore_hides_check_off(self):
        ChoreLog.objects.create(
            chore=self.dishes, person=self.mom, date=timezone.localdate(), status=ChoreLog.Status.DONE
        )
        self._identify_as(self.mom)
        response = self.client.get(reverse("household_today", kwargs={"slug": self.household.slug}))
        row = self._rows_by_chore(response)[self.dishes.id]
        self.assertIsNotNone(row["log"])
        self.assertFalse(row["can_check_off"])

    def test_unassigned_chore_has_no_assignee_or_check_off(self):
        self._identify_as(self.mom)
        response = self.client.get(reverse("household_today", kwargs={"slug": self.household.slug}))
        row = self._rows_by_chore(response)[self.trash.id]
        self.assertIsNone(row["assignee"])
        self.assertFalse(row["can_check_off"])

    def test_no_identified_person_nobody_can_check_off(self):
        response = self.client.get(reverse("household_today", kwargs={"slug": self.household.slug}))
        row = self._rows_by_chore(response)[self.dishes.id]
        self.assertFalse(row["can_check_off"])


class HouseholdHistoryViewTests(TestCase):
    def setUp(self):
        self.household = Household.objects.create(name="Test House")
        self.mom = Person.objects.create(household=self.household, name="Mom")
        self.kid = Person.objects.create(household=self.household, name="Kid")
        self.dishes = Chore.objects.create(household=self.household, name="Dishes")
        self.trash = Chore.objects.create(household=self.household, name="Trash")
        self.today = timezone.localdate()

        self.log_mom_today = ChoreLog.objects.create(
            chore=self.dishes, person=self.mom, date=self.today, status=ChoreLog.Status.DONE
        )
        self.log_kid_today = ChoreLog.objects.create(
            chore=self.trash, person=self.kid, date=self.today, status=ChoreLog.Status.MISSED
        )
        self.log_mom_old = ChoreLog.objects.create(
            chore=self.dishes,
            person=self.mom,
            date=self.today - timedelta(days=5),
            status=ChoreLog.Status.MISSED,
        )

        self.other_household = Household.objects.create(name="Other House")
        other_person = Person.objects.create(household=self.other_household, name="Someone")
        other_chore = Chore.objects.create(household=self.other_household, name="Mow lawn")
        ChoreLog.objects.create(
            chore=other_chore, person=other_person, date=self.today, status=ChoreLog.Status.DONE
        )

    def _history_url(self, **params):
        url = reverse("household_history", kwargs={"slug": self.household.slug})
        if params:
            url += "?" + "&".join(f"{k}={v}" for k, v in params.items())
        return url

    def test_no_filters_returns_all_logs_ordered_by_date_then_chore(self):
        response = self.client.get(self._history_url())
        logs = list(response.context["logs"])
        self.assertEqual(logs, [self.log_mom_today, self.log_kid_today, self.log_mom_old])

    def test_filter_by_person(self):
        response = self.client.get(self._history_url(person=self.mom.id))
        logs = list(response.context["logs"])
        self.assertEqual(set(logs), {self.log_mom_today, self.log_mom_old})

    def test_filter_by_date_range(self):
        response = self.client.get(
            self._history_url(start=self.today.isoformat(), end=self.today.isoformat())
        )
        logs = list(response.context["logs"])
        self.assertEqual(set(logs), {self.log_mom_today, self.log_kid_today})

    def test_malformed_date_filter_is_ignored_not_500(self):
        response = self.client.get(self._history_url(start="not-a-date"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["logs"]), 3)

    def test_logs_from_other_household_excluded(self):
        response = self.client.get(self._history_url())
        chores = {log.chore.name for log in response.context["logs"]}
        self.assertNotIn("Mow lawn", chores)
