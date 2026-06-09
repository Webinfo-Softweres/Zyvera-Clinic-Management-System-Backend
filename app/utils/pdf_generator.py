"""
pdf_generator.py
================
Reusable PDF builder for the Homoeo Clinic Management System.
Uses the `reportlab` library to produce professional-quality PDFs.

Functions
---------
generate_daily_pdf(data, clinic_name) -> bytes
generate_monthly_pdf(data, clinic_name) -> bytes
generate_patient_history_pdf(data, clinic_name) -> bytes
generate_doctor_summary_pdf(data, clinic_name) -> bytes
"""

from __future__ import annotations

import io
from datetime import datetime
from typing import Any, Dict, List, Optional

try:
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import cm
    from reportlab.platypus import (
        SimpleDocTemplate,
        Paragraph,
        Spacer,
        Table,
        TableStyle,
        HRFlowable,
    )
    from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
    REPORTLAB_AVAILABLE = True
except ImportError:  # pragma: no cover
    REPORTLAB_AVAILABLE = False


# ── Colour palette ────────────────────────────────────────────────────────────
PRIMARY = colors.HexColor("#1a56db")
PRIMARY_LIGHT = colors.HexColor("#e8f0fe")
HEADER_BG = colors.HexColor("#1e3a5f")
ALT_ROW = colors.HexColor("#f3f6fb")
TEXT_DARK = colors.HexColor("#1f2937")
TEXT_MUTED = colors.HexColor("#6b7280")
WHITE = colors.white


# ── Base builder ──────────────────────────────────────────────────────────────

def _base_doc(buffer: io.BytesIO) -> SimpleDocTemplate:
    return SimpleDocTemplate(
        buffer,
        pagesize=A4,
        leftMargin=2 * cm,
        rightMargin=2 * cm,
        topMargin=2 * cm,
        bottomMargin=2 * cm,
    )


def _styles():
    ss = getSampleStyleSheet()
    clinic_title = ParagraphStyle(
        "ClinicTitle",
        parent=ss["Heading1"],
        fontSize=18,
        textColor=HEADER_BG,
        spaceAfter=2,
        alignment=TA_CENTER,
    )
    report_subtitle = ParagraphStyle(
        "ReportSubtitle",
        parent=ss["Normal"],
        fontSize=11,
        textColor=TEXT_MUTED,
        spaceAfter=4,
        alignment=TA_CENTER,
    )
    section_header = ParagraphStyle(
        "SectionHeader",
        parent=ss["Heading2"],
        fontSize=12,
        textColor=PRIMARY,
        spaceBefore=14,
        spaceAfter=6,
    )
    body = ParagraphStyle(
        "Body",
        parent=ss["Normal"],
        fontSize=10,
        textColor=TEXT_DARK,
        leading=14,
    )
    return ss, clinic_title, report_subtitle, section_header, body


def _header_table_style() -> TableStyle:
    return TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), HEADER_BG),
        ("TEXTCOLOR", (0, 0), (-1, 0), WHITE),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, 0), 10),
        ("BOTTOMPADDING", (0, 0), (-1, 0), 8),
        ("TOPPADDING", (0, 0), (-1, 0), 8),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [WHITE, ALT_ROW]),
        ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
        ("FONTSIZE", (0, 1), (-1, -1), 9),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#d1d5db")),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 1), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 1), (-1, -1), 5),
    ])


def _clinic_header(clinic_name: str, report_title: str, subtitle: str = "") -> list:
    """Return common header flowables: clinic name, report title, generated date."""
    _, ct, rs, *_ = _styles()
    now = datetime.now().strftime("%d %b %Y %H:%M")
    items = [
        Paragraph(clinic_name, ct),
        Paragraph(report_title, rs),
    ]
    if subtitle:
        items.append(Paragraph(subtitle, rs))
    items += [
        Paragraph(f"Generated: {now}", rs),
        HRFlowable(width="100%", thickness=1.5, color=PRIMARY, spaceAfter=12),
    ]
    return items


def _summary_box(rows: List[tuple]) -> Table:
    """Render a two-column key/value summary table."""
    data = [[k, v] for k, v in rows]
    t = Table(data, colWidths=[7 * cm, 9 * cm])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, -1), PRIMARY_LIGHT),
        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 10),
        ("TEXTCOLOR", (0, 0), (-1, -1), TEXT_DARK),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#d1d5db")),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("LEFTPADDING", (0, 0), (-1, -1), 10),
    ]))
    return t


def _no_reportlab() -> bytes:
    """Fallback when reportlab is not installed."""
    return b"%PDF-1.4\nreportlab not installed. Run: pip install reportlab"


# ── Daily PDF ─────────────────────────────────────────────────────────────────

def generate_daily_pdf(data: Dict[str, Any], clinic_name: str = "Clinic") -> bytes:
    """Generate a professional daily registration report PDF."""
    if not REPORTLAB_AVAILABLE:
        return _no_reportlab()

    buffer = io.BytesIO()
    doc = _base_doc(buffer)
    _, _, _, section_hdr, body = _styles()

    report_date = str(data.get("report_date", "N/A"))
    story = _clinic_header(
        clinic_name,
        "Daily Registration Report",
        f"Date: {report_date}",
    )

    story.append(Paragraph("Summary", section_hdr))
    story.append(_summary_box([
        ("Report Date", report_date),
        ("Centre Code", str(data.get("centre_code", ""))),
        ("Total Registrations", str(data.get("total_registrations", 0))),
        ("New Patients", str(data.get("new_patients", 0))),
    ]))
    story.append(Spacer(1, 1 * cm))

    doc.build(story)
    return buffer.getvalue()


# ── Monthly PDF ───────────────────────────────────────────────────────────────

def generate_monthly_pdf(data: Dict[str, Any], clinic_name: str = "Clinic") -> bytes:
    """Generate a monthly report PDF with daily breakdown table."""
    if not REPORTLAB_AVAILABLE:
        return _no_reportlab()

    buffer = io.BytesIO()
    doc = _base_doc(buffer)
    _, _, _, section_hdr, body = _styles()

    month = data.get("month", "")
    year = data.get("year", "")
    story = _clinic_header(
        clinic_name,
        "Monthly Registration Report",
        f"Period: {month:02d}/{year}",
    )

    story.append(Paragraph("Summary", section_hdr))
    story.append(_summary_box([
        ("Month / Year", f"{month:02d} / {year}"),
        ("Centre Code", str(data.get("centre_code", ""))),
        ("Monthly Total", str(data.get("monthly_total", 0))),
    ]))

    story.append(Spacer(1, 0.5 * cm))
    story.append(Paragraph("Daily Breakdown", section_hdr))

    breakdown = data.get("daily_breakdown", [])
    table_data = [["Date", "Registrations"]]
    for row in breakdown:
        table_data.append([str(row.get("report_date", "")), str(row.get("registrations", 0))])

    if len(table_data) > 1:
        t = Table(table_data, colWidths=[9 * cm, 7 * cm])
        t.setStyle(_header_table_style())
        story.append(t)
    else:
        story.append(Paragraph("No data for this period.", body))

    story.append(Spacer(1, 1 * cm))
    doc.build(story)
    return buffer.getvalue()


# ── Patient History PDF ───────────────────────────────────────────────────────

def generate_patient_history_pdf(data: Dict[str, Any], clinic_name: str = "Clinic") -> bytes:
    """Generate a patient history PDF including all clinical page data."""
    if not REPORTLAB_AVAILABLE:
        return _no_reportlab()

    buffer = io.BytesIO()
    doc = _base_doc(buffer)
    _, _, _, section_hdr, body = _styles()

    patient = data.get("patient")
    if patient and hasattr(patient, "__dict__"):
        patient = {
            "patient_name": getattr(patient, "patient_name", ""),
            "hospital_no": getattr(patient, "hospital_no", ""),
            "mobile": getattr(patient, "mobile", ""),
            "age": getattr(patient, "age", ""),
            "gender": getattr(patient, "gender", ""),
            "address": getattr(patient, "address", ""),
            "reg_date": str(getattr(patient, "reg_date", "")),
        }
    patient = patient or {}

    story = _clinic_header(
        clinic_name,
        "Patient History Report",
        f"Hospital No: {patient.get('hospital_no', 'N/A')}",
    )

    story.append(Paragraph("Patient Details", section_hdr))
    story.append(_summary_box([
        ("Name", str(patient.get("patient_name", ""))),
        ("Hospital No", str(patient.get("hospital_no", ""))),
        ("Mobile", str(patient.get("mobile", ""))),
        ("Age", str(patient.get("age", ""))),
        ("Gender", str(patient.get("gender", ""))),
        ("Address", str(patient.get("address", ""))),
        ("Registration Date", str(patient.get("reg_date", ""))),
    ]))

    story.append(Spacer(1, 0.5 * cm))
    story.append(Paragraph("Clinical Pages", section_hdr))

    pages = data.get("clinical_pages", [])
    for page in pages:
        if hasattr(page, "__dict__"):
            page_no = getattr(page, "page_no", "?")
            page_data = getattr(page, "page_data", {}) or {}
        else:
            page_no = page.get("page_no", "?")
            page_data = page.get("page_data", {}) or {}

        story.append(Paragraph(f"Page {page_no}", section_hdr))
        if page_data:
            rows = [(k, str(v)) for k, v in page_data.items()]
            story.append(_summary_box(rows))
        else:
            story.append(Paragraph("No data recorded.", body))
        story.append(Spacer(1, 0.3 * cm))

    story.append(Paragraph("Timeline", section_hdr))
    timeline = data.get("timeline", [])
    if timeline:
        table_data = [["Event", "Page", "Timestamp"]]
        for entry in timeline:
            table_data.append([
                str(entry.get("event", "")),
                str(entry.get("page_no", "")),
                str(entry.get("timestamp", "")),
            ])
        t = Table(table_data, colWidths=[7 * cm, 3 * cm, 8 * cm])
        t.setStyle(_header_table_style())
        story.append(t)
    else:
        story.append(Paragraph("No timeline events.", body))

    story.append(Spacer(1, 1 * cm))
    doc.build(story)
    return buffer.getvalue()


# ── Doctor Summary PDF ────────────────────────────────────────────────────────

def generate_doctor_summary_pdf(data: Dict[str, Any], clinic_name: str = "Clinic") -> bytes:
    """Generate a doctor summary PDF for a date range."""
    if not REPORTLAB_AVAILABLE:
        return _no_reportlab()

    buffer = io.BytesIO()
    doc = _base_doc(buffer)
    _, _, _, section_hdr, body = _styles()

    from_date = str(data.get("from_date", ""))
    to_date = str(data.get("to_date", ""))

    story = _clinic_header(
        clinic_name,
        "Doctor Summary Report",
        f"Period: {from_date} to {to_date}",
    )

    story.append(Paragraph("Summary", section_hdr))
    story.append(_summary_box([
        ("Centre Code", str(data.get("centre_code", ""))),
        ("From Date", from_date),
        ("To Date", to_date),
        ("Patients Seen", str(data.get("patients_seen", 0))),
        ("Cases Created", str(data.get("cases_created", 0))),
        ("Clinical Records Entered", str(data.get("clinical_records_entered", 0))),
    ]))
    story.append(Spacer(1, 1 * cm))

    doc.build(story)
    return buffer.getvalue()
