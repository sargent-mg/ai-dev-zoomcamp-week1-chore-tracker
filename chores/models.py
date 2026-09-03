import uuid

from django.db import models


class Household(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=40, unique=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Person(models.Model):
    household = models.ForeignKey(Household, on_delete=models.CASCADE, related_name="people")
    name = models.CharField(max_length=100)

    class Meta:
        verbose_name_plural = "people"

    def __str__(self):
        return self.name


class Chore(models.Model):
    household = models.ForeignKey(Household, on_delete=models.CASCADE, related_name="chores")
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class ChoreAssignment(models.Model):
    chore = models.OneToOneField(Chore, on_delete=models.CASCADE, related_name="assignment")
    person = models.ForeignKey(Person, on_delete=models.CASCADE, related_name="chore_assignments")

    def __str__(self):
        return f"{self.chore} -> {self.person}"


class ChoreLog(models.Model):
    class Status(models.TextChoices):
        DONE = "done", "Done"
        MISSED = "missed", "Missed"

    chore = models.ForeignKey(Chore, on_delete=models.CASCADE, related_name="logs")
    person = models.ForeignKey(Person, on_delete=models.CASCADE, related_name="chore_logs")
    date = models.DateField()
    status = models.CharField(max_length=10, choices=Status.choices)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["chore", "date"], name="unique_chore_log_per_day"),
        ]
        ordering = ["-date"]

    def __str__(self):
        return f"{self.chore} — {self.date} ({self.status})"
