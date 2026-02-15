"""Core data models for PawPal+ scheduling system."""

from dataclasses import dataclass


@dataclass
class TimeWindow:
    """Represents an owner's availability time window.

    Attributes:
        start_hour: Starting hour (0-23)
        start_minute: Starting minute (0-59)
        end_hour: Ending hour (0-23)
        end_minute: Ending minute (0-59)
    """
    start_hour: int
    start_minute: int
    end_hour: int
    end_minute: int

    def __post_init__(self) -> None:
        """Validate time window constraints."""
        # Validate hour ranges
        if not (0 <= self.start_hour <= 23):
            raise ValueError(f"start_hour must be 0-23, got {self.start_hour}")
        if not (0 <= self.end_hour <= 23):
            raise ValueError(f"end_hour must be 0-23, got {self.end_hour}")

        # Validate minute ranges
        if not (0 <= self.start_minute <= 59):
            raise ValueError(f"start_minute must be 0-59, got {self.start_minute}")
        if not (0 <= self.end_minute <= 59):
            raise ValueError(f"end_minute must be 0-59, got {self.end_minute}")

        # Validate that end time is after start time
        start_mins = self.start_minutes_from_midnight()
        end_mins = self.end_minutes_from_midnight()
        if end_mins <= start_mins:
            raise ValueError(
                f"end time ({self.end_hour}:{self.end_minute:02d}) must be after "
                f"start time ({self.start_hour}:{self.start_minute:02d})"
            )

    def duration_minutes(self) -> int:
        """Calculate total duration of this window in minutes."""
        return self.end_minutes_from_midnight() - self.start_minutes_from_midnight()

    def start_minutes_from_midnight(self) -> int:
        """Convert start time to minutes from midnight."""
        return self.start_hour * 60 + self.start_minute

    def end_minutes_from_midnight(self) -> int:
        """Convert end time to minutes from midnight."""
        return self.end_hour * 60 + self.end_minute

    def to_display_string(self) -> str:
        """Format time window as display string (e.g., '6:00-8:00')."""
        return f"{self.start_hour}:{self.start_minute:02d}-{self.end_hour}:{self.end_minute:02d}"

    def overlaps_with(self, other: 'TimeWindow') -> bool:
        """Check if this window overlaps with another window."""
        # Two windows overlap if one starts before the other ends
        self_start = self.start_minutes_from_midnight()
        self_end = self.end_minutes_from_midnight()
        other_start = other.start_minutes_from_midnight()
        other_end = other.end_minutes_from_midnight()

        # Check if windows overlap (not just touch at boundaries)
        return (self_start < other_end) and (other_start < self_end)


@dataclass
class Task:
    """Represents a pet care task.

    Attributes:
        title: Description of the task
        duration_minutes: How long the task takes in minutes
        priority: Task priority (1-5, where 5 is highest)
    """
    title: str
    duration_minutes: int
    priority: int

    def __post_init__(self) -> None:
        """Validate task attributes."""
        # Validate duration is positive
        if self.duration_minutes <= 0:
            raise ValueError(f"duration_minutes must be positive, got {self.duration_minutes}")

        # Validate priority is in range 1-5
        if not (1 <= self.priority <= 5):
            raise ValueError(f"priority must be 1-5, got {self.priority}")

    def __lt__(self, other: 'Task') -> bool:
        """Compare tasks by priority for sorting (higher priority first).

        Note: Returns True if self has LOWER priority than other,
        which enables sorting in descending priority order.
        """
        return self.priority < other.priority


@dataclass
class Pet:
    """Represents a pet.

    Attributes:
        name: Pet's name
        species: Type of pet (dog, cat, other)
    """
    name: str
    species: str

    def __post_init__(self) -> None:
        """Validate pet attributes."""
        # Validate name is non-empty
        if not self.name or not self.name.strip():
            raise ValueError("Pet name cannot be empty")

        # Validate species is non-empty
        if not self.species or not self.species.strip():
            raise ValueError("Pet species cannot be empty")


@dataclass
class Owner:
    """Represents a pet owner.

    Attributes:
        name: Owner's name
        availability_windows: List of time windows when owner is available
    """
    name: str
    availability_windows: list['TimeWindow']

    def __post_init__(self) -> None:
        """Validate owner attributes and check for overlapping windows."""
        # Validate name is non-empty
        if not self.name or not self.name.strip():
            raise ValueError("Owner name cannot be empty")

        # Validate at least one availability window (or allow empty for edge case testing)
        # Note: We allow empty windows list, scheduler will handle it

        # Check for overlapping windows
        for i, window1 in enumerate(self.availability_windows):
            for window2 in self.availability_windows[i + 1:]:
                if window1.overlaps_with(window2):
                    raise ValueError(
                        f"Availability windows overlap: {window1.to_display_string()} "
                        f"and {window2.to_display_string()}"
                    )

    def total_available_minutes(self) -> int:
        """Calculate total available time across all windows."""
        return sum(window.duration_minutes() for window in self.availability_windows)
