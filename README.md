# Household Chore Tracker

A lean, no-login web app for a family to keep track of daily chores. Each household gets a shareable link; anyone with that link picks their name and can check off their own chores. See [_docs/plan.md](_docs/plan.md) for the full v1 scope and [_docs/backlog.md](_docs/backlog.md) for the implementation backlog.

## Stack

- Python 3.14, Django 6.1
- SQLite (dev)
- [uv](https://docs.astral.sh/uv/) for dependency management
- No frontend build step — server-rendered templates, vanilla CSS/JS

## Setup

Requires [uv](https://docs.astral.sh/uv/) installed locally.

```bash
uv sync
uv run python manage.py migrate
```

## Running the app

```bash
uv run python manage.py runserver
```

Visit http://localhost:8000/ to create a household, or load some sample data first:

```bash
uv run python manage.py seed_demo
```

This creates a "Demo Household" with three people, three assigned chores, and a bit of history, and prints its shareable URL.

## Running tests

```bash
uv run python manage.py test
```

With coverage:

```bash
uv run coverage run --source=chores manage.py test chores
uv run coverage report -m
```

## Marking missed chores

Chores with no check-off log for a given day can be marked "missed" via a management command — run it manually or on a daily cron/scheduled task:

```bash
uv run python manage.py mark_missed_chores          # marks yesterday's unlogged chores as missed
uv run python manage.py mark_missed_chores --date 2026-08-30
```

Unassigned chores are skipped (there's no one to attribute a miss to).

## Project structure

```
config/     Django project settings, root URLconf
chores/     The one app: models, views, forms, templates, tests, management commands
```

Key routes (all under `/h/<household-slug>/`):

| Route | Purpose |
|---|---|
| `/` | Create a new household |
| `/h/<slug>/` | Setup — add people/chores, assign chores, pick your name, share the link |
| `/h/<slug>/today/` | Today's chore list with self check-off |
| `/h/<slug>/history/` | Past completion/missed history, filterable by person and date |

There's no authentication — identity is just a name picked from the household's list, stored in the session.
