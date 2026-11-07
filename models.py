from datetime import datetime

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Boolean, CheckConstraint, DateTime, ForeignKey, Index, String, func, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

db = SQLAlchemy()
 
 
class Student(db.Model):
    __tablename__ = "students"
 
    id: Mapped[int] = mapped_column(primary_key=True)
    id_number: Mapped[str] = mapped_column(String(9), unique=True)
    name: Mapped[str] = mapped_column(String(100))
 
    tickets: Mapped[list["Ticket"]] = relationship(back_populates="student")
 
    __table_args__ = (
        CheckConstraint(
            "id_number ~ '^[0-9]{4}-[0-9]{4}$'",
            name="ck_students_id_number",
        ),
    )
 
 
class Service(db.Model):
    __tablename__ = "services"
 
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(80), unique=True)
    is_active: Mapped[bool] = mapped_column(
        Boolean, default=True, server_default=text("true")
    )
 
    tickets: Mapped[list["Ticket"]] = relationship(back_populates="service")
 
 
class Ticket(db.Model):
    __tablename__ = "tickets"
 
    id: Mapped[int] = mapped_column(primary_key=True)
    status: Mapped[str] = mapped_column(
        String(20), default="waiting", server_default="waiting"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    called_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    student_id: Mapped[int] = mapped_column(ForeignKey("students.id", ondelete="RESTRICT"))
    service_id: Mapped[int] = mapped_column(ForeignKey("services.id", ondelete="RESTRICT"))
 
    student: Mapped["Student"] = relationship(back_populates="tickets")
    service: Mapped["Service"] = relationship(back_populates="tickets")
 
    __table_args__ = (
        CheckConstraint(
            "status IN ('waiting', 'called', 'served', 'no-show', 'left')",
            name="ck_tickets_status",
        ),
        # FR-09: a student can have only one waiting or called ticket at a time
        Index(
            "uq_tickets_one_active_per_student",
            "student_id",
            unique=True,
            postgresql_where=text("status IN ('waiting', 'called')"),
        ),
    )