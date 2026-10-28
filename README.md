# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## What you will build

Your final app should:

- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.

## 🖥️ Sample Output

Given a pet "Mochi" (dog) with tasks Feeding (10 min, high), Morning walk (20 min, high), and
Playtime (45 min, low), and 60 available minutes, `Scheduler.generate_plan(...)` produces:

```
Daily plan for Mochi (dog) on 2026-10-27:
  08:00 — Feeding (10 min) [priority: high] — Scheduled by high priority (10 min fits remaining time budget)
  08:10 — Morning walk (20 min) [priority: high] — Scheduled by high priority (20 min fits remaining time budget)
```

Playtime is correctly left out ("Could not fit: Playtime") since only 30 of the 60 available
minutes are left after the two high-priority tasks and it needs 45.

## 🧪 Testing PawPal+

```bash
# Run the full test suite:
pytest

# Run with coverage:
pytest --cov
```

Sample test output:

```
============================= test session starts =============================
collected 11 items

test_pawpal.py::test_add_task_appends_to_pet PASSED                      [  9%]
test_pawpal.py::test_remove_task_drops_matching_id PASSED                [ 18%]
test_pawpal.py::test_add_pet_appends_to_owner PASSED                     [ 27%]
test_pawpal.py::test_sort_tasks_orders_by_priority_then_duration PASSED  [ 36%]
test_pawpal.py::test_select_within_time_skips_tasks_that_dont_fit PASSED [ 45%]
test_pawpal.py::test_select_within_time_with_zero_budget_selects_nothing PASSED [ 54%]
test_pawpal.py::test_resolve_conflicts_removes_duplicate_task_ids PASSED [ 63%]
test_pawpal.py::test_generate_plan_builds_sequential_schedule_starting_at_given_time PASSED [ 72%]
test_pawpal.py::test_generate_plan_excludes_tasks_that_exceed_available_time PASSED [ 81%]
test_pawpal.py::test_daily_plan_total_time_sums_scheduled_tasks PASSED   [ 90%]
test_pawpal.py::test_daily_plan_explain_includes_each_task_title PASSED  [100%]

============================= 11 passed in 0.18s ==============================
```

## 📐 Smarter Scheduling

| Feature | Method(s) | Notes |
|---------|-----------|-------|
| Task sorting | `Scheduler._sort_tasks` | Sorts by priority (high → medium → low), then by shorter duration as a tiebreaker |
| Filtering | `Scheduler._select_within_time` | Greedily walks the sorted list and skips any task whose duration would exceed the remaining time budget |
| Conflict handling | `Scheduler._resolve_conflicts` | Drops duplicate task IDs before scheduling so the same task can't be double-booked |
| Recurring tasks | `Task.is_recurring`, `Task.recurrence_pattern` | Data model supports marking a task as recurring (e.g. `"daily"`); the scheduler does not yet expand recurrence across multiple days — a good next increment |

## 📸 Demo Walkthrough

Describe your app in numbered steps so a reader can follow along without watching a video:

1. Run `streamlit run app.py` and open the app in your browser.
2. Enter the owner's name, the pet's name, and the species at the top of the page.
3. Under "Tasks", use the editable table to add a task (fill in the blank "+" row), edit any cell, or delete a row — title, duration (minutes), and priority are all editable inline.
4. Under "Build Schedule", set **Available time today (minutes)** to the time budget for the day.
5. Click **Generate schedule**. The app builds an `Owner`/`Pet`/`Task` model from your inputs, runs `Scheduler.generate_plan(...)`, and displays the resulting plan (start times, durations, priorities, and the reason each task was placed) via `DailyPlan.explain()`.
6. If any tasks didn't fit in the available time, they're listed under "Could not fit" so you can see what the scheduler had to leave out.

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or link to a demo video here -->
