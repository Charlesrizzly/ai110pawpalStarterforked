"""Tests for core data models in PawPal+ scheduling system."""

import pytest
from src.models import TimeWindow, Task, Pet, Owner


class TestTimeWindow:
    """Test suite for TimeWindow class."""

    def test_valid_time_window(self):
        """Test that a valid time window can be created."""
        window = TimeWindow(start_hour=6, start_minute=0, end_hour=8, end_minute=0)
        assert window.start_hour == 6
        assert window.start_minute == 0
        assert window.end_hour == 8
        assert window.end_minute == 0

    def test_time_window_invalid_start_hour_negative(self):
        """Test that negative start_hour raises ValueError."""
        with pytest.raises(ValueError, match="start_hour must be 0-23"):
            TimeWindow(start_hour=-1, start_minute=0, end_hour=8, end_minute=0)

    def test_time_window_invalid_start_hour_too_high(self):
        """Test that start_hour > 23 raises ValueError."""
        with pytest.raises(ValueError, match="start_hour must be 0-23"):
            TimeWindow(start_hour=24, start_minute=0, end_hour=8, end_minute=0)

    def test_time_window_invalid_end_hour_negative(self):
        """Test that negative end_hour raises ValueError."""
        with pytest.raises(ValueError, match="end_hour must be 0-23"):
            TimeWindow(start_hour=6, start_minute=0, end_hour=-1, end_minute=0)

    def test_time_window_invalid_end_hour_too_high(self):
        """Test that end_hour > 23 raises ValueError."""
        with pytest.raises(ValueError, match="end_hour must be 0-23"):
            TimeWindow(start_hour=6, start_minute=0, end_hour=24, end_minute=0)

    def test_time_window_invalid_start_minute_negative(self):
        """Test that negative start_minute raises ValueError."""
        with pytest.raises(ValueError, match="start_minute must be 0-59"):
            TimeWindow(start_hour=6, start_minute=-1, end_hour=8, end_minute=0)

    def test_time_window_invalid_start_minute_too_high(self):
        """Test that start_minute > 59 raises ValueError."""
        with pytest.raises(ValueError, match="start_minute must be 0-59"):
            TimeWindow(start_hour=6, start_minute=60, end_hour=8, end_minute=0)

    def test_time_window_invalid_end_minute_negative(self):
        """Test that negative end_minute raises ValueError."""
        with pytest.raises(ValueError, match="end_minute must be 0-59"):
            TimeWindow(start_hour=6, start_minute=0, end_hour=8, end_minute=-1)

    def test_time_window_invalid_end_minute_too_high(self):
        """Test that end_minute > 59 raises ValueError."""
        with pytest.raises(ValueError, match="end_minute must be 0-59"):
            TimeWindow(start_hour=6, start_minute=0, end_hour=8, end_minute=60)

    def test_time_window_end_before_start(self):
        """Test that end time before start time raises ValueError."""
        with pytest.raises(ValueError, match="end time .* must be after start time"):
            TimeWindow(start_hour=8, start_minute=0, end_hour=6, end_minute=0)

    def test_time_window_end_equal_start(self):
        """Test that end time equal to start time raises ValueError."""
        with pytest.raises(ValueError, match="end time .* must be after start time"):
            TimeWindow(start_hour=8, start_minute=0, end_hour=8, end_minute=0)

    def test_duration_minutes(self):
        """Test that duration_minutes calculates correctly."""
        window = TimeWindow(start_hour=6, start_minute=0, end_hour=8, end_minute=30)
        assert window.duration_minutes() == 150  # 2.5 hours = 150 minutes

    def test_duration_minutes_same_hour(self):
        """Test duration calculation within same hour."""
        window = TimeWindow(start_hour=9, start_minute=15, end_hour=9, end_minute=45)
        assert window.duration_minutes() == 30

    def test_start_minutes_from_midnight(self):
        """Test conversion of start time to minutes from midnight."""
        window = TimeWindow(start_hour=6, start_minute=30, end_hour=8, end_minute=0)
        assert window.start_minutes_from_midnight() == 390  # 6*60 + 30

    def test_end_minutes_from_midnight(self):
        """Test conversion of end time to minutes from midnight."""
        window = TimeWindow(start_hour=6, start_minute=0, end_hour=8, end_minute=15)
        assert window.end_minutes_from_midnight() == 495  # 8*60 + 15

    def test_to_display_string(self):
        """Test formatting as display string."""
        window = TimeWindow(start_hour=6, start_minute=0, end_hour=8, end_minute=30)
        assert window.to_display_string() == "6:00-8:30"

    def test_to_display_string_single_digit_minutes(self):
        """Test display string formats minutes with leading zero."""
        window = TimeWindow(start_hour=9, start_minute=5, end_hour=10, end_minute=8)
        assert window.to_display_string() == "9:05-10:08"

    def test_overlaps_with_no_overlap(self):
        """Test that non-overlapping windows return False."""
        window1 = TimeWindow(start_hour=6, start_minute=0, end_hour=8, end_minute=0)
        window2 = TimeWindow(start_hour=17, start_minute=0, end_hour=21, end_minute=0)
        assert not window1.overlaps_with(window2)
        assert not window2.overlaps_with(window1)

    def test_overlaps_with_touching_boundaries(self):
        """Test that windows touching at boundaries don't overlap."""
        window1 = TimeWindow(start_hour=6, start_minute=0, end_hour=8, end_minute=0)
        window2 = TimeWindow(start_hour=8, start_minute=0, end_hour=10, end_minute=0)
        assert not window1.overlaps_with(window2)
        assert not window2.overlaps_with(window1)

    def test_overlaps_with_partial_overlap(self):
        """Test that partially overlapping windows return True."""
        window1 = TimeWindow(start_hour=6, start_minute=0, end_hour=9, end_minute=0)
        window2 = TimeWindow(start_hour=8, start_minute=0, end_hour=11, end_minute=0)
        assert window1.overlaps_with(window2)
        assert window2.overlaps_with(window1)

    def test_overlaps_with_complete_overlap(self):
        """Test that one window completely inside another returns True."""
        window1 = TimeWindow(start_hour=6, start_minute=0, end_hour=12, end_minute=0)
        window2 = TimeWindow(start_hour=8, start_minute=0, end_hour=10, end_minute=0)
        assert window1.overlaps_with(window2)
        assert window2.overlaps_with(window1)


class TestTask:
    """Test suite for Task class."""

    def test_valid_task(self):
        """Test that a valid task can be created."""
        task = Task(title="Morning walk", duration_minutes=30, priority=5)
        assert task.title == "Morning walk"
        assert task.duration_minutes == 30
        assert task.priority == 5

    def test_task_negative_duration(self):
        """Test that negative duration raises ValueError."""
        with pytest.raises(ValueError, match="duration_minutes must be positive"):
            Task(title="Walk", duration_minutes=-10, priority=3)

    def test_task_zero_duration(self):
        """Test that zero duration raises ValueError."""
        with pytest.raises(ValueError, match="duration_minutes must be positive"):
            Task(title="Walk", duration_minutes=0, priority=3)

    def test_task_priority_too_low(self):
        """Test that priority < 1 raises ValueError."""
        with pytest.raises(ValueError, match="priority must be 1-5"):
            Task(title="Walk", duration_minutes=30, priority=0)

    def test_task_priority_too_high(self):
        """Test that priority > 5 raises ValueError."""
        with pytest.raises(ValueError, match="priority must be 1-5"):
            Task(title="Walk", duration_minutes=30, priority=6)

    def test_task_priority_negative(self):
        """Test that negative priority raises ValueError."""
        with pytest.raises(ValueError, match="priority must be 1-5"):
            Task(title="Walk", duration_minutes=30, priority=-1)

    def test_task_comparison_lower_priority(self):
        """Test that lower priority task compares as less than higher priority."""
        task1 = Task(title="Low priority", duration_minutes=30, priority=2)
        task2 = Task(title="High priority", duration_minutes=30, priority=5)
        assert task1 < task2

    def test_task_comparison_same_priority(self):
        """Test that tasks with same priority compare as equal."""
        task1 = Task(title="Task 1", duration_minutes=30, priority=3)
        task2 = Task(title="Task 2", duration_minutes=30, priority=3)
        assert not (task1 < task2)
        assert not (task2 < task1)

    def test_task_sorting(self):
        """Test that tasks sort by priority in descending order."""
        tasks = [
            Task(title="Low", duration_minutes=10, priority=1),
            Task(title="High", duration_minutes=10, priority=5),
            Task(title="Med", duration_minutes=10, priority=3),
        ]
        sorted_tasks = sorted(tasks, reverse=True)
        assert sorted_tasks[0].priority == 5
        assert sorted_tasks[1].priority == 3
        assert sorted_tasks[2].priority == 1


class TestPet:
    """Test suite for Pet class."""

    def test_valid_pet(self):
        """Test that a valid pet can be created."""
        pet = Pet(name="Mochi", species="dog")
        assert pet.name == "Mochi"
        assert pet.species == "dog"

    def test_pet_empty_name(self):
        """Test that empty name raises ValueError."""
        with pytest.raises(ValueError, match="Pet name cannot be empty"):
            Pet(name="", species="dog")

    def test_pet_whitespace_only_name(self):
        """Test that whitespace-only name raises ValueError."""
        with pytest.raises(ValueError, match="Pet name cannot be empty"):
            Pet(name="   ", species="dog")

    def test_pet_empty_species(self):
        """Test that empty species raises ValueError."""
        with pytest.raises(ValueError, match="Pet species cannot be empty"):
            Pet(name="Mochi", species="")

    def test_pet_whitespace_only_species(self):
        """Test that whitespace-only species raises ValueError."""
        with pytest.raises(ValueError, match="Pet species cannot be empty"):
            Pet(name="Mochi", species="   ")


class TestOwner:
    """Test suite for Owner class."""

    def test_valid_owner(self):
        """Test that a valid owner can be created."""
        windows = [
            TimeWindow(start_hour=6, start_minute=0, end_hour=8, end_minute=0),
            TimeWindow(start_hour=17, start_minute=0, end_hour=21, end_minute=0),
        ]
        owner = Owner(name="Jordan", availability_windows=windows)
        assert owner.name == "Jordan"
        assert len(owner.availability_windows) == 2

    def test_owner_empty_name(self):
        """Test that empty name raises ValueError."""
        windows = [TimeWindow(start_hour=6, start_minute=0, end_hour=8, end_minute=0)]
        with pytest.raises(ValueError, match="Owner name cannot be empty"):
            Owner(name="", availability_windows=windows)

    def test_owner_whitespace_only_name(self):
        """Test that whitespace-only name raises ValueError."""
        windows = [TimeWindow(start_hour=6, start_minute=0, end_hour=8, end_minute=0)]
        with pytest.raises(ValueError, match="Owner name cannot be empty"):
            Owner(name="   ", availability_windows=windows)

    def test_owner_empty_windows_list(self):
        """Test that owner with no windows can be created (edge case)."""
        owner = Owner(name="Jordan", availability_windows=[])
        assert owner.name == "Jordan"
        assert len(owner.availability_windows) == 0

    def test_owner_overlapping_windows(self):
        """Test that overlapping windows raise ValueError."""
        windows = [
            TimeWindow(start_hour=6, start_minute=0, end_hour=9, end_minute=0),
            TimeWindow(start_hour=8, start_minute=0, end_hour=11, end_minute=0),
        ]
        with pytest.raises(ValueError, match="Availability windows overlap"):
            Owner(name="Jordan", availability_windows=windows)

    def test_owner_non_overlapping_windows(self):
        """Test that non-overlapping windows work correctly."""
        windows = [
            TimeWindow(start_hour=6, start_minute=0, end_hour=8, end_minute=0),
            TimeWindow(start_hour=8, start_minute=0, end_hour=10, end_minute=0),
            TimeWindow(start_hour=17, start_minute=0, end_hour=21, end_minute=0),
        ]
        owner = Owner(name="Jordan", availability_windows=windows)
        assert len(owner.availability_windows) == 3

    def test_total_available_minutes_single_window(self):
        """Test total_available_minutes with one window."""
        windows = [TimeWindow(start_hour=6, start_minute=0, end_hour=8, end_minute=0)]
        owner = Owner(name="Jordan", availability_windows=windows)
        assert owner.total_available_minutes() == 120  # 2 hours

    def test_total_available_minutes_multiple_windows(self):
        """Test total_available_minutes with multiple windows."""
        windows = [
            TimeWindow(start_hour=6, start_minute=0, end_hour=8, end_minute=0),  # 120 min
            TimeWindow(start_hour=17, start_minute=0, end_hour=21, end_minute=0),  # 240 min
        ]
        owner = Owner(name="Jordan", availability_windows=windows)
        assert owner.total_available_minutes() == 360  # 6 hours total

    def test_total_available_minutes_empty_windows(self):
        """Test total_available_minutes with no windows."""
        owner = Owner(name="Jordan", availability_windows=[])
        assert owner.total_available_minutes() == 0
