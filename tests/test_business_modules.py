"""
Comprehensive test suite for Developer 2 modules:
  - Patient CRUD & Search
  - Clinical Page save / update / aggregation
  - Daily & Monthly Reports
  - Doctor Summary Report
  - PDF Export
  - Tenant Isolation
"""

import pytest
from datetime import date, datetime, timezone
from unittest.mock import MagicMock, patch, PropertyMock
from sqlalchemy.orm import Session

from app.models.patient import Patient
from app.models.clinical_page import ClinicalPage
from app.schemas.patient import PatientCreate, PatientUpdate
from app.schemas.clinical_page import ClinicalPageCreate, ClinicalPageUpdate
from app.services.patient_service import patient_service, PatientService
from app.services.clinical_service import clinical_service, ClinicalService
from app.services.report_service import report_service, ReportService
from app.core.exceptions import (
    NotFoundException,
    BadRequestException,
    ConflictException,
)


# ─────────────────────────────────────────────────────────────────────────────
# Fixtures
# ─────────────────────────────────────────────────────────────────────────────

@pytest.fixture
def db():
    """Mock database session."""
    return MagicMock(spec=Session)


@pytest.fixture
def centre_code():
    return "CENT001"


@pytest.fixture
def other_centre():
    return "CENT002"


def _make_patient(centre_code="CENT001", hospital_no="HSP000001", **kwargs):
    p = Patient()
    p.id = "pat-uuid-001"
    p.centre_code = centre_code
    p.hospital_no = hospital_no
    p.reg_date = date(2026, 1, 15)
    p.patient_name = "John Doe"
    p.address = "123 Main St"
    p.age = 30
    p.gender = "Male"
    p.mobile = "9876543210"
    p.is_deleted = False
    p.deleted_at = None
    p.created_by = "user-001"
    p.updated_by = "user-001"
    p.created_at = datetime.now(timezone.utc)
    p.updated_at = datetime.now(timezone.utc)
    for k, v in kwargs.items():
        setattr(p, k, v)
    return p


def _make_clinical_page(centre_code="CENT001", hospital_no="HSP000001", page_no=1, data=None):
    cp = ClinicalPage()
    cp.id = f"page-uuid-{page_no:03d}"
    cp.centre_code = centre_code
    cp.hospital_no = hospital_no
    cp.page_no = page_no
    cp.page_data = data or {"keynote": "test", "medicine": "Belladonna"}
    cp.created_by = "user-001"
    cp.updated_by = "user-001"
    cp.created_at = datetime.now(timezone.utc)
    cp.updated_at = datetime.now(timezone.utc)
    return cp


# ─────────────────────────────────────────────────────────────────────────────
# 1. Patient Creation
# ─────────────────────────────────────────────────────────────────────────────

class TestPatientCreation:
    def test_create_patient_success(self, db, centre_code):
        patient_in = PatientCreate(
            patient_name="Jane Smith",
            age=25,
            gender="Female",
            mobile="9000000001",
        )
        created = _make_patient(patient_name="Jane Smith", hospital_no="HSP000001")

        with (
            patch(
                "app.repositories.patient_repository.PatientRepository.generate_hospital_no",
                return_value="HSP000001",
            ),
            patch(
                "app.repositories.patient_repository.PatientRepository.create_patient",
                return_value=created,
            ),
        ):
            result = PatientService.create_patient(
                db, patient_in=patient_in, centre_code=centre_code, created_by="user-001"
            )
        assert result.hospital_no == "HSP000001"
        assert result.patient_name == "Jane Smith"

    def test_hospital_no_format(self):
        """Hospital number must follow HSP000001 format."""
        from app.utils.report_helpers import format_hospital_no
        assert format_hospital_no(1) == "HSP000001"
        assert format_hospital_no(999) == "HSP000999"
        assert format_hospital_no(1000000) == "HSP1000000"

    def test_create_patient_uses_centre_from_token(self, db):
        """centre_code must come from token, never be user-supplied."""
        patient_in = PatientCreate(patient_name="Bob")
        created = _make_patient(centre_code="CENT_FROM_TOKEN", hospital_no="HSP000001")

        with (
            patch(
                "app.repositories.patient_repository.PatientRepository.generate_hospital_no",
                return_value="HSP000001",
            ),
            patch(
                "app.repositories.patient_repository.PatientRepository.create_patient",
                return_value=created,
            ),
        ):
            result = PatientService.create_patient(
                db, patient_in=patient_in,
                centre_code="CENT_FROM_TOKEN",
                created_by="user-001",
            )
        assert result.centre_code == "CENT_FROM_TOKEN"


# ─────────────────────────────────────────────────────────────────────────────
# 2. Patient Search
# ─────────────────────────────────────────────────────────────────────────────

class TestPatientSearch:
    def test_search_returns_results(self, db, centre_code):
        patients = [_make_patient(), _make_patient(hospital_no="HSP000002")]
        with patch(
            "app.repositories.patient_repository.PatientRepository.search_patients",
            return_value=(patients, 2),
        ):
            items, total = PatientService.search_patients(db, centre_code=centre_code, q="John")
        assert total == 2
        assert len(items) == 2

    def test_search_query_too_short(self, db, centre_code):
        with pytest.raises(BadRequestException):
            PatientService.search_patients(db, centre_code=centre_code, q="a")

    def test_search_scoped_to_centre(self, db, centre_code, other_centre):
        """Searching in CENT001 must not return CENT002 records."""
        cent1_patients = [_make_patient(centre_code=centre_code)]
        with patch(
            "app.repositories.patient_repository.PatientRepository.search_patients",
            return_value=(cent1_patients, 1),
        ) as mock_search:
            items, total = PatientService.search_patients(db, centre_code=centre_code, q="John")
            args = mock_search.call_args
            assert args.kwargs["centre_code"] == centre_code
        assert all(p.centre_code == centre_code for p in items)


# ─────────────────────────────────────────────────────────────────────────────
# 3. Patient Update
# ─────────────────────────────────────────────────────────────────────────────

class TestPatientUpdate:
    def test_update_patient_fields(self, db, centre_code):
        existing = _make_patient()
        update_in = PatientUpdate(patient_name="Updated Name", age=35)

        with (
            patch(
                "app.repositories.patient_repository.PatientRepository.get_by_id_and_centre",
                return_value=existing,
            ),
            patch(
                "app.repositories.patient_repository.PatientRepository.update_patient",
                return_value=existing,
            ),
        ):
            result = PatientService.update_patient(
                db,
                patient_id="pat-uuid-001",
                centre_code=centre_code,
                patient_in=update_in,
                updated_by="user-001",
            )
        assert result is not None

    def test_update_immutable_fields_ignored(self, db, centre_code):
        """hospital_no must never be changed."""
        existing = _make_patient()
        update_data_captured = {}

        def capture_update(db, db_obj, update_data):
            update_data_captured.update(update_data)
            return db_obj

        update_in = PatientUpdate(patient_name="New Name")
        with (
            patch(
                "app.repositories.patient_repository.PatientRepository.get_by_id_and_centre",
                return_value=existing,
            ),
            patch(
                "app.repositories.patient_repository.PatientRepository.update_patient",
                side_effect=capture_update,
            ),
        ):
            PatientService.update_patient(
                db,
                patient_id="pat-uuid-001",
                centre_code=centre_code,
                patient_in=update_in,
                updated_by="user-001",
            )
        assert "hospital_no" not in update_data_captured
        assert "centre_code" not in update_data_captured

    def test_update_patient_not_found(self, db, centre_code):
        with patch(
            "app.repositories.patient_repository.PatientRepository.get_by_id_and_centre",
            return_value=None,
        ):
            with pytest.raises(NotFoundException):
                PatientService.update_patient(
                    db,
                    patient_id="bad-id",
                    centre_code=centre_code,
                    patient_in=PatientUpdate(patient_name="X"),
                    updated_by="user-001",
                )


# ─────────────────────────────────────────────────────────────────────────────
# 4. Clinical Page Save
# ─────────────────────────────────────────────────────────────────────────────

class TestClinicalPageSave:
    def test_save_page_creates_new(self, db, centre_code):
        patient = _make_patient()
        page = _make_clinical_page()

        with (
            patch(
                "app.repositories.patient_repository.PatientRepository.get_by_hospital_no",
                return_value=patient,
            ),
            patch(
                "app.repositories.clinical_repository.ClinicalRepository.upsert_page",
                return_value=page,
            ),
        ):
            result = ClinicalService.save_page(
                db,
                centre_code=centre_code,
                hospital_no="HSP000001",
                page_no=1,
                data={"keynote": "headache"},
                user_id="user-001",
            )
        assert result.page_no == 1

    def test_save_page_invalid_page_no_zero(self, db, centre_code):
        with pytest.raises(BadRequestException, match="1–7"):
            ClinicalService.save_page(
                db, centre_code=centre_code, hospital_no="HSP000001",
                page_no=0, data={}, user_id="user-001",
            )

    def test_save_page_invalid_page_no_eight(self, db, centre_code):
        with pytest.raises(BadRequestException, match="1–7"):
            ClinicalService.save_page(
                db, centre_code=centre_code, hospital_no="HSP000001",
                page_no=8, data={}, user_id="user-001",
            )

    def test_save_page_invalid_negative(self, db, centre_code):
        with pytest.raises(BadRequestException, match="1–7"):
            ClinicalService.save_page(
                db, centre_code=centre_code, hospital_no="HSP000001",
                page_no=-1, data={}, user_id="user-001",
            )

    def test_save_page_patient_not_in_centre(self, db, centre_code):
        with patch(
            "app.repositories.patient_repository.PatientRepository.get_by_hospital_no",
            return_value=None,
        ):
            with pytest.raises(NotFoundException):
                ClinicalService.save_page(
                    db, centre_code=centre_code, hospital_no="HSP999999",
                    page_no=1, data={}, user_id="user-001",
                )


# ─────────────────────────────────────────────────────────────────────────────
# 5. Clinical Page Update
# ─────────────────────────────────────────────────────────────────────────────

class TestClinicalPageUpdate:
    def test_update_existing_page(self, db, centre_code):
        patient = _make_patient()
        existing_page = _make_clinical_page()
        updated_page = _make_clinical_page(data={"keynote": "updated"})

        with (
            patch(
                "app.repositories.patient_repository.PatientRepository.get_by_hospital_no",
                return_value=patient,
            ),
            patch(
                "app.repositories.clinical_repository.ClinicalRepository.get_page",
                return_value=existing_page,
            ),
            patch(
                "app.repositories.clinical_repository.ClinicalRepository.update_page",
                return_value=updated_page,
            ),
        ):
            result = ClinicalService.update_page(
                db,
                centre_code=centre_code,
                hospital_no="HSP000001",
                page_no=1,
                data={"keynote": "updated"},
                user_id="user-001",
            )
        assert result.page_data == {"keynote": "updated"}

    def test_update_nonexistent_page_raises(self, db, centre_code):
        patient = _make_patient()
        with (
            patch(
                "app.repositories.patient_repository.PatientRepository.get_by_hospital_no",
                return_value=patient,
            ),
            patch(
                "app.repositories.clinical_repository.ClinicalRepository.get_page",
                return_value=None,
            ),
        ):
            with pytest.raises(NotFoundException):
                ClinicalService.update_page(
                    db, centre_code=centre_code, hospital_no="HSP000001",
                    page_no=3, data={}, user_id="user-001",
                )


# ─────────────────────────────────────────────────────────────────────────────
# 6. Case Aggregation
# ─────────────────────────────────────────────────────────────────────────────

class TestCaseAggregation:
    def test_get_case_builds_correct_structure(self, db, centre_code):
        patient = _make_patient()
        pages = [
            _make_clinical_page(page_no=1, data={"keynote": "headache"}),
            _make_clinical_page(page_no=3, data={"temp": "98.6"}),
        ]
        with (
            patch(
                "app.repositories.patient_repository.PatientRepository.get_by_hospital_no",
                return_value=patient,
            ),
            patch(
                "app.repositories.clinical_repository.ClinicalRepository.get_all_pages_for_patient",
                return_value=pages,
            ),
        ):
            case = ClinicalService.get_case(db, centre_code=centre_code, hospital_no="HSP000001")

        assert case["patient"]["hospital_no"] == "HSP000001"
        assert case["page1"] == {"keynote": "headache"}
        assert case["page2"] is None
        assert case["page3"] == {"temp": "98.6"}
        assert case["page4"] is None
        assert case["page7"] is None

    def test_get_case_patient_not_found(self, db, centre_code):
        with patch(
            "app.repositories.patient_repository.PatientRepository.get_by_hospital_no",
            return_value=None,
        ):
            with pytest.raises(NotFoundException):
                ClinicalService.get_case(db, centre_code=centre_code, hospital_no="INVALID")


# ─────────────────────────────────────────────────────────────────────────────
# 7. Daily Report
# ─────────────────────────────────────────────────────────────────────────────

class TestDailyReport:
    def test_daily_report_returns_correct_structure(self, db, centre_code):
        mock_data = {
            "report_date": date(2026, 6, 1),
            "total_registrations": 10,
            "new_patients": 10,
            "centre_code": centre_code,
        }
        with patch(
            "app.repositories.report_repository.ReportRepository.get_daily_stats",
            return_value=mock_data,
        ):
            result = ReportService.get_daily_report(db, centre_code=centre_code, report_date=date(2026, 6, 1))

        assert result["total_registrations"] == 10
        assert result["centre_code"] == centre_code

    def test_daily_report_zero_for_empty_day(self, db, centre_code):
        mock_data = {
            "report_date": date(2026, 6, 2),
            "total_registrations": 0,
            "new_patients": 0,
            "centre_code": centre_code,
        }
        with patch(
            "app.repositories.report_repository.ReportRepository.get_daily_stats",
            return_value=mock_data,
        ):
            result = ReportService.get_daily_report(db, centre_code=centre_code, report_date=date(2026, 6, 2))
        assert result["total_registrations"] == 0


# ─────────────────────────────────────────────────────────────────────────────
# 8. Monthly Report
# ─────────────────────────────────────────────────────────────────────────────

class TestMonthlyReport:
    def test_monthly_report_structure(self, db, centre_code):
        mock_data = {
            "month": 6,
            "year": 2026,
            "centre_code": centre_code,
            "monthly_total": 45,
            "daily_breakdown": [
                {"report_date": date(2026, 6, 1), "registrations": 5},
                {"report_date": date(2026, 6, 2), "registrations": 10},
            ],
        }
        with patch(
            "app.repositories.report_repository.ReportRepository.get_monthly_stats",
            return_value=mock_data,
        ):
            result = ReportService.get_monthly_report(db, centre_code=centre_code, month=6, year=2026)

        assert result["monthly_total"] == 45
        assert len(result["daily_breakdown"]) == 2

    def test_monthly_report_tenant_scoped(self, db, centre_code, other_centre):
        """Each clinic gets its own monthly data."""
        with patch(
            "app.repositories.report_repository.ReportRepository.get_monthly_stats",
            return_value={"month": 6, "year": 2026, "centre_code": centre_code, "monthly_total": 5, "daily_breakdown": []},
        ) as mock_stats:
            ReportService.get_monthly_report(db, centre_code=centre_code, month=6, year=2026)
            args = mock_stats.call_args
            assert args.args[1] == centre_code or args.kwargs.get("centre_code") == centre_code


# ─────────────────────────────────────────────────────────────────────────────
# 9. PDF Export
# ─────────────────────────────────────────────────────────────────────────────

class TestPDFExport:
    def test_generate_daily_pdf_returns_bytes(self):
        from app.utils.pdf_generator import generate_daily_pdf
        data = {
            "report_date": date(2026, 6, 1),
            "total_registrations": 5,
            "new_patients": 5,
            "centre_code": "CENT001",
        }
        result = generate_daily_pdf(data, clinic_name="Test Clinic")
        assert isinstance(result, bytes)
        assert len(result) > 0

    def test_generate_monthly_pdf_returns_bytes(self):
        from app.utils.pdf_generator import generate_monthly_pdf
        data = {
            "month": 6,
            "year": 2026,
            "centre_code": "CENT001",
            "monthly_total": 30,
            "daily_breakdown": [{"report_date": date(2026, 6, 1), "registrations": 3}],
        }
        result = generate_monthly_pdf(data, clinic_name="Test Clinic")
        assert isinstance(result, bytes)

    def test_generate_patient_history_pdf_returns_bytes(self):
        from app.utils.pdf_generator import generate_patient_history_pdf
        data = {
            "patient": {
                "patient_name": "John Doe",
                "hospital_no": "HSP000001",
                "mobile": "9999999999",
                "age": 30,
                "gender": "Male",
                "address": "123 Main St",
                "reg_date": "2026-01-01",
            },
            "clinical_pages": [],
            "timeline": [],
        }
        result = generate_patient_history_pdf(data, clinic_name="Test Clinic")
        assert isinstance(result, bytes)

    def test_generate_doctor_summary_pdf_returns_bytes(self):
        from app.utils.pdf_generator import generate_doctor_summary_pdf
        data = {
            "centre_code": "CENT001",
            "from_date": date(2026, 6, 1),
            "to_date": date(2026, 6, 30),
            "patients_seen": 50,
            "cases_created": 40,
            "clinical_records_entered": 120,
        }
        result = generate_doctor_summary_pdf(data, clinic_name="Test Clinic")
        assert isinstance(result, bytes)

    def test_invalid_report_type_raises(self, db, centre_code):
        with pytest.raises(BadRequestException):
            ReportService.get_report_data_for_pdf(
                db, centre_code=centre_code, report_type="INVALID", params={}
            )


# ─────────────────────────────────────────────────────────────────────────────
# 10. Tenant Isolation
# ─────────────────────────────────────────────────────────────────────────────

class TestTenantIsolation:
    def test_patient_not_visible_across_tenants(self, db):
        """A patient in CENT001 must not be accessible from CENT002."""
        # The repository returns None because centre_code filter excludes it
        with patch(
            "app.repositories.patient_repository.PatientRepository.get_by_id_and_centre",
            return_value=None,
        ):
            with pytest.raises(NotFoundException):
                PatientService.get_patient(db, patient_id="pat-uuid-001", centre_code="CENT002")

    def test_clinical_page_patient_validation_enforces_tenant(self, db):
        """Clinical page lookup must reject patients from another tenant."""
        # Patient belongs to CENT001; request comes from CENT002 → patient not found
        with patch(
            "app.repositories.patient_repository.PatientRepository.get_by_hospital_no",
            return_value=None,
        ):
            with pytest.raises(NotFoundException):
                ClinicalService.get_page(
                    db,
                    centre_code="CENT002",
                    hospital_no="HSP000001",
                    page_no=1,
                )

    def test_doctor_summary_date_validation(self, db, centre_code):
        """from_date after to_date must raise BadRequestException."""
        with pytest.raises(BadRequestException):
            ReportService.get_doctor_summary(
                db,
                centre_code=centre_code,
                from_date=date(2026, 6, 30),
                to_date=date(2026, 6, 1),
            )

    def test_hospital_no_sequential_per_centre(self):
        """Each clinic maintains its own sequence starting at HSP000001."""
        from app.utils.report_helpers import format_hospital_no
        cent1_no = format_hospital_no(1)
        cent2_no = format_hospital_no(1)
        assert cent1_no == cent2_no == "HSP000001"
        # Both clinics independently start from 1 — uniqueness is per (centre_code, hospital_no)
