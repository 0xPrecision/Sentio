import enum


class Environment(enum.StrEnum):
    DEV = "dev"
    PROD = "prod"
    TEST = "test"


class TenantsPlan(enum.StrEnum):
    LITE = "LITE"
    STANDARD = "STANDARD"
    PRO = "PRO"


class TenantUserRole(enum.StrEnum):
    OWNER = "OWNER"
    ADMIN = "ADMIN"
    MANAGER = "MANAGER"
    STAFF = "STAFF"


class TimeSlotStatus(enum.StrEnum):
    AVAILABLE = "AVAILABLE"
    BLOCKED = "BLOCKED"
    BOOKED = "BOOKED"
    EXPIRED = "EXPIRED"


class BookingStatus(enum.StrEnum):
    CONFIRMED = "CONFIRMED"
    CANCELLED = "CANCELLED"
    CANCELLED_LATE = "CANCELLED_LATE"
    NO_SHOW = "NO_SHOW"
    DONE = "DONE"
    NO_HISTORY = "NO_HISTORY"
