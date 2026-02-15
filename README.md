# PawPal+ (Module 2 Project)

**PawPal+** is a Streamlit-based pet care task scheduler that helps pet owners plan daily care activities based on their availability and task priorities. The system uses a priority-based greedy algorithm to generate optimal schedules while handling various constraints and edge cases.

## 📸 Demo
-[ 

https://github.com/user-attachments/assets/f44f2cd9-1a3d-4177-ba17-4121fe71929b

] [Insert screenshot here!]

## Features

### Core Scheduling Algorithm

**Priority-Based Greedy First-Fit Scheduling (O(n log n))**
- Sorts tasks by priority in descending order (5=highest, 1=lowest)
- Places each task in the earliest available time window with sufficient space
- Automatically skips lower-priority tasks when time is insufficient
- Maintains stable sorting for tasks with equal priority (preserves input order)

### Time Management

**Discrete Time Window Support**
- Owner specifies availability as discrete time blocks (e.g., 6:00-8:00am, 5:00-9:00pm)
- Supports multiple non-overlapping windows throughout the day
- Validates time ranges (0-23 hours, 0-59 minutes)
- Detects and prevents overlapping availability windows
- Calculates total available time across all windows

**Smart Task Placement**
- Tasks scheduled sequentially within each window
- Automatically spans multiple windows when needed
- Tracks remaining time per window for optimal placement
- Handles tasks that don't fit in any single window

### Comprehensive Validation

**Input Validation**
- Task duration: Must be positive (> 0 minutes)
- Task priority: Must be in range 1-5
- Time windows: End time must be after start time
- Owner/Pet names: Cannot be empty or whitespace-only
- Prevents duplicate or overlapping windows

**Edge Case Handling**
- Zero available time: Returns empty schedule with explanation
- No tasks: Returns appropriate message
- Tasks too long for any window: Automatically skips with reason
- Insufficient total time: Prioritizes high-priority tasks
- All same priority: Maintains input order (stable sort)

### Intelligent Explanations

**Algorithm Transparency**
- Explains scheduling strategy used (priority-based ordering)
- Lists each scheduled task with assigned time slot and window
- Details which tasks were skipped and why
- Shows time utilization statistics
- Provides reasoning for scheduling decisions

### Results & Metrics

**Comprehensive Output**
- **Scheduled Tasks**: Time range, duration, priority, assigned window
- **Skipped Tasks**: Which tasks didn't fit and why
- **Utilization Metrics**: Percentage of available time used
- **Time Statistics**: Total scheduled vs. available minutes
- **Visual Display**: Color-coded tables and metrics

### User Interface

**Intuitive Two-Column Layout**
- **Left Column (Input)**:
  - Owner and pet information
  - Time window builder with hour/minute controls
  - Task creator with title, duration, priority inputs
  - Real-time validation and feedback

- **Right Column (Results)**:
  - Summary metrics (scheduled, skipped, utilization)
  - Detailed task tables with times
  - Expandable explanation section
  - Statistics breakdown

**User Experience**
- Real-time input validation with clear error messages
- One-click window and task addition
- Clear/reset functionality for both windows and tasks
- Automatic time calculations and summaries
- Example usage guide included
- Mobile-friendly responsive design

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

## Architecture

### System Design

**Data Models** (`src/models.py`):
- `TimeWindow`: Availability window with validation and helper methods
- `Task`: Pet care task with duration and priority
- `Pet`: Basic pet information
- `Owner`: Pet owner with availability windows

**Scheduling Engine** (`src/scheduler.py`):
- `Scheduler`: Core algorithm implementation
- Priority-based greedy first-fit scheduling
- Window state tracking and management
- Comprehensive explanation generation

**Result Classes** (`src/schedule_result.py`):
- `ScheduledTask`: Task with assigned time slot
- `ScheduleResult`: Complete scheduling output with metrics

### Algorithm Details

**Scheduling Strategy:**
1. Validate all inputs (owner, pet, tasks, time windows)
2. Sort tasks by priority (descending: 5 → 4 → 3 → 2 → 1)
3. Initialize tracking for each availability window
4. For each task (in priority order):
   - Try to fit in first available window with space
   - If successful: assign time slot and update window state
   - If unsuccessful: add to skipped tasks list
5. Generate detailed explanation of decisions
6. Return complete result with metrics

**Time Complexity**: O(n log n) where n = number of tasks
- Sorting: O(n log n)
- Task placement: O(n × w) where w = number of windows (typically small)
- Overall: O(n log n) for practical use cases

**Space Complexity**: O(n + w) for storing tasks and window states

### Testing

**Comprehensive Test Suite** (65 tests, 100% pass rate):
- **Model Validation Tests (44)**: Time ranges, priorities, overlapping windows
- **Scheduler Logic Tests (21)**: Priority ordering, edge cases, integration
- **Coverage**: Happy paths, edge cases, error conditions

## Getting Started

### Setup

```bash
# Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Running the Application

```bash
# Launch Streamlit app
streamlit run app.py

# Run tests
pytest tests/ -v

# Run specific test file
pytest tests/test_scheduler.py -v
```

### Quick Start Example

1. **Add Availability Windows:**
   - Morning: 6:00 - 8:00 (2 hours)
   - Evening: 17:00 - 21:00 (4 hours)

2. **Add Tasks:**
   - Morning walk (30 min, priority 5)
   - Feeding (10 min, priority 5)
   - Medicine (5 min, priority 4)
   - Play time (60 min, priority 3)
   - Grooming (45 min, priority 2)
   - Training (30 min, priority 1)

3. **Generate Schedule** - Click the button to see:
   - Which tasks were scheduled and when
   - Which tasks were skipped and why
   - Time utilization metrics
   - Detailed explanation

### Project Structure

```
PawPal+/
├── src/
│   ├── models.py              # Data models (TimeWindow, Task, Pet, Owner)
│   ├── scheduler.py           # Scheduling algorithm
│   └── schedule_result.py     # Result classes
├── tests/
│   ├── test_models.py         # Model validation tests
│   └── test_scheduler.py      # Scheduler logic tests
├── app.py                     # Streamlit UI
├── requirements.txt           # Dependencies
├── reflection.md              # Project reflection
└── README.md                  # This file
```

## Design Decisions

### Why Greedy Algorithm?

**Tradeoff: Simplicity vs. Optimality**

The scheduler uses a greedy first-fit algorithm rather than optimal bin packing because:
1. **Predictable**: Users can understand why tasks were scheduled in a specific order
2. **Fast**: O(n log n) performance scales well for typical pet care scenarios (10-20 tasks)
3. **Good Enough**: Pet care scheduling isn't mission-critical; slightly suboptimal is acceptable
4. **Explainable**: Easy to generate clear explanations of scheduling decisions
5. **Practical**: Perfect packing (NP-complete) would be overkill for this domain

### Why Discrete Time Windows?

Realistic pet owner availability is fragmented (morning before work, evening after work) rather than continuous. Discrete windows better model real-world constraints.

### Why Priority Scale 1-5?

Provides sufficient granularity for pet care tasks (critical medication vs. optional grooming) while remaining simple and intuitive for users.

## Development Workflow

This project followed a systematic TDD approach:

1. **Requirements Analysis**: Discussed constraints, priorities, and edge cases
2. **UML Design**: Created class diagram with Mermaid.js
3. **Class Stubs**: Implemented skeleton classes with type hints
4. **Model Implementation**: Added validation logic with tests (44 tests)
5. **Algorithm Implementation**: Built scheduler with tests (21 tests)
6. **UI Integration**: Connected backend to Streamlit interface
7. **Reflection**: Documented design decisions and lessons learned
