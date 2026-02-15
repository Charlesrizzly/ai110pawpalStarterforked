"""Core scheduling engine for PawPal+."""

from typing import Optional
from src.models import Owner, Pet, Task
from src.schedule_result import ScheduleResult, ScheduledTask


class Scheduler:
    """Core scheduling engine that generates optimal task schedules.

    Attributes:
        owner: The pet owner with availability windows
        pet: The pet being cared for
        tasks: List of tasks to schedule
    """

    def __init__(self, owner: Owner, pet: Pet, tasks: list[Task]) -> None:
        """Initialize the scheduler with owner, pet, and tasks.

        Args:
            owner: Pet owner with availability information
            pet: Pet requiring care
            tasks: List of tasks to be scheduled
        """
        self._owner = owner
        self._pet = pet
        self._tasks = tasks

    def generate_schedule(self) -> ScheduleResult:
        """Generate an optimized schedule based on priorities and constraints.

        Returns:
            ScheduleResult containing scheduled tasks, skipped tasks, and explanation
        """
        # Step 1: Validate inputs
        self._validate_inputs()

        # Step 2: Handle edge case - no tasks
        if not self._tasks:
            return ScheduleResult(
                scheduled_tasks=[],
                skipped_tasks=[],
                total_scheduled_minutes=0,
                total_available_minutes=self._owner.total_available_minutes(),
                explanation="No tasks to schedule."
            )

        # Step 3: Handle edge case - no available time
        if not self._owner.availability_windows:
            return ScheduleResult(
                scheduled_tasks=[],
                skipped_tasks=list(self._tasks),
                total_scheduled_minutes=0,
                total_available_minutes=0,
                explanation="No availability windows provided. All tasks skipped."
            )

        # Step 4: Sort tasks by priority (highest first)
        sorted_tasks = self._sort_tasks_by_priority()

        # Step 5: Initialize window state tracking
        windows_state = []
        for i, window in enumerate(self._owner.availability_windows):
            windows_state.append({
                "window_index": i,
                "window": window,
                "remaining_start_minutes": window.start_minutes_from_midnight(),
                "remaining_minutes": window.duration_minutes(),
            })

        # Step 6: Try to schedule each task
        scheduled_tasks = []
        skipped_tasks = []

        for task in sorted_tasks:
            success, scheduled_task = self._try_fit_task(task, windows_state)
            if success and scheduled_task:
                scheduled_tasks.append(scheduled_task)
            else:
                skipped_tasks.append(task)

        # Step 7: Calculate total scheduled time
        total_scheduled_minutes = sum(st.task.duration_minutes for st in scheduled_tasks)
        total_available_minutes = self._owner.total_available_minutes()

        # Step 8: Generate explanation
        explanation = self._generate_explanation(scheduled_tasks, skipped_tasks)

        # Step 9: Return result
        return ScheduleResult(
            scheduled_tasks=scheduled_tasks,
            skipped_tasks=skipped_tasks,
            total_scheduled_minutes=total_scheduled_minutes,
            total_available_minutes=total_available_minutes,
            explanation=explanation
        )

    def _validate_inputs(self) -> None:
        """Validate that all inputs are valid before scheduling."""
        # Owner, Pet, and Task validation happens in their __post_init__ methods
        # This method can perform additional cross-validation if needed
        if self._owner is None:
            raise ValueError("Owner cannot be None")
        if self._pet is None:
            raise ValueError("Pet cannot be None")
        if self._tasks is None:
            raise ValueError("Tasks list cannot be None")

    def _sort_tasks_by_priority(self) -> list[Task]:
        """Sort tasks by priority in descending order (highest first).

        Returns:
            Sorted list of tasks
        """
        # Use sorted() with reverse=True to get descending order (5, 4, 3, 2, 1)
        # The Task.__lt__ method compares priorities, so sorting in reverse gives highest first
        return sorted(self._tasks, key=lambda t: t.priority, reverse=True)

    def _try_fit_task(self, task: Task, windows_state: list[dict]) -> tuple[bool, Optional[ScheduledTask]]:
        """Attempt to fit a task into the first available window.

        Args:
            task: The task to schedule
            windows_state: Current state of all windows (remaining time, etc.)

        Returns:
            Tuple of (success: bool, scheduled_task: ScheduledTask or None)
        """
        # Try to fit task in first available window with sufficient space
        for window_state in windows_state:
            if window_state["remaining_minutes"] >= task.duration_minutes:
                # Task fits in this window!

                # Calculate start time (current position in this window)
                start_minutes = window_state["remaining_start_minutes"]
                start_hour = start_minutes // 60
                start_minute = start_minutes % 60

                # Calculate end time
                end_minutes = start_minutes + task.duration_minutes
                end_hour = end_minutes // 60
                end_minute = end_minutes % 60

                # Create scheduled task
                scheduled_task = ScheduledTask(
                    task=task,
                    window_index=window_state["window_index"],
                    start_hour=start_hour,
                    start_minute=start_minute,
                    end_hour=end_hour,
                    end_minute=end_minute
                )

                # Update window state
                window_state["remaining_start_minutes"] = end_minutes
                window_state["remaining_minutes"] -= task.duration_minutes

                return (True, scheduled_task)

        # Task doesn't fit in any window
        return (False, None)

    def _generate_explanation(self, scheduled: list[ScheduledTask], skipped: list[Task]) -> str:
        """Generate human-readable explanation of scheduling decisions.

        Args:
            scheduled: List of successfully scheduled tasks
            skipped: List of tasks that couldn't be scheduled

        Returns:
            Formatted explanation string
        """
        lines = []

        # Opening
        lines.append(f"Schedule generated for {self._pet.name} the {self._pet.species}.")
        lines.append("")

        # Scheduling strategy
        lines.append("Scheduling Strategy:")
        lines.append("- Tasks were scheduled in priority order (5=highest, 1=lowest)")
        lines.append("- Each task was placed in the earliest available time window with sufficient space")
        lines.append("")

        # Scheduled tasks summary
        if scheduled:
            lines.append(f"Successfully Scheduled: {len(scheduled)} task(s)")
            for st in scheduled:
                lines.append(
                    f"  • [Priority {st.task.priority}] {st.task.title} "
                    f"at {st.time_range_string()} ({st.task.duration_minutes} min)"
                )
        else:
            lines.append("Successfully Scheduled: 0 tasks")

        lines.append("")

        # Skipped tasks summary
        if skipped:
            lines.append(f"Skipped Tasks: {len(skipped)} task(s)")
            lines.append("The following tasks could not fit in the available time windows:")
            for task in skipped:
                lines.append(
                    f"  • [Priority {task.priority}] {task.title} "
                    f"({task.duration_minutes} min needed)"
                )
        else:
            lines.append("Skipped Tasks: None - all tasks were successfully scheduled!")

        return "\n".join(lines)
