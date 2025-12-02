import enum


class TenantsPlan(enum.StrEnum):
    LITE = "lite"
    STANDARD = "standard"
    PRO = "pro"


class TenantUserRole(enum.StrEnum):
    OWNER = "owner"
    ADMIN = "admin"
    MANAGER = "manager"
    STAFF = "staff"


class TimeSlotStatus(enum.StrEnum):
    AVAILABLE = "available"
    BLOCKED = "blocked"
    BOOKED = "booked"
    EXPIRED = "expired"

class BookingStatus(enum.StrEnum):
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"
    NO_SHOW = "no_show"
    DONE = "done"
    NO_HISTORY = "no_history"