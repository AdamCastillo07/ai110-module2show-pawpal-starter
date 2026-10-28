"""PawPal+ class stubs — structure only, no scheduling logic yet.

Mirrors diagrams/uml.mmd. Fill in method bodies as you implement each piece.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, time
from enum import Enum


class Priority(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


@dataclass
class Task:
    id: str
    title: str
    duration_minutes: int
    priority: Priority
    is_recurring: bool = False
    recurrence_pattern: str | None = None


@dataclass
class Pet:
    name: str
    species: str
    tasks: list[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        self.tasks.append(task)

    def remove_task(self, task_id: str) -> None:
        self.tasks = [t for t in self.tasks if t.id != task_id]


@dataclass
class Owner:
    name: str
    preferences: dict = field(default_factory=dict)
    pets: list[Pet] = field(default_factory=list)

    def add_pet(self, pet: Pet) -> None:
        self.pets.append(pet)


@dataclass
class ScheduledTask:
    task: Task
    start_time: time
    end_time: time
    reason: str = ""


@dataclass
class DailyPlan:
    plan_date: date
    pet: Pet
    items: list[ScheduledTask] = field(default_factory=list)

    def add_item(self, item: ScheduledTask) -> None:
        self.items.append(item)

    def total_time(self) -> int:
        return sum(item.task.duration_minutes for item in self.items)

    def explain(self) -> str:
        lines = [f"Daily plan for {self.pet.name} ({self.pet.species}) on {self.plan_date}:"]
        for item in self.items:
            start = item.start_time.strftime("%H:%M")
            lines.append(
                f"  {start} — {item.task.title} ({item.task.duration_minutes} min) "
                f"[priority: {item.task.priority.value}] — {item.reason}"
            )
        return "\n".join(lines)


_PRIORITY_ORDER = {Priority.HIGH: 0, Priority.MEDIUM: 1, Priority.LOW: 2}

_DEFAULT_START_TIME = time(hour=8, minute=0)


class Scheduler:
    def __init__(self, available_minutes: int):
        self.available_minutes = available_minutes

    def generate_plan(
        self,
        pet: Pet,
        available_minutes: int,
        plan_date: date | None = None,
        start_time: time = _DEFAULT_START_TIME,
    ) -> DailyPlan:
        plan_date = plan_date or date.today()
        plan = DailyPlan(plan_date=plan_date, pet=pet)

        candidates = self._resolve_conflicts(pet.tasks)
        ordered = self._sort_tasks(candidates)
        selected = self._select_within_time(ordered, available_minutes)

        minutes_elapsed = 0
        for task in selected:
            start_minutes = start_time.hour * 60 + start_time.minute + minutes_elapsed
            end_minutes = start_minutes + task.duration_minutes
            plan.add_item(
                ScheduledTask(
                    task=task,
                    start_time=time(hour=(start_minutes // 60) % 24, minute=start_minutes % 60),
                    end_time=time(hour=(end_minutes // 60) % 24, minute=end_minutes % 60),
                    reason=f"Scheduled by {task.priority.value} priority "
                    f"({task.duration_minutes} min fits remaining time budget)",
                )
            )
            minutes_elapsed += task.duration_minutes

        return plan

    def _sort_tasks(self, tasks: list[Task]) -> list[Task]:
        return sorted(
            tasks,
            key=lambda t: (_PRIORITY_ORDER[t.priority], t.duration_minutes),
        )

    def _select_within_time(self, tasks: list[Task], available_minutes: int) -> list[Task]:
        selected: list[Task] = []
        remaining = available_minutes
        for task in tasks:
            if task.duration_minutes <= remaining:
                selected.append(task)
                remaining -= task.duration_minutes
        return selected

    def _resolve_conflicts(self, tasks: list[Task]) -> list[Task]:
        seen_ids: set[str] = set()
        unique_tasks: list[Task] = []
        for task in tasks:
            if task.id not in seen_ids:
                seen_ids.add(task.id)
                unique_tasks.append(task)
        return unique_tasks
