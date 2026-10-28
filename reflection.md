# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

The UML (`diagrams/uml.mmd`) splits the system into a data model and a planning layer:

- `Owner` — name, preferences, and the pets they own.
- `Pet` — name, species, and its list of `Task`s.
- `Task` — title, duration, `Priority` (enum: LOW/MEDIUM/HIGH), and optional recurrence fields.
- `Scheduler` — stateless-ish planning logic: sorts tasks, resolves conflicts, and fits as many as possible into an available-time budget.
- `DailyPlan` — the output of a scheduling run: a list of `ScheduledTask`s, with `total_time()` and `explain()`.
- `ScheduledTask` — a `Task` placed at a specific start/end time, with a `reason` string.

The split keeps "what a task is" (data) separate from "how a plan gets built" (algorithm) and separate again from "what the plan looked like" (result), so each class has one job.

**b. Design changes**

The README originally suggested conflict handling meant "overlapping time slots." In practice, `Scheduler.generate_plan` assigns start times itself by laying tasks out sequentially — it never receives tasks with pre-existing fixed times from the user — so two tasks can never actually overlap. I changed `_resolve_conflicts` to instead catch duplicate task IDs (e.g., the same task accidentally added twice), which is the conflict that can actually occur given how tasks enter the system today.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

The scheduler considers two constraints: **available time** (a minute budget for the day) and **task priority** (high/medium/low). `Owner.preferences` exists in the data model but isn't consulted by the scheduler yet — that's a real gap, not a finished feature. Priority mattered most because the scenario is explicitly about a busy owner who can't do everything; time was the hard constraint that makes picking matter at all.

**b. Tradeoffs**

The scheduler is greedy: it sorts by priority then duration, and fills the time budget in that order (`_sort_tasks` → `_select_within_time`). This can be suboptimal in the knapsack sense — e.g., a combination of two lower-priority tasks might use the remaining time more fully than the one it picks — but it's simple, fast (O(n log n)), and matches the intuitive expectation that "important things come first," which is more important than squeezing out every last minute for this scenario.

---

## 3. AI Collaboration

**a. How you used AI**

I used Claude Code throughout: translating the README scenario into the UML class diagram, converting that UML into class stubs, implementing the scheduling algorithm, writing the pytest suite, and wiring the Streamlit UI to the backend. The most useful pattern was asking for one "next step" at a time (per the README's suggested workflow) instead of asking for the whole app at once — each step produced a small, reviewable, testable chunk before moving on.

**b. Judgment and verification**

Honestly, in this session I accepted each step as the AI produced it rather than rejecting a suggestion outright — verification mostly took the form of running the test suite (11/11 passing) and  running the scheduler logic to check the output against expected behavior, rather than disagreeing with a design choice. 

---

## 4. Testing and Verification

**a. What you tested**

`test_pawpal.py` covers: container operations (adding/removing tasks and pets), sort order (priority first, duration as a tiebreaker), time-budget filtering (including a zero-budget edge case), duplicate-task-ID conflict removal, the full `generate_plan` sequential scheduling (correct start/end times), `total_time()` summation, and that `explain()` actually names the scheduled tasks and pet. These map directly to the README's "Smarter Scheduling" behaviors (sorting, filtering, conflict handling) plus the boundary conditions most likely to hide bugs.

**b. Confidence**

Fairly confident in the core path — 11/11 tests pass, including the exact-fit boundary (`duration_minutes <= remaining`) and the zero-budget edge case. Untested edge cases I'd add next: two tasks with identical priority *and* duration (is sort order stable/predictable?), a single task longer than the entire available-time budget, `generate_plan` with an empty task list, and recurring-task expansion once that logic actually exists (currently `is_recurring` is just a flag the scheduler ignores).

---

## 5. Reflection

**a. What went well**

Going UML → stubs → logic → tests → UI in that order meant each piece was small and verifiable on its own; by the time the Streamlit button was wired up, the scheduling logic underneath it was already tested and trusted, so the last step was just plumbing, not debugging.

**b. What you would improve**

Two real gaps to close with another iteration: `Owner.preferences` is defined but never used by the scheduler, and `Task.is_recurring`/`recurrence_pattern` are stored but never expanded into an actual multi-day plan. Both were modeled in the UML up front but not implemented — a good reminder that a UML field isn't the same as a working feature.

**c. Key takeaway**
I found that designing the UML before actually writing code helped me understand how my project will actually run. Implementing later did not take long because I started out with a solid plan.
