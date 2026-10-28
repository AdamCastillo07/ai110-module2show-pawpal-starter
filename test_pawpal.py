from datetime import date, time

from pawpal import DailyPlan, Owner, Pet, Priority, Scheduler, Task


def make_task(id, title, duration_minutes, priority):
    return Task(id=id, title=title, duration_minutes=duration_minutes, priority=priority)


def test_add_task_appends_to_pet():
    pet = Pet(name="Mochi", species="dog")
    task = make_task("1", "Walk", 20, Priority.HIGH)

    pet.add_task(task)

    assert pet.tasks == [task]


def test_remove_task_drops_matching_id():
    pet = Pet(name="Mochi", species="dog")
    pet.add_task(make_task("1", "Walk", 20, Priority.HIGH))
    pet.add_task(make_task("2", "Feed", 10, Priority.HIGH))

    pet.remove_task("1")

    assert [t.id for t in pet.tasks] == ["2"]


def test_add_pet_appends_to_owner():
    owner = Owner(name="Jordan")
    pet = Pet(name="Mochi", species="dog")

    owner.add_pet(pet)

    assert owner.pets == [pet]


def test_sort_tasks_orders_by_priority_then_duration():
    scheduler = Scheduler(available_minutes=120)
    tasks = [
        make_task("1", "Playtime", 45, Priority.LOW),
        make_task("2", "Morning walk", 30, Priority.HIGH),
        make_task("3", "Feeding", 10, Priority.HIGH),
        make_task("4", "Grooming", 15, Priority.MEDIUM),
    ]

    ordered = scheduler._sort_tasks(tasks)

    assert [t.id for t in ordered] == ["3", "2", "4", "1"]


def test_select_within_time_skips_tasks_that_dont_fit():
    scheduler = Scheduler(available_minutes=60)
    tasks = [
        make_task("1", "Feeding", 10, Priority.HIGH),
        make_task("2", "Morning walk", 30, Priority.HIGH),
        make_task("3", "Playtime", 45, Priority.LOW),
    ]

    selected = scheduler._select_within_time(tasks, available_minutes=60)

    assert [t.id for t in selected] == ["1", "2"]


def test_select_within_time_with_zero_budget_selects_nothing():
    scheduler = Scheduler(available_minutes=0)
    tasks = [make_task("1", "Feeding", 10, Priority.HIGH)]

    selected = scheduler._select_within_time(tasks, available_minutes=0)

    assert selected == []


def test_resolve_conflicts_removes_duplicate_task_ids():
    scheduler = Scheduler(available_minutes=60)
    tasks = [
        make_task("1", "Feeding", 10, Priority.HIGH),
        make_task("1", "Feeding (duplicate)", 10, Priority.HIGH),
        make_task("2", "Walk", 20, Priority.HIGH),
    ]

    unique = scheduler._resolve_conflicts(tasks)

    assert [t.id for t in unique] == ["1", "2"]


def test_generate_plan_builds_sequential_schedule_starting_at_given_time():
    pet = Pet(name="Mochi", species="dog")
    pet.add_task(make_task("1", "Feeding", 10, Priority.HIGH))
    pet.add_task(make_task("2", "Morning walk", 30, Priority.HIGH))
    scheduler = Scheduler(available_minutes=60)

    plan = scheduler.generate_plan(
        pet, available_minutes=60, plan_date=date(2026, 1, 1), start_time=time(8, 0)
    )

    assert [item.task.id for item in plan.items] == ["1", "2"]
    assert plan.items[0].start_time == time(8, 0)
    assert plan.items[0].end_time == time(8, 10)
    assert plan.items[1].start_time == time(8, 10)
    assert plan.items[1].end_time == time(8, 40)


def test_generate_plan_excludes_tasks_that_exceed_available_time():
    pet = Pet(name="Mochi", species="dog")
    pet.add_task(make_task("1", "Feeding", 10, Priority.HIGH))
    pet.add_task(make_task("2", "Playtime", 45, Priority.LOW))
    scheduler = Scheduler(available_minutes=20)

    plan = scheduler.generate_plan(pet, available_minutes=20)

    assert [item.task.id for item in plan.items] == ["1"]


def test_daily_plan_total_time_sums_scheduled_tasks():
    pet = Pet(name="Mochi", species="dog")
    pet.add_task(make_task("1", "Feeding", 10, Priority.HIGH))
    pet.add_task(make_task("2", "Morning walk", 30, Priority.HIGH))
    scheduler = Scheduler(available_minutes=60)

    plan = scheduler.generate_plan(pet, available_minutes=60)

    assert plan.total_time() == 40


def test_daily_plan_explain_includes_each_task_title():
    pet = Pet(name="Mochi", species="dog")
    pet.add_task(make_task("1", "Feeding", 10, Priority.HIGH))
    scheduler = Scheduler(available_minutes=60)

    plan = scheduler.generate_plan(pet, available_minutes=60)
    explanation = plan.explain()

    assert "Feeding" in explanation
    assert "Mochi" in explanation
