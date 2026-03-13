from datetime import datetime, timezone, timedelta

from sentio.core.enums import BookingStatus
from sentio.services.utils import check_customer_last_booking_status

import sentio.services.utils as utils


class DummySlot:
    def __init__(self, start_at):
        self.start_at = start_at


class DummyTenantCustomer:
    def __init__(self, last_booking_status, late_cancellation=False, is_active=True):
        self.last_booking_status = last_booking_status
        self.late_cancellation = late_cancellation
        self.is_active = is_active


class DummyBooking:
    def __init__(self, tc=None, start_at=None):
        self.tenant_customer = tc
        self.time_slot = DummySlot(start_at)


def test_check_time_to_start_positive(monkeypatch):
    fixed_now = datetime(2025, 1, 1, 12, 0, tzinfo=timezone.utc)

    class FakeDateTime(datetime):
        @classmethod
        def now(cls, tz=None):
            return fixed_now

    monkeypatch.setattr(utils, "datetime", FakeDateTime)

    booking = DummyBooking(start_at=fixed_now + timedelta(minutes=30))
    seconds = utils.check_time_to_start(booking)

    assert 1790 <= seconds <= 1810


def test_check_time_to_start_negative(monkeypatch):
    fixed_now = datetime(2025, 1, 1, 12, 0, tzinfo=timezone.utc)

    class FakeDateTime(datetime):
        @classmethod
        def now(cls, tz=None):
            return fixed_now

    monkeypatch.setattr(utils, "datetime", FakeDateTime)

    booking = DummyBooking(start_at=fixed_now + timedelta(minutes=-30))
    seconds = utils.check_time_to_start(booking)

    assert seconds < 0


def test_penalty_first_cancellation_sets_flag():
    tc = DummyTenantCustomer(last_booking_status=BookingStatus.DONE, late_cancellation=False)
    booking = DummyBooking(tc)

    check_customer_last_booking_status(booking)

    assert tc.late_cancellation is False
    assert tc.last_booking_status == BookingStatus.CANCELLED_LATE


def test_penalty_second_cancellation_sets_flag():
    tc = DummyTenantCustomer(
        last_booking_status=BookingStatus.CANCELLED_LATE, late_cancellation=False
    )
    booking = DummyBooking(tc)

    check_customer_last_booking_status(booking)

    assert tc.late_cancellation is True
    assert tc.last_booking_status == BookingStatus.CANCELLED_LATE


def test_penalty_third_cancellation_sets_flag_and_inactive():
    tc = DummyTenantCustomer(
        last_booking_status=BookingStatus.CANCELLED_LATE, late_cancellation=True, is_active=True
    )
    booking = DummyBooking(tc)

    check_customer_last_booking_status(booking)

    assert tc.is_active == False
