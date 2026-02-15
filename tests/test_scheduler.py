"""Tests for the PawPal+ scheduling algorithm."""

import pytest
from src.models import TimeWindow, Task, Pet, Owner
from src.scheduler import Scheduler
from src.schedule_result import ScheduleResult


class TestSchedulerBasics:
    """Test basic scheduling functionality."""

    def test_schedule_single_task_single_window(self):
        """Test scheduling a single task in a single window."""
        owner = Owner(
            name="Jordan",
            availability_windows=[
                TimeWindow(start_hour=9, start_minute=0, end_hour=10, end_minute=0)
            ]
        )
        pet = Pet(name="Mochi", species="dog")
        tasks = [Task(title="Walk", duration_minutes=30, priority=5)]

        scheduler = Scheduler(owner, pet, tasks)
        result = scheduler.generate_schedule()

        assert len(result.scheduled_tasks) == 1
        assert len(result.skipped_tasks) == 0
        assert result.scheduled_tasks[0].task.title == "Walk"
        assert result.scheduled_tasks[0].start_hour == 9
        assert result.scheduled_tasks[0].start_minute == 0
        assert result.scheduled_tasks[0].end_hour == 9
        assert result.scheduled_tasks[0].end_minute == 30
        assert result.total_scheduled_minutes == 30
        assert result.total_available_minutes == 60

    def test_schedule_multiple_tasks_single_window(self):
        """Test scheduling multiple tasks in a single window."""
        owner = Owner(
            name="Jordan",
            availability_windows=[
                TimeWindow(start_hour=9, start_minute=0, end_hour=10, end_minute=0)
            ]
        )
        pet = Pet(name="Mochi", species="dog")
        tasks = [
            Task(title="Walk", duration_minutes=20, priority=5),
            Task(title="Feed", duration_minutes=10, priority=5),
            Task(title="Play", duration_minutes=15, priority=3),
        ]

        scheduler = Scheduler(owner, pet, tasks)
        result = scheduler.generate_schedule()

        assert len(result.scheduled_tasks) == 3
        assert len(result.skipped_tasks) == 0
        # Tasks should be scheduled sequentially
        assert result.scheduled_tasks[0].start_minute == 0
        assert result.scheduled_tasks[1].start_minute == 20
        assert result.scheduled_tasks[2].start_minute == 30
        assert result.total_scheduled_minutes == 45

    def test_schedule_tasks_across_multiple_windows(self):
        """Test scheduling tasks that span multiple availability windows."""
        owner = Owner(
            name="Jordan",
            availability_windows=[
                TimeWindow(start_hour=6, start_minute=0, end_hour=7, end_minute=0),   # 60 min
                TimeWindow(start_hour=17, start_minute=0, end_hour=19, end_minute=0),  # 120 min
            ]
        )
        pet = Pet(name="Mochi", species="dog")
        tasks = [
            Task(title="Morning walk", duration_minutes=40, priority=5),
            Task(title="Evening walk", duration_minutes=40, priority=5),
            Task(title="Play", duration_minutes=30, priority=3),
        ]

        scheduler = Scheduler(owner, pet, tasks)
        result = scheduler.generate_schedule()

        assert len(result.scheduled_tasks) == 3
        assert len(result.skipped_tasks) == 0
        # First task in first window
        assert result.scheduled_tasks[0].window_index == 0
        assert result.scheduled_tasks[0].start_hour == 6
        # Second and third tasks in second window
        assert result.scheduled_tasks[1].window_index == 1
        assert result.scheduled_tasks[1].start_hour == 17
        assert result.scheduled_tasks[2].window_index == 1

    def test_schedule_by_priority(self):
        """Test that higher priority tasks are scheduled before lower priority tasks."""
        owner = Owner(
            name="Jordan",
            availability_windows=[
                TimeWindow(start_hour=9, start_minute=0, end_hour=10, end_minute=0)
            ]
        )
        pet = Pet(name="Mochi", species="dog")
        tasks = [
            Task(title="Low priority", duration_minutes=20, priority=1),
            Task(title="High priority", duration_minutes=20, priority=5),
            Task(title="Medium priority", duration_minutes=20, priority=3),
        ]

        scheduler = Scheduler(owner, pet, tasks)
        result = scheduler.generate_schedule()

        # All three tasks should fit (60 minutes available)
        assert len(result.scheduled_tasks) == 3
        # Check priority order
        assert result.scheduled_tasks[0].task.title == "High priority"
        assert result.scheduled_tasks[1].task.title == "Medium priority"
        assert result.scheduled_tasks[2].task.title == "Low priority"


class TestSchedulerEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_schedule_no_tasks(self):
        """Test scheduling when no tasks are provided."""
        owner = Owner(
            name="Jordan",
            availability_windows=[
                TimeWindow(start_hour=9, start_minute=0, end_hour=10, end_minute=0)
            ]
        )
        pet = Pet(name="Mochi", species="dog")
        tasks = []

        scheduler = Scheduler(owner, pet, tasks)
        result = scheduler.generate_schedule()

        assert len(result.scheduled_tasks) == 0
        assert len(result.skipped_tasks) == 0
        assert result.total_scheduled_minutes == 0
        assert "No tasks to schedule" in result.explanation

    def test_schedule_no_availability_windows(self):
        """Test scheduling when owner has no availability windows."""
        owner = Owner(name="Jordan", availability_windows=[])
        pet = Pet(name="Mochi", species="dog")
        tasks = [Task(title="Walk", duration_minutes=30, priority=5)]

        scheduler = Scheduler(owner, pet, tasks)
        result = scheduler.generate_schedule()

        assert len(result.scheduled_tasks) == 0
        assert len(result.skipped_tasks) == 1
        assert result.total_available_minutes == 0
        assert "No availability windows" in result.explanation

    def test_schedule_task_too_long_for_any_window(self):
        """Test scheduling when a task is longer than any single window."""
        owner = Owner(
            name="Jordan",
            availability_windows=[
                TimeWindow(start_hour=9, start_minute=0, end_hour=9, end_minute=30),   # 30 min
                TimeWindow(start_hour=17, start_minute=0, end_hour=17, end_minute=45),  # 45 min
            ]
        )
        pet = Pet(name="Mochi", species="dog")
        tasks = [
            Task(title="Short task", duration_minutes=20, priority=5),
            Task(title="Too long", duration_minutes=60, priority=4),  # Longer than any window
        ]

        scheduler = Scheduler(owner, pet, tasks)
        result = scheduler.generate_schedule()

        assert len(result.scheduled_tasks) == 1
        assert len(result.skipped_tasks) == 1
        assert result.scheduled_tasks[0].task.title == "Short task"
        assert result.skipped_tasks[0].title == "Too long"

    def test_schedule_insufficient_time(self):
        """Test scheduling when there's not enough time for all tasks."""
        owner = Owner(
            name="Jordan",
            availability_windows=[
                TimeWindow(start_hour=9, start_minute=0, end_hour=10, end_minute=0)  # 60 min
            ]
        )
        pet = Pet(name="Mochi", species="dog")
        tasks = [
            Task(title="High priority 1", duration_minutes=30, priority=5),
            Task(title="High priority 2", duration_minutes=30, priority=5),
            Task(title="Low priority", duration_minutes=30, priority=1),  # Won't fit
        ]

        scheduler = Scheduler(owner, pet, tasks)
        result = scheduler.generate_schedule()

        assert len(result.scheduled_tasks) == 2
        assert len(result.skipped_tasks) == 1
        assert result.skipped_tasks[0].title == "Low priority"
        assert result.total_scheduled_minutes == 60

    def test_schedule_exact_fit(self):
        """Test scheduling when tasks exactly fill available time."""
        owner = Owner(
            name="Jordan",
            availability_windows=[
                TimeWindow(start_hour=9, start_minute=0, end_hour=10, end_minute=0)  # 60 min
            ]
        )
        pet = Pet(name="Mochi", species="dog")
        tasks = [
            Task(title="Task 1", duration_minutes=20, priority=5),
            Task(title="Task 2", duration_minutes=20, priority=4),
            Task(title="Task 3", duration_minutes=20, priority=3),
        ]

        scheduler = Scheduler(owner, pet, tasks)
        result = scheduler.generate_schedule()

        assert len(result.scheduled_tasks) == 3
        assert len(result.skipped_tasks) == 0
        assert result.total_scheduled_minutes == 60
        assert result.total_available_minutes == 60
        assert result.utilization_percentage() == 100.0

    def test_schedule_same_priority_maintains_order(self):
        """Test that tasks with same priority maintain their input order (stable sort)."""
        owner = Owner(
            name="Jordan",
            availability_windows=[
                TimeWindow(start_hour=9, start_minute=0, end_hour=11, end_minute=0)  # 120 min
            ]
        )
        pet = Pet(name="Mochi", species="dog")
        tasks = [
            Task(title="First", duration_minutes=20, priority=3),
            Task(title="Second", duration_minutes=20, priority=3),
            Task(title="Third", duration_minutes=20, priority=3),
        ]

        scheduler = Scheduler(owner, pet, tasks)
        result = scheduler.generate_schedule()

        assert len(result.scheduled_tasks) == 3
        # Should maintain input order for same priority
        assert result.scheduled_tasks[0].task.title == "First"
        assert result.scheduled_tasks[1].task.title == "Second"
        assert result.scheduled_tasks[2].task.title == "Third"


class TestSchedulerValidation:
    """Test input validation."""

    def test_scheduler_validates_none_owner(self):
        """Test that scheduler validates None owner."""
        pet = Pet(name="Mochi", species="dog")
        tasks = [Task(title="Walk", duration_minutes=30, priority=5)]

        scheduler = Scheduler(owner=None, pet=pet, tasks=tasks)
        with pytest.raises(ValueError, match="Owner cannot be None"):
            scheduler.generate_schedule()

    def test_scheduler_validates_none_pet(self):
        """Test that scheduler validates None pet."""
        owner = Owner(
            name="Jordan",
            availability_windows=[
                TimeWindow(start_hour=9, start_minute=0, end_hour=10, end_minute=0)
            ]
        )
        tasks = [Task(title="Walk", duration_minutes=30, priority=5)]

        scheduler = Scheduler(owner=owner, pet=None, tasks=tasks)
        with pytest.raises(ValueError, match="Pet cannot be None"):
            scheduler.generate_schedule()

    def test_scheduler_validates_none_tasks(self):
        """Test that scheduler validates None tasks list."""
        owner = Owner(
            name="Jordan",
            availability_windows=[
                TimeWindow(start_hour=9, start_minute=0, end_hour=10, end_minute=0)
            ]
        )
        pet = Pet(name="Mochi", species="dog")

        scheduler = Scheduler(owner=owner, pet=pet, tasks=None)
        with pytest.raises(ValueError, match="Tasks list cannot be None"):
            scheduler.generate_schedule()


class TestScheduleResult:
    """Test ScheduleResult methods and properties."""

    def test_utilization_percentage(self):
        """Test utilization percentage calculation."""
        owner = Owner(
            name="Jordan",
            availability_windows=[
                TimeWindow(start_hour=9, start_minute=0, end_hour=11, end_minute=0)  # 120 min
            ]
        )
        pet = Pet(name="Mochi", species="dog")
        tasks = [
            Task(title="Task 1", duration_minutes=30, priority=5),
            Task(title="Task 2", duration_minutes=30, priority=5),
        ]

        scheduler = Scheduler(owner, pet, tasks)
        result = scheduler.generate_schedule()

        assert result.total_scheduled_minutes == 60
        assert result.total_available_minutes == 120
        assert result.utilization_percentage() == 50.0

    def test_utilization_percentage_zero_available(self):
        """Test utilization percentage when no time available."""
        owner = Owner(name="Jordan", availability_windows=[])
        pet = Pet(name="Mochi", species="dog")
        tasks = [Task(title="Walk", duration_minutes=30, priority=5)]

        scheduler = Scheduler(owner, pet, tasks)
        result = scheduler.generate_schedule()

        assert result.utilization_percentage() == 0.0

    def test_explanation_contains_pet_info(self):
        """Test that explanation contains pet information."""
        owner = Owner(
            name="Jordan",
            availability_windows=[
                TimeWindow(start_hour=9, start_minute=0, end_hour=10, end_minute=0)
            ]
        )
        pet = Pet(name="Mochi", species="dog")
        tasks = [Task(title="Walk", duration_minutes=30, priority=5)]

        scheduler = Scheduler(owner, pet, tasks)
        result = scheduler.generate_schedule()

        assert "Mochi" in result.explanation
        assert "dog" in result.explanation

    def test_explanation_lists_scheduled_tasks(self):
        """Test that explanation lists all scheduled tasks."""
        owner = Owner(
            name="Jordan",
            availability_windows=[
                TimeWindow(start_hour=9, start_minute=0, end_hour=10, end_minute=0)
            ]
        )
        pet = Pet(name="Mochi", species="dog")
        tasks = [
            Task(title="Walk", duration_minutes=20, priority=5),
            Task(title="Feed", duration_minutes=10, priority=5),
        ]

        scheduler = Scheduler(owner, pet, tasks)
        result = scheduler.generate_schedule()

        assert "Walk" in result.explanation
        assert "Feed" in result.explanation

    def test_explanation_lists_skipped_tasks(self):
        """Test that explanation lists skipped tasks."""
        owner = Owner(
            name="Jordan",
            availability_windows=[
                TimeWindow(start_hour=9, start_minute=0, end_hour=9, end_minute=30)  # 30 min
            ]
        )
        pet = Pet(name="Mochi", species="dog")
        tasks = [
            Task(title="Short task", duration_minutes=20, priority=5),
            Task(title="Skipped task", duration_minutes=30, priority=1),
        ]

        scheduler = Scheduler(owner, pet, tasks)
        result = scheduler.generate_schedule()

        assert "Skipped task" in result.explanation


class TestScheduledTaskMethods:
    """Test ScheduledTask helper methods."""

    def test_time_range_string(self):
        """Test that time_range_string formats correctly."""
        owner = Owner(
            name="Jordan",
            availability_windows=[
                TimeWindow(start_hour=9, start_minute=5, end_hour=10, end_minute=0)
            ]
        )
        pet = Pet(name="Mochi", species="dog")
        tasks = [Task(title="Walk", duration_minutes=30, priority=5)]

        scheduler = Scheduler(owner, pet, tasks)
        result = scheduler.generate_schedule()

        time_str = result.scheduled_tasks[0].time_range_string()
        assert time_str == "9:05-9:35"

    def test_window_display(self):
        """Test that window_display formats correctly."""
        owner = Owner(
            name="Jordan",
            availability_windows=[
                TimeWindow(start_hour=6, start_minute=0, end_hour=6, end_minute=30),  # 30 min - only fits one task
                TimeWindow(start_hour=17, start_minute=0, end_hour=19, end_minute=0),  # 120 min
            ]
        )
        pet = Pet(name="Mochi", species="dog")
        tasks = [
            Task(title="Morning task", duration_minutes=30, priority=5),
            Task(title="Evening task", duration_minutes=30, priority=5),
        ]

        scheduler = Scheduler(owner, pet, tasks)
        result = scheduler.generate_schedule()

        assert result.scheduled_tasks[0].window_display() == "Window 1"
        assert result.scheduled_tasks[1].window_display() == "Window 2"


class TestIntegrationScenarios:
    """Test realistic end-to-end scenarios."""

    def test_realistic_daily_schedule(self):
        """Test a realistic daily pet care schedule."""
        owner = Owner(
            name="Jordan",
            availability_windows=[
                TimeWindow(start_hour=6, start_minute=0, end_hour=8, end_minute=0),   # 120 min morning
                TimeWindow(start_hour=17, start_minute=0, end_hour=21, end_minute=0),  # 240 min evening
            ]
        )
        pet = Pet(name="Mochi", species="dog")
        tasks = [
            Task(title="Morning walk", duration_minutes=30, priority=5),
            Task(title="Feeding", duration_minutes=10, priority=5),
            Task(title="Medicine", duration_minutes=5, priority=4),
            Task(title="Play time", duration_minutes=60, priority=3),
            Task(title="Grooming", duration_minutes=45, priority=2),
            Task(title="Training", duration_minutes=30, priority=1),
        ]

        scheduler = Scheduler(owner, pet, tasks)
        result = scheduler.generate_schedule()

        # Should schedule highest priority tasks first
        assert len(result.scheduled_tasks) >= 4  # At least the high priority ones
        assert result.scheduled_tasks[0].task.priority >= 4
        assert result.scheduled_tasks[1].task.priority >= 4

        # Verify times are within windows
        for st in result.scheduled_tasks:
            window = owner.availability_windows[st.window_index]
            assert st.start_hour >= window.start_hour
            assert st.end_hour <= window.end_hour

        # Verify utilization
        assert 0 <= result.utilization_percentage() <= 100
