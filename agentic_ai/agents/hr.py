"""
HRAgent - Human Resources Management
=====================================

Provides employee management, onboarding, performance reviews,
time-off tracking, and HR analytics.
"""

import logging
import secrets
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional


logger = logging.getLogger(__name__)


class EmploymentType(Enum):
    """Employment types."""
    FULL_TIME = "full_time"
    PART_TIME = "part_time"
    CONTRACTOR = "contractor"
    INTERN = "intern"


class ReviewStatus(Enum):
    """Performance review status."""
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    ACKNOWLEDGED = "acknowledged"


class TimeOffType(Enum):
    """Time off types."""
    VACATION = "vacation"
    SICK = "sick"
    PERSONAL = "personal"
    PARENTAL = "parental"
    BEREAVEMENT = "bereavement"
    UNPAID = "unpaid"


class TimeOffStatus(Enum):
    """Time off request status."""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    CANCELLED = "cancelled"


@dataclass
class Employee:
    """Employee record."""
    employee_id: str
    name: str
    email: str
    department: str
    position: str
    manager_id: Optional[str]
    employment_type: EmploymentType
    hire_date: datetime
    salary: float = 0.0
    location: str = ""
    status: str = "active"  # active, on_leave, terminated
    skills: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class Onboarding:
    """Onboarding checklist."""
    onboarding_id: str
    employee_id: str
    tasks: List[Dict[str, Any]]
    start_date: datetime
    expected_end: datetime
    progress: float = 0.0
    status: str = "in_progress"  # in_progress, completed
    completed_at: Optional[datetime] = None


@dataclass
class PerformanceReview:
    """Performance review."""
    review_id: str
    employee_id: str
    reviewer_id: str
    period_start: datetime
    period_end: datetime
    status: ReviewStatus
    goals: List[str] = field(default_factory=list)
    achievements: List[str] = field(default_factory=list)
    areas_for_improvement: List[str] = field(default_factory=list)
    rating: Optional[int] = None  # 1-5
    feedback: str = ""
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class TimeOffRequest:
    """Time off request."""
    request_id: str
    employee_id: str
    time_off_type: TimeOffType
    start_date: datetime
    end_date: datetime
    status: TimeOffStatus
    reason: str = ""
    approved_by: Optional[str] = None
    approved_at: Optional[datetime] = None
    created_at: datetime = field(default_factory=datetime.utcnow)


class HRAgent:
    """
    HR Agent for employee management, onboarding,
    performance reviews, and time-off tracking.
    """

    def __init__(self, agent_id: str = "hr-agent"):
        self.agent_id = agent_id
        self.employees: Dict[str, Employee] = {}
        self.onboardings: Dict[str, Onboarding] = {}
        self.reviews: Dict[str, PerformanceReview] = {}
        self.time_off_requests: Dict[str, TimeOffRequest] = {}
        self.departments: Dict[str, Dict[str, Any]] = {}

        # Initialize default departments
        self._init_departments()

    def _init_departments(self):
        """Initialize default departments."""
        self.departments = {
            'engineering': {'name': 'Engineering', 'head_count': 0, 'budget': 0},
            'sales': {'name': 'Sales', 'head_count': 0, 'budget': 0},
            'marketing': {'name': 'Marketing', 'head_count': 0, 'budget': 0},
            'hr': {'name': 'Human Resources', 'head_count': 0, 'budget': 0},
            'finance': {'name': 'Finance', 'head_count': 0, 'budget': 0},
        }

    # ============================================
    # Employee Management
    # ============================================

    def hire_employee(
        self,
        name: str,
        email: str,
        department: str,
        position: str,
        employment_type: EmploymentType,
        manager_id: Optional[str] = None,
        salary: float = 0.0,
        location: str = "",
        skills: Optional[List[str]] = None,
    ) -> Employee:
        """Hire a new employee."""
        employee = Employee(
            employee_id=self._generate_id("emp"),
            name=name,
            email=email,
            department=department,
            position=position,
            manager_id=manager_id,
            employment_type=employment_type,
            hire_date=datetime.utcnow(),
            salary=salary,
            location=location,
            skills=skills or [],
        )

        self.employees[employee.employee_id] = employee

        # Update department head count
        if department in self.departments:
            self.departments[department]['head_count'] += 1

        logger.info(f"Hired employee: {employee.name} ({employee.employee_id})")
        return employee

    def terminate_employee(
        self,
        employee_id: str,
        reason: str,
        terminated_by: str,
    ) -> Optional[Employee]:
        """Terminate an employee."""
        if employee_id not in self.employees:
            return None

        employee = self.employees[employee_id]
        employee.status = "terminated"

        # Update department head count
        if employee.department in self.departments:
            self.departments[employee.department]['head_count'] -= 1

        logger.info(f"Terminated employee: {employee.name}")
        return employee

    def get_employee(self, employee_id: str) -> Optional[Employee]:
        """Get employee by ID."""
        return self.employees.get(employee_id)

    def get_employees(
        self,
        department: Optional[str] = None,
        status: Optional[str] = None,
        employment_type: Optional[EmploymentType] = None,
    ) -> List[Employee]:
        """Get employees with filtering."""
        employees = list(self.employees.values())

        if department:
            employees = [e for e in employees if e.department == department]

        if status:
            employees = [e for e in employees if e.status == status]

        if employment_type:
            employees = [e for e in employees if e.employment_type == employment_type]

        return employees

    def update_employee(
        self,
        employee_id: str,
        updates: Dict[str, Any],
    ) -> bool:
        """Update employee information."""
        if employee_id not in self.employees:
            return False

        employee = self.employees[employee_id]

        for key, value in updates.items():
            if hasattr(employee, key):
                setattr(employee, key, value)

        return True

    # ============================================
    # Onboarding
    # ============================================

    def create_onboarding(
        self,
        employee_id: str,
        start_date: datetime,
        duration_days: int = 30,
    ) -> Onboarding:
        """Create onboarding checklist for new employee."""
        # Default onboarding tasks
        tasks = [
            {'name': 'Complete HR paperwork', 'completed': False, 'category': 'admin'},
            {'name': 'Set up workstation', 'completed': False, 'category': 'equipment'},
            {'name': 'IT orientation', 'completed': False, 'category': 'training'},
            {'name': 'Meet team members', 'completed': False, 'category': 'social'},
            {'name': 'Review company policies', 'completed': False, 'category': 'training'},
            {'name': 'Complete security training', 'completed': False, 'category': 'training'},
            {'name': '30-day check-in', 'completed': False, 'category': 'review'},
        ]

        onboarding = Onboarding(
            onboarding_id=self._generate_id("onboard"),
            employee_id=employee_id,
            tasks=tasks,
            start_date=start_date,
            expected_end=start_date + timedelta(days=duration_days),
        )

        self.onboardings[onboarding.onboarding_id] = onboarding
        logger.info(f"Created onboarding for employee {employee_id}")
        return onboarding

    def complete_onboarding_task(
        self,
        onboarding_id: str,
        task_name: str,
    ) -> bool:
        """Mark onboarding task as complete."""
        if onboarding_id not in self.onboardings:
            return False

        onboarding = self.onboardings[onboarding_id]

        for task in onboarding.tasks:
            if task['name'] == task_name:
                task['completed'] = True
                break

        # Calculate progress
        completed = sum(1 for t in onboarding.tasks if t['completed'])
        onboarding.progress = (completed / len(onboarding.tasks)) * 100

        # Check if all tasks complete
        if onboarding.progress == 100:
            onboarding.status = "completed"
            onboarding.completed_at = datetime.utcnow()

        return True

    def get_onboarding_progress(self, employee_id: str) -> Optional[Dict[str, Any]]:
        """Get onboarding progress for employee."""
        for onboarding in self.onboardings.values():
            if onboarding.employee_id == employee_id:
                return {
                    'onboarding_id': onboarding.onboarding_id,
                    'progress': onboarding.progress,
                    'status': onboarding.status,
                    'tasks_completed': sum(1 for t in onboarding.tasks if t['completed']),
                    'total_tasks': len(onboarding.tasks),
                }
        return None

    # ============================================
    # Performance Reviews
    # ============================================

    def create_review(
        self,
        employee_id: str,
        reviewer_id: str,
        period_start: datetime,
        period_end: datetime,
        goals: Optional[List[str]] = None,
    ) -> PerformanceReview:
        """Create performance review."""
        review = PerformanceReview(
            review_id=self._generate_id("review"),
            employee_id=employee_id,
            reviewer_id=reviewer_id,
            period_start=period_start,
            period_end=period_end,
            status=ReviewStatus.NOT_STARTED,
            goals=goals or [],
        )

        self.reviews[review.review_id] = review
        logger.info(f"Created review for employee {employee_id}")
        return review

    def submit_review(
        self,
        review_id: str,
        achievements: List[str],
        areas_for_improvement: List[str],
        rating: int,
        feedback: str,
    ) -> Optional[PerformanceReview]:
        """Submit completed review."""
        if review_id not in self.reviews:
            return None

        review = self.reviews[review_id]
        review.status = ReviewStatus.COMPLETED
        review.achievements = achievements
        review.areas_for_improvement = areas_for_improvement
        review.rating = min(5, max(1, rating))  # Clamp 1-5
        review.feedback = feedback

        return review

    def get_reviews(
        self,
        employee_id: Optional[str] = None,
        status: Optional[ReviewStatus] = None,
    ) -> List[PerformanceReview]:
        """Get reviews with filtering."""
        reviews = list(self.reviews.values())

        if employee_id:
            reviews = [r for r in reviews if r.employee_id == employee_id]

        if status:
            reviews = [r for r in reviews if r.status == status]

        return reviews

    # ============================================
    # Time Off Management
    # ============================================

    def request_time_off(
        self,
        employee_id: str,
        time_off_type: TimeOffType,
        start_date: datetime,
        end_date: datetime,
        reason: str = "",
    ) -> TimeOffRequest:
        """Request time off."""
        request = TimeOffRequest(
            request_id=self._generate_id("pto"),
            employee_id=employee_id,
            time_off_type=time_off_type,
            start_date=start_date,
            end_date=end_date,
            status=TimeOffStatus.PENDING,
            reason=reason,
        )

        self.time_off_requests[request.request_id] = request
        logger.info(f"Time off request from {employee_id}: {start_date} to {end_date}")
        return request

    def approve_time_off(
        self,
        request_id: str,
        approved_by: str,
    ) -> Optional[TimeOffRequest]:
        """Approve time off request."""
        if request_id not in self.time_off_requests:
            return None

        request = self.time_off_requests[request_id]
        request.status = TimeOffStatus.APPROVED
        request.approved_by = approved_by
        request.approved_at = datetime.utcnow()

        # Update employee status if long leave
        days = (request.end_date - request.start_date).days
        if days > 14:
            employee = self.employees.get(request.employee_id)
            if employee:
                employee.status = "on_leave"

        return request

    def reject_time_off(
        self,
        request_id: str,
        approved_by: str,
        reason: str = "",
    ) -> Optional[TimeOffRequest]:
        """Reject time off request."""
        if request_id not in self.time_off_requests:
            return None

        request = self.time_off_requests[request_id]
        request.status = TimeOffStatus.REJECTED
        request.approved_by = approved_by
        request.approved_at = datetime.utcnow()

        if reason:
            request.reason = f"{request.reason} (Rejected: {reason})"

        return request

    def get_time_off_requests(
        self,
        employee_id: Optional[str] = None,
        status: Optional[TimeOffStatus] = None,
    ) -> List[TimeOffRequest]:
        """Get time off requests with filtering."""
        requests = list(self.time_off_requests.values())

        if employee_id:
            requests = [r for r in requests if r.employee_id == employee_id]

        if status:
            requests = [r for r in requests if r.status == status]

        return requests

    # ============================================
    # HR Analytics
    # ============================================

    def get_hr_metrics(self) -> Dict[str, Any]:
        """Get HR metrics summary."""
        employees = list(self.employees.values())
        active = [e for e in employees if e.status == 'active']

        # Department breakdown
        by_department = {}
        for emp in active:
            dept = emp.department
            by_department[dept] = by_department.get(dept, 0) + 1

        # Employment type breakdown
        by_type = {}
        for emp in active:
            emp_type = emp.employment_type.value
            by_type[emp_type] = by_type.get(emp_type, 0) + 1

        # Time off stats
        pending_pto = len([r for r in self.time_off_requests.values() if r.status == TimeOffStatus.PENDING])
        approved_pto = len([r for r in self.time_off_requests.values() if r.status == TimeOffStatus.APPROVED])

        # Review stats
        completed_reviews = len([r for r in self.reviews.values() if r.status == ReviewStatus.COMPLETED])

        # Onboarding stats
        active_onboardings = len([o for o in self.onboardings.values() if o.status == 'in_progress'])

        return {
            'total_employees': len(employees),
            'active_employees': len(active),
            'by_department': by_department,
            'by_employment_type': by_type,
            'time_off': {
                'pending': pending_pto,
                'approved': approved_pto,
            },
            'reviews_completed': completed_reviews,
            'active_onboardings': active_onboardings,
            'departments': self.departments,
        }

    # ============================================
    # Utilities
    # ============================================

    def _generate_id(self, prefix: str) -> str:
        """Generate a unique ID."""
        timestamp = datetime.utcnow().strftime('%Y%m%d%H%M%S')
        random_suffix = secrets.token_hex(4)
        return f"{prefix}-{timestamp}-{random_suffix}"

    def get_state(self) -> Dict[str, Any]:
        """Get agent state summary."""
        return {
            'agent_id': self.agent_id,
            'employees_count': len(self.employees),
            'active_employees': len([e for e in self.employees.values() if e.status == 'active']),
            'onboardings_count': len(self.onboardings),
            'reviews_count': len(self.reviews),
            'time_off_requests': len(self.time_off_requests),
        }


def get_capabilities() -> Dict[str, Any]:
    """Return agent capabilities for orchestration."""
    return {
        'agent_type': 'hr',
        'version': '1.0.0',
        'capabilities': [
            'hire_employee',
            'terminate_employee',
            'get_employee',
            'get_employees',
            'update_employee',
            'create_onboarding',
            'complete_onboarding_task',
            'get_onboarding_progress',
            'create_review',
            'submit_review',
            'get_reviews',
            'request_time_off',
            'approve_time_off',
            'reject_time_off',
            'get_time_off_requests',
            'get_hr_metrics',
        ],
        'employment_types': [t.value for t in EmploymentType],
        'review_statuses': [s.value for s in ReviewStatus],
        'time_off_types': [t.value for t in TimeOffType],
        'time_off_statuses': [s.value for s in TimeOffStatus],
    }


if __name__ == "__main__":
    # Quick test
    agent = HRAgent()

    # Hire employee
    emp = agent.hire_employee(
        name="John Doe",
        email="john@example.com",
        department="engineering",
        position="Software Engineer",
        employment_type=EmploymentType.FULL_TIME,
        salary=100000.0,
        location="Remote",
        skills=['Python', 'JavaScript', 'AWS'],
    )

    print(f"Hired: {emp.name} ({emp.employee_id})")
    print(f"Department: {emp.department}")
    print(f"Position: {emp.position}")

    # Create onboarding
    onboarding = agent.create_onboarding(emp.employee_id, datetime.utcnow())
    print(f"\nOnboarding created: {onboarding.progress}% complete")

    # Complete a task
    agent.complete_onboarding_task(onboarding.onboarding_id, "Complete HR paperwork")
    print(f"After task: {onboarding.progress:.0f}% complete")

    print(f"\nState: {agent.get_state()}")
