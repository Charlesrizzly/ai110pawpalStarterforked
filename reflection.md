# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

- Briefly describe your initial UML design.
- What classes did you include, and what responsibilities did you assign to each?

**Answer:**

My initial UML design included 7 core classes organized into three layers:

**Data Models:**
- `TimeWindow`: Represents owner availability windows with start/end hour/minute, validates time ranges, and provides helper methods for duration calculation and overlap detection
- `Task`: Represents pet care tasks with title, duration (minutes), and priority (1-5 scale)
- `Pet`: Basic pet information (name, species)
- `Owner`: Pet owner with name and list of availability windows

**Scheduling Logic:**
- `Scheduler`: Core engine that takes Owner, Pet, and Tasks as input and generates an optimized schedule using a priority-based greedy first-fit algorithm

**Result Classes:**
- `ScheduledTask`: Represents a task placed in the schedule with specific start/end times and window assignment
- `ScheduleResult`: Complete scheduling output containing scheduled tasks, skipped tasks, explanation, and utilization metrics

Each class had clear, single responsibilities following SOLID principles. Data models handled validation and data representation, the Scheduler handled the algorithm logic, and result classes handled output formatting.

**b. Design changes**

- Did your design change during implementation?
- If yes, describe at least one change and why you made it.

**Answer:**

Yes, the design evolved during implementation. One key change was in how we handle time window state tracking. Initially, I considered storing time windows as simple tuples, but during implementation I realized we needed to track:
- The original TimeWindow object
- The current fill position (remaining_start_minutes)
- Remaining available time in that window
- Window index for result reporting

This led to using a dictionary-based state tracking structure in the Scheduler, which made the first-fit algorithm much cleaner and easier to debug. This change was made because the implementation revealed we needed more context than the original design captured.

Another minor change: I initially used the `|` union operator for type hints (e.g., `ScheduledTask | None`), but had to switch to `Optional[ScheduledTask]` for Python 3.9 compatibility after the first test run failed.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

**Answer:**

My scheduler considers three main constraints:

1. **Time availability**: Owner's availability windows (discrete time blocks, not continuous)
2. **Task duration**: How long each task takes in minutes
3. **Task priority**: Importance level from 1 (lowest) to 5 (highest)

I decided priority should be the primary constraint because in pet care, critical tasks like medication (high priority) are more important than optional activities like grooming (lower priority). Time constraints come second - the scheduler tries to fit high-priority tasks first, then fills remaining time with lower-priority tasks.

The decision to use discrete time windows (rather than total available time) came from discussing realistic pet owner schedules - people have fragmented availability (morning before work, evening after work) rather than continuous blocks.

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

**Answer:**

The main tradeoff is **simplicity vs. optimality**. My scheduler uses a greedy first-fit algorithm that schedules tasks in priority order and places each task in the first available window with sufficient space. This is simple and fast (O(n log n)) but not guaranteed to find the optimal packing.

**Example of suboptimality:**
- Window 1: 60 minutes, Window 2: 120 minutes
- Tasks: A (50 min, priority 5), B (40 min, priority 4), C (30 min, priority 3)
- Greedy result: A→B in Window 1 (C skipped)
- Optimal result: A→C in Window 1, B in Window 2 (all three scheduled)

**Why this tradeoff is reasonable:**
1. Pet care scheduling isn't mission-critical - slightly suboptimal is acceptable
2. The greedy approach is predictable and explainable to users
3. O(n log n) performance scales well for typical use (10-20 tasks)
4. Users can adjust priorities if results aren't satisfactory
5. Perfect packing (NP-complete knapsack problem) would be overkill for this domain

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

**Answer:**

I used Claude Code (AI) throughout the entire project lifecycle:

1. **Requirements Analysis**: Discussed complexity levels and clarified whether to include time windows, task dependencies, multiple pets, etc.
2. **System Design**: AI generated a Mermaid.js UML diagram showing all classes, attributes, methods, and relationships
3. **Implementation**: AI wrote class stubs, validation logic, scheduling algorithm, and helper methods
4. **Test-Driven Development**: AI wrote comprehensive test suites (65 tests total) covering normal cases, edge cases, and integration scenarios
5. **UI Integration**: AI built a complete Streamlit interface with two-column layout, input validation, and result visualization

**Most helpful prompts:**
- "Let's talk about requirements and edge cases" - opened discussion before coding
- "Implement validation logic in __post_init__ methods" - specific, actionable
- "Write comprehensive tests following TDD approach" - clear methodology
- "Proceed with Phase 3" - referenced our shared plan for continuity

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

**Answer:**

One key moment was when choosing the scheduling complexity level. AI presented three options (MVP, Intermediate, Advanced) with clear tradeoffs. I chose **Intermediate** (time windows for owner availability) but **not** task-level time constraints, even though AI initially suggested both. I recognized that task-level constraints would add significant complexity for minimal benefit in a Module 2 project.

**Verification approach:**
1. **Ran all tests**: 65 tests, 100% pass rate confirmed correctness
2. **Reviewed generated code**: Checked for security issues (SQL injection, XSS, etc.)
3. **Traced algorithm logic**: Manually walked through the greedy first-fit algorithm with sample data
4. **Tested edge cases**: Zero time, no tasks, overlapping windows all handled correctly
5. **Validated UML accuracy**: Confirmed the final code matched the planned design

I didn't blindly accept AI output - I actively reviewed, questioned, and tested everything.

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

**Answer:**

I tested 65 behaviors across multiple test suites:

**Model Validation (44 tests):**
- TimeWindow: Valid ranges, invalid hours/minutes, end before start, duration calculations, overlap detection
- Task: Valid tasks, negative/zero duration, invalid priorities
- Pet: Empty/whitespace names and species
- Owner: Empty names, overlapping windows, total time calculations

**Scheduler Logic (21 tests):**
- Basic scheduling: single task, multiple tasks, tasks across windows
- Priority ordering: highest priority scheduled first
- Edge cases: no tasks, no availability, tasks too long for any window
- Insufficient time: lower priority tasks skipped
- Exact fit: 100% utilization
- Stable sort: same priority tasks maintain input order

**Why these tests were important:**
1. Validation tests prevent invalid data from corrupting the system
2. Priority tests confirm the core scheduling strategy works correctly
3. Edge case tests ensure robustness in unusual scenarios
4. Integration tests verify end-to-end functionality

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

**Answer:**

I'm **very confident** (90%+) the scheduler works correctly because:
- 100% test pass rate with comprehensive coverage
- Tests cover happy paths, edge cases, and error conditions
- Algorithm is simple enough to reason about (greedy first-fit)
- Type hints catch many errors at design time

**Edge cases I would test next:**

1. **Time boundary cases**: Tasks spanning midnight, windows crossing midnight
2. **Large scale**: 100+ tasks, 50+ windows to test performance
3. **Realistic scenarios**: Weekly schedules, recurring tasks, task dependencies
4. **Concurrency**: Multiple pets with parallel tasks
5. **Error recovery**: Corrupted session state, invalid data

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

**Answer:**

I'm most satisfied with the **systematic, test-driven approach** and **clean architecture**.

The project followed a clear progression: requirements → UML design → class stubs → validation logic → tests → scheduling algorithm → more tests → UI integration. This methodology prevented "code and fix" chaos and ensured quality at each step.

The final architecture is clean and extensible:
- Models are immutable dataclasses with validation
- Scheduler is decoupled from UI (could swap Streamlit for CLI/web API)
- All classes have single responsibilities
- 100% test coverage gives confidence for future changes

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

**Answer:**

If I had another iteration, I would:

1. **Add more sophisticated scheduling**: Try multiple packing strategies, implement branch-and-bound for optimal scheduling, support task preferences and dependencies
2. **Extend to multiple pets**: Schedule tasks for multiple pets, detect conflicts, support simultaneous tasks
3. **Add persistence**: Save/load schedules to JSON or database, export to calendar formats, track completion history
4. **Improve UI/UX**: Drag-and-drop task reordering, visual timeline view, suggested optimizations, mobile-responsive design
5. **Add more tests**: Property-based testing with Hypothesis, load testing, UI testing

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?

**Answer:**

The most important thing I learned is that **good system design requires balancing competing concerns**, and **AI is a powerful design partner when used thoughtfully**.

**On system design:**
Good architecture emerges from:
- **Understanding constraints first** - We discussed requirements and edge cases before writing code
- **Making explicit tradeoffs** - Choosing greedy over optimal was conscious, not accidental
- **Incremental validation** - Each component was tested independently before integration
- **Anticipating change** - The design supports future extensions without major refactoring

**On working with AI:**
AI is most valuable when:
- **You maintain design authority** - AI suggests, you decide based on your goals
- **You provide clear context** - Referencing our shared plan kept responses consistent
- **You verify everything** - Tests caught issues immediately
- **You iterate thoughtfully** - Discussing requirements first led to better solutions than jumping to code

This experience showed me that professional software development isn't about writing code faster - it's about making good design decisions, thinking through edge cases, and building systems that are correct, maintainable, and extensible. AI tools accelerate this process but don't replace the need for careful thinking.
