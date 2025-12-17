from datetime import datetime, timezone
from typing import TYPE_CHECKING

from sentio.core.enums import BookingStatus

if TYPE_CHECKING:
    from sentio.models.booking import Booking


def check_customer_last_booking_status(booking: Booking) -> None:
    if booking.tenant_customer.last_booking_status not in [
        BookingStatus.DONE,
        BookingStatus.NO_HISTORY,
    ]:
        if booking.tenant_customer.late_cancellation:
            booking.tenant_customer.is_active = False

        else:
            booking.tenant_customer.late_cancellation = True
            booking.tenant_customer.last_booking_status = BookingStatus.CANCELLED_LATE
    else:
        booking.tenant_customer.last_booking_status = BookingStatus.CANCELLED_LATE


def check_time_to_start(booking: Booking) -> int:
    now = datetime.now(timezone.utc)
    slot_start = booking.time_slot.start_at.astimezone(timezone.utc)
    delta = slot_start - now
    seconds_left = int(delta.total_seconds())

    return seconds_left
