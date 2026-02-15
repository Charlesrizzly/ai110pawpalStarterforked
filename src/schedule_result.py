"""Result classes for schedule generation."""

from dataclasses import dataclass
from src.models import Task


@dataclass
class ScheduledTask:
    """Represents a task that has been placed in the schedule.

    Attributes:
        task: The original task being scheduled
        window_index: Which availability window this task is in
        start_hour: Scheduled start hour (0-23)
        start_minute: Scheduled start minute (0-59)
        end_hour: Scheduled end hour (0-23)
        end_minute: Scheduled end minute (0-59)
    """
    task: Task
    window_index: int
    start_hour: int
    start_minute: int
    end_hour: int
    end_minute: int

    def time_range_string(self) -> str:
        """Format the scheduled time as a string (e.g., '6:00-6:30')."""
        return (
            f"{self.start_hour}:{self.start_minute:02d}-"
            f"{self.end_hour}:{self.end_minute:02d}"
        )

    def window_display(self) -> str:
        """Format information about which window this task is in."""
        return f"Window {self.window_index + 1}"


@dataclass
class ScheduleResult:
    """Contains the complete result of schedule generation.

    Attributes:
        scheduled_tasks: List of tasks that were successfully scheduled
        skipped_tasks: List of tasks that couldn't fit in the schedule
        total_scheduled_minutes: Total time used by scheduled tasks
        total_available_minutes: Total time available across all windows
        explanation: Human-readable explanation of the schedule
    """
    scheduled_tasks: list[ScheduledTask]
    skipped_tasks: list[Task]
    total_scheduled_minutes: int
    total_available_minutes: int
    explanation: str

    def utilization_percentage(self) -> float:
        """Calculate what percentage of available time was used."""
        if self.total_available_minutes == 0:
            return 0.0
        return (self.total_scheduled_minutes / self.total_available_minutes) * 100

    def summary(self) -> str:
        """Generate a user-friendly summary of the schedule."""
        lines = []

        # Header
        lines.append("=" * 50)
        lines.append("SCHEDULE SUMMARY")
        lines.append("=" * 50)

        # Scheduled tasks count
        lines.append(f"\nScheduled Tasks: {len(self.scheduled_tasks)}")
        if self.scheduled_tasks:
            for st in self.scheduled_tasks:
                lines.append(
                    f"  - [{st.task.priority}] {st.task.title}: "
                    f"{st.time_range_string()} ({st.task.duration_minutes} min)"
                )

        # Skipped tasks count
        lines.append(f"\nSkipped Tasks: {len(self.skipped_tasks)}")
        if self.skipped_tasks:
            for task in self.skipped_tasks:
                lines.append(
                    f"  - [{task.priority}] {task.title}: "
                    f"{task.duration_minutes} min"
                )

        # Time utilization
        lines.append(f"\nTime Utilization:")
        lines.append(
            f"  Used: {self.total_scheduled_minutes} / "
            f"{self.total_available_minutes} minutes "
            f"({self.utilization_percentage():.1f}%)"
        )

        # Explanation
        lines.append(f"\nExplanation:")
        lines.append(f"  {self.explanation}")

        lines.append("=" * 50)

        return "\n".join(lines)
