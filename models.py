from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Enum, Boolean, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
import enum

Base = declarative_base()

# Create a mixin for timestamp and soft delete functionality


class TimestampMixin:
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(),
                        onupdate=func.now(), nullable=False)
    deleted_at = Column(DateTime, nullable=True)
    is_deleted = Column(Boolean, default=False, nullable=False)

# Enum definitions


class UserRole(str, enum.Enum):
    SUPER_ADMIN = "SUPER_ADMIN"
    ADMIN = "ADMIN"
    PLANT_ADMIN = "PLANT_ADMIN"
    PLANNER = "PLANNER"
    TEAM_LEADER = "TEAM_LEADER"
    MEMBER = "MEMBER"


class DayNight(str, enum.Enum):
    DAY = "DAY"
    NIGHT = "NIGHT"


class ShiftType(str, enum.Enum):
    SHIFT_A = "SHIFT-A"
    SHIFT_B = "SHIFT-B"
    SHIFT_C = "SHIFT-C"


class Hour(str, enum.Enum):
    HOUR_01 = "HOUR-01"
    HOUR_02 = "HOUR-02"
    HOUR_03 = "HOUR-03"
    HOUR_04 = "HOUR-04"
    HOUR_05 = "HOUR-05"
    HOUR_06 = "HOUR-06"
    HOUR_07 = "HOUR-07"
    HOUR_08 = "HOUR-08"
    HOUR_09 = "HOUR-09"
    HOUR_10 = "HOUR-10"
    HOUR_11 = "HOUR-11"
    HOUR_12 = "HOUR-12"

# Base models


class Plant(Base, TimestampMixin):
    __tablename__ = "plant"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)

    # Relationships
    zones = relationship("Zone", back_populates="plant")
    plant_admins = relationship("PlantAdmin", back_populates="plant")
    planners = relationship("Planner", back_populates="plant")
    shifts = relationship("Shift", back_populates="plant")


class Zone(Base, TimestampMixin):
    __tablename__ = "zone"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    plant_id = Column(Integer, ForeignKey("plant.id"))

    # Relationships
    plant = relationship("Plant", back_populates="zones")
    loops = relationship("Loop", back_populates="zone")


class Loop(Base, TimestampMixin):
    __tablename__ = "loop"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    zone_id = Column(Integer, ForeignKey("zone.id"))

    # Relationships
    zone = relationship("Zone", back_populates="loops")
    lines = relationship("Line", back_populates="loop")

    # Unnested relationships - using foreign key references is simpler
    @property
    def plant(self):
        return self.zone.plant if self.zone else None


class Line(Base, TimestampMixin):
    __tablename__ = "line"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    loop_id = Column(Integer, ForeignKey("loop.id"))

    # Relationships
    loop = relationship("Loop", back_populates="lines")
    cells = relationship("Cell", back_populates="line")
    team_leaders = relationship("TeamLeader", back_populates="line")
    productions = relationship("Production", back_populates="line")

    # Unnested relationships as properties
    @property
    def zone(self):
        return self.loop.zone if self.loop else None

    @property
    def plant(self):
        return self.loop.zone.plant if self.loop and self.loop.zone else None


class Cell(Base, TimestampMixin):
    __tablename__ = "cell"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    line_id = Column(Integer, ForeignKey("line.id"))

    # Relationships
    line = relationship("Line", back_populates="cells")
    members = relationship("Member", back_populates="cell")
    working_members = relationship(
        "Attendance", foreign_keys="Attendance.working_cell_id", back_populates="working_cell")

    # Unnested relationships as properties
    @property
    def loop(self):
        return self.line.loop if self.line else None

    @property
    def zone(self):
        return self.line.loop.zone if self.line and self.line.loop else None

    @property
    def plant(self):
        return self.line.loop.zone.plant if self.line and self.line.loop and self.line.loop.zone else None


class User(Base, TimestampMixin):
    __tablename__ = "user"

    sap_id = Column(String, primary_key=True, index=True)
    name = Column(String, index=True)
    role = Column(Enum(UserRole))
    password = Column(String)

    # Relationships
    admin = relationship("Admin", back_populates="user", uselist=False)
    plant_admin = relationship(
        "PlantAdmin", back_populates="user", uselist=False)
    planner = relationship("Planner", back_populates="user", uselist=False)
    team_leader = relationship(
        "TeamLeader", back_populates="user", uselist=False)
    member = relationship("Member", back_populates="user", uselist=False)


class Admin(Base, TimestampMixin):
    __tablename__ = "admin"

    user_id = Column(String, ForeignKey("user.sap_id"), primary_key=True)

    # Relationships
    user = relationship("User", back_populates="admin")


class PlantAdmin(Base, TimestampMixin):
    __tablename__ = "plant_admin"

    user_id = Column(String, ForeignKey("user.sap_id"), primary_key=True)
    plant_id = Column(Integer, ForeignKey("plant.id"))

    # Relationships
    user = relationship("User", back_populates="plant_admin")
    plant = relationship("Plant", back_populates="plant_admins")


class Planner(Base, TimestampMixin):
    __tablename__ = "planner"

    user_id = Column(String, ForeignKey("user.sap_id"), primary_key=True)
    plant_id = Column(Integer, ForeignKey("plant.id"))

    # Relationships
    user = relationship("User", back_populates="planner")
    plant = relationship("Plant", back_populates="planners")
    shifts = relationship("Shift", back_populates="planner")
    productions = relationship("Production", back_populates="planner")


class TeamLeader(Base, TimestampMixin):
    __tablename__ = "team_leader"

    user_id = Column(String, ForeignKey("user.sap_id"), primary_key=True)
    line_id = Column(Integer, ForeignKey("line.id"))

    # Relationships
    user = relationship("User", back_populates="team_leader")
    line = relationship("Line", back_populates="team_leaders")
    productions = relationship("Production", back_populates="team_leader")
    attendances = relationship("Attendance", back_populates="team_leader")

    # Unnested relationships as properties
    @property
    def loop(self):
        return self.line.loop if self.line else None

    @property
    def zone(self):
        return self.line.loop.zone if self.line and self.line.loop else None

    @property
    def plant(self):
        return self.line.loop.zone.plant if self.line and self.line.loop and self.line.loop.zone else None


class Member(Base, TimestampMixin):
    __tablename__ = "member"

    user_id = Column(String, ForeignKey("user.sap_id"), primary_key=True)
    cell_id = Column(Integer, ForeignKey("cell.id"))

    # Relationships
    user = relationship("User", back_populates="member")
    cell = relationship("Cell", back_populates="members")
    attendances = relationship("Attendance", back_populates="member")

    # Unnested relationships as properties
    @property
    def line(self):
        return self.cell.line if self.cell else None

    @property
    def loop(self):
        return self.cell.line.loop if self.cell and self.cell.line else None

    @property
    def zone(self):
        return self.cell.line.loop.zone if self.cell and self.cell.line and self.cell.line.loop else None

    @property
    def plant(self):
        return self.cell.line.loop.zone.plant if self.cell and self.cell.line and self.cell.line.loop and self.cell.line.loop.zone else None


class Shift(Base, TimestampMixin):
    __tablename__ = "shift"

    id = Column(Integer, primary_key=True, index=True)
    date = Column(DateTime, index=True)
    day_night = Column(Enum(DayNight))
    shift = Column(Enum(ShiftType))
    plant_id = Column(Integer, ForeignKey("plant.id"))
    planner_id = Column(String, ForeignKey("planner.user_id"))

    # Relationships
    plant = relationship("Plant", back_populates="shifts")
    planner = relationship("Planner", back_populates="shifts")
    productions = relationship("Production", back_populates="shift")
    attendances = relationship("Attendance", back_populates="shift")


class Production(Base, TimestampMixin):
    __tablename__ = "production"

    id = Column(Integer, primary_key=True, index=True)
    plan = Column(Integer)
    achievement = Column(Integer)
    scraps = Column(Integer)
    defects = Column(Integer)
    flash = Column(Integer)
    hour = Column(Enum(Hour))
    line_id = Column(Integer, ForeignKey("line.id"))
    shift_id = Column(Integer, ForeignKey("shift.id"))
    planner_id = Column(String, ForeignKey("planner.user_id"))
    team_leader_id = Column(String, ForeignKey("team_leader.user_id"))

    # Relationships
    shift = relationship("Shift", back_populates="productions")
    planner = relationship("Planner", back_populates="productions")
    team_leader = relationship("TeamLeader", back_populates="productions")
    line = relationship("Line", back_populates="productions")
    losses = relationship("Loss", back_populates="production")

    # Basic relationships
    # Using direct relationships with foreign keys for clarity
    @property
    def planner_user(self):
        return self.planner.user if self.planner else None

    @property
    def team_leader_user(self):
        return self.team_leader.user if self.team_leader else None

    # Unnested relationships as properties
    @property
    def loop(self):
        return self.line.loop if self.line else None

    @property
    def zone(self):
        return self.line.loop.zone if self.line and self.line.loop else None

    @property
    def plant(self):
        return self.line.loop.zone.plant if self.line and self.line.loop and self.line.loop.zone else None


class LossReason(Base, TimestampMixin):
    __tablename__ = "loss_reason"

    id = Column(Integer, primary_key=True, autoincrement=False)
    title = Column(String)
    department = Column(String)

    # Relationships
    losses = relationship("Loss", back_populates="loss_reason")


class Loss(Base, TimestampMixin):
    __tablename__ = "loss"

    id = Column(Integer, primary_key=True, index=True)
    amount = Column(Integer)
    loss_reason_id = Column(Integer, ForeignKey("loss_reason.id"))
    production_id = Column(Integer, ForeignKey("production.id"))

    # Relationships
    loss_reason = relationship("LossReason", back_populates="losses")
    production = relationship("Production", back_populates="losses")

    # All the unnested relationships using properties
    @property
    def shift(self):
        return self.production.shift if self.production else None

    @property
    def planner(self):
        return self.production.planner if self.production else None

    @property
    def team_leader(self):
        return self.production.team_leader if self.production else None

    @property
    def planner_user(self):
        return self.production.planner.user if self.production and self.production.planner else None

    @property
    def team_leader_user(self):
        return self.production.team_leader.user if self.production and self.production.team_leader else None

    @property
    def line(self):
        return self.production.line if self.production else None

    @property
    def loop(self):
        return self.production.line.loop if self.production and self.production.line else None

    @property
    def zone(self):
        return self.production.line.loop.zone if self.production and self.production.line and self.production.line.loop else None

    @property
    def plant(self):
        return self.production.line.loop.zone.plant if self.production and self.production.line and self.production.line.loop and self.production.line.loop.zone else None


class AttendanceType(Base, TimestampMixin):
    __tablename__ = "attendance_type"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    color = Column(String)

    # Relationships
    attendances = relationship("Attendance", back_populates="attendance_type")


class Attendance(Base, TimestampMixin):
    __tablename__ = "attendance"

    id = Column(Integer, primary_key=True, index=True)
    member_id = Column(String, ForeignKey("member.user_id"))
    attendance_type_id = Column(Integer, ForeignKey("attendance_type.id"))
    shift_id = Column(Integer, ForeignKey("shift.id"))
    working_cell_id = Column(Integer, ForeignKey("cell.id"))
    team_leader_id = Column(String, ForeignKey("team_leader.user_id"))

    # Relationships
    attendance_type = relationship(
        "AttendanceType", back_populates="attendances")
    member = relationship("Member", back_populates="attendances")
    team_leader = relationship("TeamLeader", back_populates="attendances")
    shift = relationship("Shift", back_populates="attendances")
    working_cell = relationship(
        "Cell", foreign_keys=[working_cell_id], back_populates="working_members")

    # All relationships using properties
    @property
    def member_user(self):
        return self.member.user if self.member else None

    @property
    def team_leader_user(self):
        return self.team_leader.user if self.team_leader else None

    # Working cell hierarchy
    @property
    def working_line(self):
        return self.working_cell.line if self.working_cell else None

    @property
    def working_loop(self):
        return self.working_cell.line.loop if self.working_cell and self.working_cell.line else None

    @property
    def working_zone(self):
        return self.working_cell.line.loop.zone if self.working_cell and self.working_cell.line and self.working_cell.line.loop else None

    @property
    def working_plant(self):
        return self.working_cell.line.loop.zone.plant if self.working_cell and self.working_cell.line and self.working_cell.line.loop and self.working_cell.line.loop.zone else None

    # Member's normal location hierarchy
    @property
    def member_cell(self):
        return self.member.cell if self.member else None

    @property
    def member_line(self):
        return self.member.cell.line if self.member and self.member.cell else None

    @property
    def member_loop(self):
        return self.member.cell.line.loop if self.member and self.member.cell and self.member.cell.line else None

    @property
    def member_zone(self):
        return self.member.cell.line.loop.zone if self.member and self.member.cell and self.member.cell.line and self.member.cell.line.loop else None

    @property
    def member_plant(self):
        return self.member.cell.line.loop.zone.plant if self.member and self.member.cell and self.member.cell.line and self.member.cell.line.loop and self.member.cell.line.loop.zone else None
