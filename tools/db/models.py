import time
from sqlalchemy import Column, Float, Integer, String
from sqlalchemy import CheckConstraint
from . import Base

class Courses(Base):
    __tablename__ = 'courses'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    department = Column(String(200), nullable=False)
    grade = Column(Integer, nullable=False)
    serial_no = Column(String(20), nullable=True)
    course_id = Column(String(20), nullable=False)
    specialty = Column(String(10), nullable=True)
    semester = Column(Integer, nullable=False)
    class_type = Column(String(5), nullable=True)
    group_type = Column(String(5), nullable=True)
    required_elective_type = Column(String(5), nullable=True)
    credits = Column(Float, nullable=True)
    course_name = Column(String(200), nullable=False)
    people_limit = Column(Integer, nullable=True)
    instructor = Column(String(50), nullable=False)
    time_place = Column(String(100), nullable=True)
    
class Metadata(Base):
    __tablename__ = 'metadata'

    id = Column(Integer, primary_key=True, default=1)
    year = Column(Integer, nullable=False)
    semester = Column(Integer, nullable=False)
    created_at = Column(Integer, nullable=False, default=lambda: int(time.time()))
    last_updated = Column(Integer, nullable=False, default=lambda: int(time.time()), onupdate=lambda: int(time.time()))

    __table_args__ = (
        CheckConstraint('id = 1', name='check_single_metadata_row'),
    )
    
    