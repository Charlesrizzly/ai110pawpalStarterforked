"""PawPal+ - Pet Care Task Scheduler"""

import streamlit as st
import pandas as pd
from src.models import TimeWindow, Task, Pet, Owner
from src.scheduler import Scheduler

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="wide")

# Initialize session state
if "tasks" not in st.session_state:
    st.session_state.tasks = []
if "windows" not in st.session_state:
    st.session_state.windows = []

# Header
st.title("🐾 PawPal+")
st.markdown("**Your Pet Care Task Scheduler** - Plan your pet care tasks based on your availability and priorities")

st.divider()

# Main layout: Two columns
col_input, col_output = st.columns([1, 1])

with col_input:
    st.header("📝 Input")

    # Owner & Pet Information
    with st.expander("👤 Owner & Pet Info", expanded=True):
        owner_name = st.text_input("Owner name", value="Jordan", key="owner_name")

        col_pet1, col_pet2 = st.columns(2)
        with col_pet1:
            pet_name = st.text_input("Pet name", value="Mochi", key="pet_name")
        with col_pet2:
            species = st.selectbox("Species", ["dog", "cat", "other"], key="species")

    # Availability Windows
    with st.expander("⏰ Your Availability Windows", expanded=True):
        st.caption("Add time windows when you're available to care for your pet")

        col_w1, col_w2, col_w3, col_w4 = st.columns(4)
        with col_w1:
            start_hour = st.number_input("Start hour", min_value=0, max_value=23, value=6, key="start_hour")
        with col_w2:
            start_min = st.number_input("Start min", min_value=0, max_value=59, value=0, step=15, key="start_min")
        with col_w3:
            end_hour = st.number_input("End hour", min_value=0, max_value=23, value=8, key="end_hour")
        with col_w4:
            end_min = st.number_input("End min", min_value=0, max_value=59, value=0, step=15, key="end_min")

        col_btn1, col_btn2 = st.columns([1, 3])
        with col_btn1:
            if st.button("➕ Add Window"):
                try:
                    window = TimeWindow(
                        start_hour=start_hour,
                        start_minute=start_min,
                        end_hour=end_hour,
                        end_minute=end_min
                    )
                    st.session_state.windows.append({
                        "start_hour": start_hour,
                        "start_minute": start_min,
                        "end_hour": end_hour,
                        "end_minute": end_min,
                        "display": window.to_display_string()
                    })
                    st.success(f"Added window: {window.to_display_string()}")
                except ValueError as e:
                    st.error(f"Invalid window: {e}")

        with col_btn2:
            if st.button("🗑️ Clear All Windows"):
                st.session_state.windows = []
                st.rerun()

        if st.session_state.windows:
            st.write("**Current windows:**")
            window_df = pd.DataFrame(st.session_state.windows)
            st.dataframe(window_df[["display"]], use_container_width=True, hide_index=True)

            total_mins = sum(
                (w["end_hour"] * 60 + w["end_minute"]) - (w["start_hour"] * 60 + w["start_minute"])
                for w in st.session_state.windows
            )
            st.info(f"💡 Total available time: **{total_mins} minutes** ({total_mins / 60:.1f} hours)")
        else:
            st.warning("⚠️ No availability windows added yet")

    # Tasks
    with st.expander("✅ Pet Care Tasks", expanded=True):
        st.caption("Add tasks with duration and priority (5=highest, 1=lowest)")

        col_t1, col_t2, col_t3 = st.columns([3, 2, 2])
        with col_t1:
            task_title = st.text_input("Task title", value="Morning walk", key="task_title")
        with col_t2:
            duration = st.number_input("Duration (min)", min_value=1, max_value=240, value=30, key="duration")
        with col_t3:
            priority_num = st.number_input("Priority (1-5)", min_value=1, max_value=5, value=5, key="priority")

        col_btn3, col_btn4 = st.columns([1, 3])
        with col_btn3:
            if st.button("➕ Add Task"):
                try:
                    task = Task(title=task_title, duration_minutes=int(duration), priority=int(priority_num))
                    st.session_state.tasks.append({
                        "title": task_title,
                        "duration_minutes": int(duration),
                        "priority": int(priority_num)
                    })
                    st.success(f"Added task: {task_title}")
                except ValueError as e:
                    st.error(f"Invalid task: {e}")

        with col_btn4:
            if st.button("🗑️ Clear All Tasks"):
                st.session_state.tasks = []
                st.rerun()

        if st.session_state.tasks:
            st.write("**Current tasks:**")
            tasks_df = pd.DataFrame(st.session_state.tasks)
            # Sort by priority descending for display
            tasks_df = tasks_df.sort_values("priority", ascending=False)
            st.dataframe(tasks_df, use_container_width=True, hide_index=True)

            total_task_mins = sum(t["duration_minutes"] for t in st.session_state.tasks)
            st.info(f"💡 Total task time needed: **{total_task_mins} minutes** ({total_task_mins / 60:.1f} hours)")
        else:
            st.warning("⚠️ No tasks added yet")

    # Generate Schedule Button
    st.divider()
    generate_btn = st.button("🎯 **Generate Schedule**", type="primary", use_container_width=True)

with col_output:
    st.header("📅 Schedule Results")

    if generate_btn:
        # Validate inputs
        if not owner_name.strip():
            st.error("❌ Please enter an owner name")
        elif not pet_name.strip():
            st.error("❌ Please enter a pet name")
        elif not st.session_state.windows:
            st.error("❌ Please add at least one availability window")
        elif not st.session_state.tasks:
            st.error("❌ Please add at least one task")
        else:
            try:
                # Create domain objects
                owner = Owner(
                    name=owner_name,
                    availability_windows=[
                        TimeWindow(
                            start_hour=w["start_hour"],
                            start_minute=w["start_minute"],
                            end_hour=w["end_hour"],
                            end_minute=w["end_minute"]
                        )
                        for w in st.session_state.windows
                    ]
                )

                pet = Pet(name=pet_name, species=species)

                tasks = [
                    Task(
                        title=t["title"],
                        duration_minutes=t["duration_minutes"],
                        priority=t["priority"]
                    )
                    for t in st.session_state.tasks
                ]

                # Run scheduler
                scheduler = Scheduler(owner, pet, tasks)
                result = scheduler.generate_schedule()

                # Store result in session state
                st.session_state.result = result

                # Display success message
                st.success(f"✅ Schedule generated for **{pet_name}** the {species}!")

            except ValueError as e:
                st.error(f"❌ Validation error: {e}")
            except Exception as e:
                st.error(f"❌ Error generating schedule: {e}")

    # Display results if available
    if "result" in st.session_state:
        result = st.session_state.result

        # Summary metrics
        col_m1, col_m2, col_m3 = st.columns(3)
        with col_m1:
            st.metric("✅ Scheduled", len(result.scheduled_tasks))
        with col_m2:
            st.metric("⏭️ Skipped", len(result.skipped_tasks))
        with col_m3:
            st.metric("📊 Utilization", f"{result.utilization_percentage():.1f}%")

        st.divider()

        # Scheduled Tasks
        if result.scheduled_tasks:
            st.subheader("✅ Scheduled Tasks")
            scheduled_data = []
            for st_task in result.scheduled_tasks:
                scheduled_data.append({
                    "Time": st_task.time_range_string(),
                    "Task": st_task.task.title,
                    "Duration": f"{st_task.task.duration_minutes} min",
                    "Priority": st_task.task.priority,
                    "Window": st_task.window_display()
                })

            scheduled_df = pd.DataFrame(scheduled_data)
            st.dataframe(scheduled_df, use_container_width=True, hide_index=True)
        else:
            st.info("No tasks were scheduled")

        # Skipped Tasks
        if result.skipped_tasks:
            st.subheader("⏭️ Skipped Tasks")
            skipped_data = []
            for task in result.skipped_tasks:
                skipped_data.append({
                    "Task": task.title,
                    "Duration": f"{task.duration_minutes} min",
                    "Priority": task.priority,
                    "Reason": "Insufficient time in available windows"
                })

            skipped_df = pd.DataFrame(skipped_data)
            st.dataframe(skipped_df, use_container_width=True, hide_index=True)

        # Explanation
        with st.expander("📖 Detailed Explanation", expanded=True):
            st.markdown("```\n" + result.explanation + "\n```")

        # Summary
        with st.expander("📊 Summary Statistics"):
            st.write(f"**Total Available Time:** {result.total_available_minutes} minutes")
            st.write(f"**Total Scheduled Time:** {result.total_scheduled_minutes} minutes")
            st.write(f"**Remaining Time:** {result.total_available_minutes - result.total_scheduled_minutes} minutes")
            st.write(f"**Utilization:** {result.utilization_percentage():.1f}%")

            if result.scheduled_tasks:
                st.write(f"**Average Task Duration:** {result.total_scheduled_minutes / len(result.scheduled_tasks):.1f} minutes")
    else:
        st.info("👈 Enter your availability windows and tasks, then click **Generate Schedule** to see results!")

        # Show example
        with st.expander("💡 Example Usage"):
            st.markdown("""
            **Try this example:**

            1. **Availability Windows:**
               - Morning: 6:00 - 8:00 (2 hours)
               - Evening: 17:00 - 21:00 (4 hours)

            2. **Tasks:**
               - Morning walk (30 min, priority 5)
               - Feeding (10 min, priority 5)
               - Medicine (5 min, priority 4)
               - Play time (60 min, priority 3)
               - Grooming (45 min, priority 2)
               - Training (30 min, priority 1)

            3. Click **Generate Schedule** to see which tasks fit!
            """)

# Footer
st.divider()
st.caption("🐾 PawPal+ - Built with ❤️ using Streamlit | Priority-based greedy scheduling algorithm")
