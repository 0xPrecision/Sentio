from sentio.core.exceptions import SentioError


class BookingError(SentioError):
    pass


class BookingStatusError(BookingError):
    pass


class DateValidationError(BookingError):
    pass


class TimeSlotNotFoundError(BookingError):
    def __init__(self, *, tenant_id: int, time_slot_id: int) -> None:
        self.tenant_id = tenant_id
        self.time_slot_id = time_slot_id


class SlotNotAvailableError(BookingError):
    pass
