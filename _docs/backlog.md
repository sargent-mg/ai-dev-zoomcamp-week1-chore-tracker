# Backlog — Household Chore Tracker (Django v1)

Derived from [_docs/plan.md](_docs/plan.md).

## 1. Data models
- [x] `Household` model (a household has a shared link/slug, no auth)
- [x] `Person` model (name, belongs to a `Household`, no password)
- [x] `Chore` model (name, belongs to a `Household`, fixed daily recurrence)
- [x] `ChoreAssignment` — links a `Chore` to a `Person` (fixed, permanent assignment, not rotating)
- [x] `ChoreLog` — one entry per chore per day: status (`done` / `missed`), timestamp, done by

## 2. Household access (no login)
- [x] Route to create a new household (generates a shareable link/slug)
- [x] Landing page for a household link: list of people, "pick your name" to identify as that person for the session
- [x] Store the picked person in the session (no accounts/passwords)

## 3. Chore & person setup
- [x] View/form to add people to a household
- [x] View/form to add chores to a household
- [x] View/form to assign a chore to a person (fixed assignment, editable by anyone in the household)

## 4. Daily chore list (shared view)
- [x] View showing all chores for the household today, with assignee and status
- [x] Self check-off action: mark a chore done as the currently identified person (honor system, no approval step)
- [x] Prevent marking someone else's chore as done (only the assigned person sees/can use the "Mark done" button)

## 5. Missed chore handling
- [x] Daily job/management command (`mark_missed_chores`, defaults to yesterday) that marks incomplete assigned chores as "missed"
- [x] No notifications/escalation — just log the missed status in history

## 6. History view
- [x] Page showing past days' chore completion/missed status per person
- [x] Simple filter by person or by date range

## 7. UI / responsive web app
- [x] Base responsive template (mobile-friendly, no app install)
- [x] Wire up templates for household landing, daily list, history

## 8. Admin & housekeeping
- [x] Register models in Django admin for easy debugging/data entry
- [x] Seed/fixture data or management command for quick local testing (`seed_demo`)
- [x] Basic tests: model behavior (missed-chore logic), check-off view, session-based person identification

## Explicitly out of scope (do not build)
- Chore rotation between people
- Points/rewards/gamification
- Push notifications
- Photo proof or parent approval workflows
- Full email/password authentication
- Escalation or notify-others logic for missed chores
