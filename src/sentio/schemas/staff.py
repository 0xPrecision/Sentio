from pydantic import BaseModel


class StaffMemberCreate(BaseModel):
    display_name: str
    bio: str | None = None
    color_hex: str | None = None


class StaffMemberRead(BaseModel):
    display_name: str
    bio: str | None = None
    color_hex: str | None = None


class StaffMemberUpdate(BaseModel):
    display_name: str | None = None
    bio: str | None = None
    color_hex: str | None = None
    is_active: bool | None = None


class StaffServiceCreate(BaseModel):
    staff_member_id: int
    service_id: int


class StaffServiceRead(BaseModel):
    staff_member_id: int
    service_id: int
