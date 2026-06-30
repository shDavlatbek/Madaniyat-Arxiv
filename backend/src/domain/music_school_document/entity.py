from __future__ import annotations

import uuid
from datetime import date, datetime

from src.domain.shared.entity import Entity


class MusicSchoolDocument(Entity):
    def __init__(
        self,
        student_full_name: str,
        music_school_id: uuid.UUID,
        specialty_id: uuid.UUID,
        graduation_year: int,
        diploma_serial: str,
        diploma_number: str,
        given_date: date,
        description: str | None = None,
        file_path: str | None = None,
        passport_series: str | None = None,
        passport_number: str | None = None,
        pinfl: str | None = None,
        extracted_text: str | None = None,
        ocr_status: str = "pending",
        ocr_completed_at: datetime | None = None,
        created_by: uuid.UUID | None = None,
        music_school_name: str | None = None,
        specialty_name: str | None = None,
        id: uuid.UUID | None = None,
        created_at: datetime | None = None,
        updated_at: datetime | None = None,
    ):
        super().__init__(id=id, created_at=created_at, updated_at=updated_at)
        
        if not student_full_name or not student_full_name.strip():
            raise ValueError("Student full name cannot be empty")
        if not specialty_id:
            raise ValueError("Specialty is required")
        if not diploma_serial or not diploma_serial.strip():
            raise ValueError("Diploma serial cannot be empty")
        if not diploma_number or not diploma_number.strip():
            raise ValueError("Diploma number cannot be empty")
            
        self.student_full_name = student_full_name.strip()
        self.music_school_id = music_school_id
        self.specialty_id = specialty_id
        self.graduation_year = graduation_year
        self.diploma_serial = diploma_serial.strip()
        self.diploma_number = diploma_number.strip()
        self.given_date = given_date
        self.description = description
        self.file_path = file_path
        self.passport_series = passport_series.strip().upper() if passport_series else None
        self.passport_number = passport_number.strip() if passport_number else None
        self.pinfl = pinfl.strip() if pinfl else None
        self.extracted_text = extracted_text
        self.ocr_status = ocr_status
        self.ocr_completed_at = ocr_completed_at
        self.created_by = created_by
        
        # Read-only relation fields populated by the mapper
        self.music_school_name = music_school_name
        self.specialty_name = specialty_name

    def update(
        self,
        student_full_name: str | None = None,
        music_school_id: uuid.UUID | None = None,
        specialty_id: uuid.UUID | None = None,
        graduation_year: int | None = None,
        diploma_serial: str | None = None,
        diploma_number: str | None = None,
        given_date: date | None = None,
        description: str | None = None,
        passport_series: str | None = None,
        passport_number: str | None = None,
        pinfl: str | None = None,
    ) -> None:
        if student_full_name is not None:
            if not student_full_name.strip():
                raise ValueError("Student full name cannot be empty")
            self.student_full_name = student_full_name.strip()
        if music_school_id is not None:
            self.music_school_id = music_school_id
        if specialty_id is not None:
            self.specialty_id = specialty_id
        if graduation_year is not None:
            self.graduation_year = graduation_year
        if diploma_serial is not None:
            if not diploma_serial.strip():
                raise ValueError("Diploma serial cannot be empty")
            self.diploma_serial = diploma_serial.strip()
        if diploma_number is not None:
            if not diploma_number.strip():
                raise ValueError("Diploma number cannot be empty")
            self.diploma_number = diploma_number.strip()
        if given_date is not None:
            self.given_date = given_date
        if description is not None:
            self.description = description
        if passport_series is not None:
            self.passport_series = passport_series.strip().upper() or None
        if passport_number is not None:
            self.passport_number = passport_number.strip() or None
        if pinfl is not None:
            self.pinfl = pinfl.strip() or None
            
        self.updated_at = datetime.utcnow()

    def set_file_path(self, file_path: str) -> None:
        self.file_path = file_path
        self.updated_at = datetime.utcnow()

    def set_ocr_result(self, extracted_text: str) -> None:
        self.extracted_text = extracted_text
        self.ocr_status = "done"
        self.ocr_completed_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()

    def set_ocr_failed(self) -> None:
        self.ocr_status = "failed"
        self.ocr_completed_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
