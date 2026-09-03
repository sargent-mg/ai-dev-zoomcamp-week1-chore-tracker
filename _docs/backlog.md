# Backlog — Household Chore Tracker (Django v1)

Derived from [_docs/plan.md](_docs/plan.md).

## 1. Data models
- [ ] `Household` model (a household has a shared link/slug, no auth)
- [ ] `Person` model (name, belongs to a `Household`, no password)
- [ ] `Chore` model (name, belongs to a `Household`, fixed daily recurrence)
- [ ] `ChoreAssignment` — links a `Chore` to a `Person` (fixed, permanent assignment, not rotating)
- [ ] `ChoreLog` — one entry per chore per day: status (`done` / `missed`), timestamp, done by

## 2. Household access (no login)
- [ ] Route to create a new household (generates a shareable link/slug)
- [ ] Landing page for a household link: list of people, "pick your name" to identify as that person for the session
- [ ] Store the picked person in the session (no accounts/passwords)

## 3. Chore & person setup
- [ ] View/form to add people to a household
- [ ] View/form to add chores to a household
- [ ] View/form to assign a chore to a person (fixed assignment, editable by anyone in the household)

## 4. Daily chore list (shared view)
- [ ] View showing all chores for the household today, with assignee and status
- [ ] Self check-off action: mark a chore done as the currently identified person (honor system, no approval step)
- [ ] Prevent marking someone else's chore as done (or decide if that's allowed — check against plan's "self check-off")

## 5. Missed chore handling
- [ ] Daily job/management command (or lazy check on page load) that marks yesterday's incomplete chores as "missed"
- [ ] No notifications/escalation — just log the missed status in history

## 6. History view
- [ ] Page showing past days' chore completion/missed status per person
- [ ] Simple filter by person or by date range (optional, keep minimal)

## 7. UI / responsive web app
- [ ] Base responsive template (mobile-friendly, no app install)
- [ ] Wire up templates for household landing, daily list, history

## 8. Admin & housekeeping
- [ ] Register models in Django admin for easy debugging/data entry
- [ ] Seed/fixture data or management command for quick local testing
- [ ] Basic tests: model behavior (missed-chore logic), check-off view, session-based person identification

## Explicitly out of scope (do not build)
- Chore rotation between people
- Points/rewards/gamification
- Push notifications
- Photo proof or parent approval workflows
- Full email/password authentication
- Escalation or notify-others logic for missed chores
