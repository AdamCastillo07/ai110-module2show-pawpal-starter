import streamlit as st

from pawpal import Owner, Pet, Priority, Scheduler, Task

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")

st.markdown(
    """
**PawPal+** helps a pet owner plan daily care tasks for their pet based on
available time and task priority.
"""
)

with st.expander("How it works", expanded=False):
    st.markdown(
        """
- Enter the owner and pet info below.
- Add, edit, or remove care tasks (title, duration, priority) in the table.
- Set how much time is available today.
- Click **Generate schedule** to build a plan: tasks are ordered by priority
  (ties broken by shorter duration), then fit into the available time.
  Anything that doesn't fit is listed separately.
"""
    )

st.divider()

st.subheader("Quick Demo Inputs (UI only)")
owner_name = st.text_input("Owner name", value="Jordan")
pet_name = st.text_input("Pet name", value="Mochi")
species = st.selectbox("Species", ["dog", "cat", "other"])

st.markdown("### Tasks")
st.caption("Add, edit, or remove tasks directly in the table (use the + row to add a task).")

if "tasks" not in st.session_state:
    st.session_state.tasks = [
        {"title": "Morning walk", "duration_minutes": 20, "priority": "high"},
    ]

edited_tasks = st.data_editor(
    st.session_state.tasks,
    num_rows="dynamic",
    use_container_width=True,
    key="tasks_editor",
    column_config={
        "title": st.column_config.TextColumn("Task title", required=True),
        "duration_minutes": st.column_config.NumberColumn(
            "Duration (minutes)", min_value=1, max_value=240, required=True
        ),
        "priority": st.column_config.SelectboxColumn(
            "Priority", options=["low", "medium", "high"], required=True
        ),
    },
)
st.session_state.tasks = edited_tasks

valid_tasks = [
    t
    for t in st.session_state.tasks
    if t.get("title") and t.get("duration_minutes") and t.get("priority")
]
if not valid_tasks:
    st.info("No tasks yet. Add a row above.")

st.divider()

st.subheader("Build Schedule")
st.caption("Set how much time is available today, then generate a plan from the tasks above.")

available_minutes = st.number_input(
    "Available time today (minutes)", min_value=10, max_value=600, value=60
)

if st.button("Generate schedule"):
    if not valid_tasks:
        st.warning("Add at least one complete task before generating a schedule.")
    else:
        pet = Pet(name=pet_name, species=species)
        for i, t in enumerate(valid_tasks):
            pet.add_task(
                Task(
                    id=str(i),
                    title=t["title"],
                    duration_minutes=t["duration_minutes"],
                    priority=Priority(t["priority"]),
                )
            )
        owner = Owner(name=owner_name)
        owner.add_pet(pet)

        scheduler = Scheduler(available_minutes=int(available_minutes))
        plan = scheduler.generate_plan(pet, available_minutes=int(available_minutes))

        if plan.items:
            st.success(
                f"Generated a plan using {plan.total_time()} of {int(available_minutes)} "
                "available minutes."
            )
            st.code(plan.explain())
        else:
            st.warning("No tasks fit in the available time.")

        scheduled_ids = {item.task.id for item in plan.items}
        unscheduled = [t for t in pet.tasks if t.id not in scheduled_ids]
        if unscheduled:
            st.caption("Could not fit: " + ", ".join(t.title for t in unscheduled))
