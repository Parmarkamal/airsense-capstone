"""
AirSense — Master Capstone Project Report Generator
File: generate_capstone_report.py
Institution: Gujarat University, Centre for Professional Courses (CPC)
Program: M.Sc. IT Business Intelligence & Analytics (2 Years) — Semester 3
"""

import sys
from pathlib import Path
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import parse_xml
from docx.oxml.ns import nsdecls

PROJECT_ROOT = Path(__file__).resolve().parent
OUTPUT_DOCX = PROJECT_ROOT / "AirSense_Capstone_Project_Report.docx"

COLOR_PRIMARY_HEX = "1E293B"      # Dark slate
COLOR_SECONDARY_HEX = "2563EB"    # Royal blue
COLOR_TEXT_HEX = "0F172A"         # Very dark slate
COLOR_BG_LIGHT_HEX = "F8FAFC"     # Light background
COLOR_BORDER_HEX = "CBD5E1"       # Light gray border
COLOR_HEADER_BG_HEX = "1E293B"    # Header fill

def set_cell_background(cell, hex_color):
    tc_pr = cell._tc.get_or_add_tcPr()
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{hex_color}"/>')
    tc_pr.append(shd)

def set_cell_margins(cell, top=100, bottom=100, left=150, right=150):
    tc_pr = cell._tc.get_or_add_tcPr()
    tc_mar = parse_xml(f'<w:tcMar {nsdecls("w")}>'
                       f'<w:top w:w="{top}" w:type="dxa"/>'
                       f'<w:bottom w:w="{bottom}" w:type="dxa"/>'
                       f'<w:left w:w="{left}" w:type="dxa"/>'
                       f'<w:right w:w="{right}" w:type="dxa"/>'
                       f'</w:tcMar>')
    tc_pr.append(tc_mar)

def set_table_borders(table):
    tbl_pr = table._tbl.tblPr
    borders = parse_xml(f'<w:tblBorders {nsdecls("w")}>'
                        f'<w:top w:val="single" w:sz="6" w:space="0" w:color="{COLOR_BORDER_HEX}"/>'
                        f'<w:bottom w:val="single" w:sz="8" w:space="0" w:color="{COLOR_PRIMARY_HEX}"/>'
                        f'<w:insideH w:val="single" w:sz="4" w:space="0" w:color="{COLOR_BORDER_HEX}"/>'
                        f'<w:insideV w:val="none"/>'
                        f'<w:left w:val="none"/>'
                        f'<w:right w:val="none"/>'
                        f'</w:tblBorders>')
    tbl_pr.append(borders)

def add_styled_paragraph(doc, text, font_size=12, bold=False, italic=False, 
                         align=WD_ALIGN_PARAGRAPH.JUSTIFY, space_before=0, space_after=6, 
                         color_rgb=RGBColor(15, 23, 42)):
    p = doc.add_paragraph()
    p.alignment = align
    p.paragraph_format.space_before = Pt(space_before)
    p.paragraph_format.space_after = Pt(space_after)
    p.paragraph_format.line_spacing = 1.15

    run = p.add_run(text)
    run.font.name = "Bookman Old Style"
    run.font.size = Pt(font_size)
    run.font.bold = bold
    run.font.italic = italic
    run.font.color.rgb = color_rgb
    return p

def add_chapter_title(doc, chapter_num, title):
    doc.add_page_break()
    p_num = doc.add_paragraph()
    p_num.alignment = WD_ALIGN_PARAGRAPH.LEFT
    p_num.paragraph_format.space_before = Pt(12)
    p_num.paragraph_format.space_after = Pt(2)
    r_num = p_num.add_run(f"CHAPTER {chapter_num}")
    r_num.font.name = "Bookman Old Style"
    r_num.font.size = Pt(14)
    r_num.font.bold = True
    r_num.font.color.rgb = RGBColor(37, 99, 235)

    p_title = doc.add_paragraph()
    p_title.alignment = WD_ALIGN_PARAGRAPH.LEFT
    p_title.paragraph_format.space_before = Pt(0)
    p_title.paragraph_format.space_after = Pt(18)
    r_title = p_title.add_run(title)
    r_title.font.name = "Bookman Old Style"
    r_title.font.size = Pt(22)
    r_title.font.bold = True
    r_title.font.color.rgb = RGBColor(30, 41, 59)
    return p_title

def add_heading_1(doc, text):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.LEFT
    p.paragraph_format.space_before = Pt(14)
    p.paragraph_format.space_after = Pt(6)
    run = p.add_run(text)
    run.font.name = "Bookman Old Style"
    run.font.size = Pt(16)
    run.font.bold = True
    run.font.color.rgb = RGBColor(30, 41, 59)
    return p

def add_heading_2(doc, text):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.LEFT
    p.paragraph_format.space_before = Pt(10)
    p.paragraph_format.space_after = Pt(4)
    run = p.add_run(text)
    run.font.name = "Bookman Old Style"
    run.font.size = Pt(14)
    run.font.bold = True
    run.font.color.rgb = RGBColor(37, 99, 235)
    return p

def add_heading_3(doc, text):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.LEFT
    p.paragraph_format.space_before = Pt(8)
    p.paragraph_format.space_after = Pt(3)
    run = p.add_run(text)
    run.font.name = "Bookman Old Style"
    run.font.size = Pt(13)
    run.font.bold = True
    run.font.italic = True
    run.font.color.rgb = RGBColor(51, 65, 85)
    return p

def add_bullet_point(doc, bold_prefix, text):
    p = doc.add_paragraph(style='List Bullet')
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(3)
    p.paragraph_format.line_spacing = 1.15

    r_pre = p.add_run(bold_prefix)
    r_pre.font.name = "Bookman Old Style"
    r_pre.font.size = Pt(12)
    r_pre.font.bold = True
    r_pre.font.color.rgb = RGBColor(15, 23, 42)

    r_text = p.add_run(" " + text)
    r_text.font.name = "Bookman Old Style"
    r_text.font.size = Pt(12)
    r_text.font.color.rgb = RGBColor(15, 23, 42)
    return p

def add_callout_box(doc, title, text):
    table = doc.add_table(rows=1, cols=1)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.autofit = False
    table.columns[0].width = Inches(6.0)

    cell = table.cell(0, 0)
    set_cell_background(cell, COLOR_BG_LIGHT_HEX)
    set_cell_margins(cell, top=140, bottom=140, left=180, right=180)

    tc_pr = cell._tc.get_or_add_tcPr()
    borders = parse_xml(f'<w:tcBorders {nsdecls("w")}>'
                        f'<w:left w:val="single" w:sz="24" w:space="0" w:color="{COLOR_SECONDARY_HEX}"/>'
                        f'<w:top w:val="none"/>'
                        f'<w:bottom w:val="none"/>'
                        f'<w:right w:val="none"/>'
                        f'</w:tcBorders>')
    tc_pr.append(borders)

    p = cell.paragraphs[0]
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p.paragraph_format.space_before = Pt(2)
    p.paragraph_format.space_after = Pt(4)
    p.paragraph_format.line_spacing = 1.15

    r_t = p.add_run(f"📌 {title}\n")
    r_t.font.name = "Bookman Old Style"
    r_t.font.size = Pt(12)
    r_t.font.bold = True
    r_t.font.color.rgb = RGBColor(30, 41, 59)

    r_b = p.add_run(text)
    r_b.font.name = "Bookman Old Style"
    r_b.font.size = Pt(11)
    r_b.font.color.rgb = RGBColor(51, 65, 85)

    p_after = doc.add_paragraph()
    p_after.paragraph_format.space_before = Pt(0)
    p_after.paragraph_format.space_after = Pt(6)

def add_figure_placeholder(doc, fig_number, caption, description=""):
    table = doc.add_table(rows=1, cols=1)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.columns[0].width = Inches(6.0)
    cell = table.cell(0, 0)
    set_cell_background(cell, "F1F5F9")
    set_cell_margins(cell, top=180, bottom=180, left=200, right=200)

    p = cell.paragraphs[0]
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_box = p.add_run(f"[ FIGURE / SYSTEM DIAGRAM ARTIFACT: {caption} ]\n")
    r_box.font.name = "Bookman Old Style"
    r_box.font.size = Pt(11)
    r_box.font.bold = True
    r_box.font.color.rgb = RGBColor(71, 85, 105)

    if description:
        r_desc = p.add_run(description)
        r_desc.font.name = "Bookman Old Style"
        r_desc.font.size = Pt(10)
        r_desc.font.italic = True
        r_desc.font.color.rgb = RGBColor(100, 116, 139)

    p_cap = doc.add_paragraph()
    p_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_cap.paragraph_format.space_before = Pt(6)
    p_cap.paragraph_format.space_after = Pt(12)
    r_c = p_cap.add_run(f"Figure {fig_number}: {caption}")
    r_c.font.name = "Bookman Old Style"
    r_c.font.size = Pt(11)
    r_c.font.bold = True
    r_c.font.color.rgb = RGBColor(30, 41, 59)

def add_academic_table(doc, headers, data, table_number, caption, col_widths=None):
    p_cap = doc.add_paragraph()
    p_cap.alignment = WD_ALIGN_PARAGRAPH.LEFT
    p_cap.paragraph_format.space_before = Pt(10)
    p_cap.paragraph_format.space_after = Pt(4)
    r_c = p_cap.add_run(f"Table {table_number}: {caption}")
    r_c.font.name = "Bookman Old Style"
    r_c.font.size = Pt(11)
    r_c.font.bold = True
    r_c.font.color.rgb = RGBColor(30, 41, 59)

    table = doc.add_table(rows=len(data) + 1, cols=len(headers))
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(table)

    hdr_cells = table.rows[0].cells
    for i, header_text in enumerate(headers):
        hdr_cells[i].text = header_text
        set_cell_background(hdr_cells[i], COLOR_HEADER_BG_HEX)
        set_cell_margins(hdr_cells[i], top=120, bottom=120, left=140, right=140)
        p = hdr_cells[i].paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        for r in p.runs:
            r.font.name = "Bookman Old Style"
            r.font.size = Pt(10.5)
            r.font.bold = True
            r.font.color.rgb = RGBColor(255, 255, 255)

    for r_idx, row_data in enumerate(data):
        row_cells = table.rows[r_idx + 1].cells
        bg_col = "FFFFFF" if r_idx % 2 == 0 else "F8FAFC"
        for c_idx, cell_value in enumerate(row_data):
            row_cells[c_idx].text = str(cell_value)
            set_cell_background(row_cells[c_idx], bg_col)
            set_cell_margins(row_cells[c_idx], top=80, bottom=80, left=120, right=120)
            p = row_cells[c_idx].paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.LEFT if c_idx != 0 else WD_ALIGN_PARAGRAPH.CENTER
            for r in p.runs:
                r.font.name = "Bookman Old Style"
                r.font.size = Pt(10)
                r.font.color.rgb = RGBColor(15, 23, 42)

    if col_widths:
        for row in table.rows:
            for idx, width in enumerate(col_widths):
                row.cells[idx].width = Inches(width)

    p_sp = doc.add_paragraph()
    p_sp.paragraph_format.space_before = Pt(0)
    p_sp.paragraph_format.space_after = Pt(10)

# ═══════════════════════════════════════════════════════════════════════════════
# PRELIMINARY PAGES BUILDER
# ═══════════════════════════════════════════════════════════════════════════════

def build_preliminary_pages(doc):
    # ── COVER / TITLE PAGE ─────────────────────────────────────────────────────
    add_styled_paragraph(doc, "PROJECT REPORT", font_size=16, bold=True, align=WD_ALIGN_PARAGRAPH.CENTER, space_before=24, space_after=12)
    
    add_styled_paragraph(doc, "AirSense: Real-Time Urban Air Quality Forecasting and Grounded GenAI Health Advisory System", 
                         font_size=22, bold=True, align=WD_ALIGN_PARAGRAPH.CENTER, space_before=12, space_after=24, color_rgb=RGBColor(30, 41, 59))
    
    add_styled_paragraph(doc, "By", font_size=12, italic=True, align=WD_ALIGN_PARAGRAPH.CENTER, space_before=6, space_after=6)
    
    # Students Table
    t_students = doc.add_table(rows=3, cols=2)
    t_students.alignment = WD_TABLE_ALIGNMENT.CENTER
    students_info = [
        ("Parmar Kamal", "Enrolment No: 202527600007"),
        ("Pandya Krushna", "Enrolment No: 202527600006"),
        ("Jadeja Meetrajsinh", "Enrolment No: 202527600001"),
    ]
    for idx, (name, enr) in enumerate(students_info):
        r_cells = t_students.rows[idx].cells
        r_cells[0].text = name
        r_cells[1].text = enr
        for c in r_cells:
            p = c.paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p.runs[0].font.name = "Bookman Old Style"
            p.runs[0].font.size = Pt(12)
            p.runs[0].font.bold = True
            set_cell_margins(c, top=40, bottom=40, left=80, right=80)
    
    add_styled_paragraph(doc, "\nUnder the Supervision of", font_size=12, italic=True, align=WD_ALIGN_PARAGRAPH.CENTER, space_before=18, space_after=4)
    add_styled_paragraph(doc, "Ms. Swati Solanki", font_size=14, bold=True, align=WD_ALIGN_PARAGRAPH.CENTER, space_before=0, space_after=24)
    
    add_styled_paragraph(doc, "A Report Submitted to\nGujarat University\nIn Partial Fulfilment of the Requirements for the Degree of", 
                         font_size=12, align=WD_ALIGN_PARAGRAPH.CENTER, space_before=12, space_after=6)
    
    add_styled_paragraph(doc, "M.Sc. IT Business Intelligence & Analytics (2 Years)\nSemester 3", 
                         font_size=14, bold=True, align=WD_ALIGN_PARAGRAPH.CENTER, space_before=0, space_after=18, color_rgb=RGBColor(37, 99, 235))
    
    add_styled_paragraph(doc, "November 2026", font_size=12, bold=True, align=WD_ALIGN_PARAGRAPH.CENTER, space_before=6, space_after=24)
    
    add_styled_paragraph(doc, "Centre for Professional Courses\nGujarat University, Navrangpura, Ahmedabad, Gujarat, 380009", 
                         font_size=11, bold=True, align=WD_ALIGN_PARAGRAPH.CENTER, space_before=12, space_after=0)

    # ── CERTIFICATE PAGE ───────────────────────────────────────────────────────
    doc.add_page_break()
    add_styled_paragraph(doc, "Centre for Professional Courses\nGujarat University, Navrangpura, Ahmedabad, Gujarat, 380009", 
                         font_size=12, bold=True, align=WD_ALIGN_PARAGRAPH.CENTER, space_before=10, space_after=24)
    
    add_styled_paragraph(doc, "CERTIFICATE", font_size=18, bold=True, align=WD_ALIGN_PARAGRAPH.CENTER, space_before=12, space_after=20, color_rgb=RGBColor(30, 41, 59))
    
    cert_text = (
        "This is to certify that the capstone research work embodied in this project report entitled "
        "“AirSense: Real-Time Urban Air Quality Forecasting and Grounded GenAI Health Advisory System” "
        "was carried out by Parmar Kamal (Enrolment No: 202527600007), Pandya Krushna (Enrolment No: 202527600006), "
        "and Jadeja Meetrajsinh (Enrolment No: 202527600001) at the Centre for Professional Courses (CPC) "
        "for partial fulfilment of the M.Sc. IT Business Intelligence & Analytics (2 Years) degree to be awarded "
        "by Gujarat University. This research work has been carried out under my supervision and is to the "
        "satisfaction of the department."
    )
    add_styled_paragraph(doc, cert_text, font_size=12, align=WD_ALIGN_PARAGRAPH.JUSTIFY, space_before=12, space_after=36)
    
    add_styled_paragraph(doc, "Date: ____________________\nPlace: Ahmedabad, Gujarat", font_size=12, align=WD_ALIGN_PARAGRAPH.LEFT, space_before=0, space_after=48)
    
    # Signatures Table
    t_sig = doc.add_table(rows=2, cols=3)
    t_sig.alignment = WD_TABLE_ALIGNMENT.CENTER
    sig_data = [
        ("Ms. Swati Solanki\n(Guide)\nCPC, Gujarat University",
         "Ms. Amandeep Kaur\n(Program In-Charge)\nCPC, Gujarat University",
         "Dr. B. S. Agrawal\n(Director (I/C))\nCPC, Gujarat University"),
        ("[ Seal of the Institute ]", "", "")
    ]
    for r_i, r in enumerate(sig_data):
        for c_i, val in enumerate(r):
            cell = t_sig.rows[r_i].cells[c_i]
            cell.text = val
            p = cell.paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            for run in p.runs:
                run.font.name = "Bookman Old Style"
                run.font.size = Pt(11)
                run.font.bold = True

    # ── DECLARATION OF ORIGINALITY ─────────────────────────────────────────────
    doc.add_page_break()
    add_styled_paragraph(doc, "DECLARATION OF ORIGINALITY", font_size=18, bold=True, align=WD_ALIGN_PARAGRAPH.CENTER, space_before=12, space_after=20, color_rgb=RGBColor(30, 41, 59))
    
    decl_p1 = (
        "We hereby certify that we are the sole authors of this Project report entitled "
        "“AirSense: Real-Time Urban Air Quality Forecasting and Grounded GenAI Health Advisory System” "
        "and that neither any part of this Project report nor the whole of the Project report has been "
        "submitted for a degree or diploma to any other University or Institution."
    )
    add_styled_paragraph(doc, decl_p1, font_size=12, align=WD_ALIGN_PARAGRAPH.JUSTIFY, space_before=10, space_after=12)
    
    decl_p2 = (
        "We certify that, to the best of our knowledge, our Project report does not infringe upon anyone’s "
        "copyright nor violate any proprietary rights and that any ideas, techniques, quotations, or any "
        "other material from the work of other people included in our Project report, published or otherwise, "
        "are fully acknowledged in accordance with the standard referencing practices."
    )
    add_styled_paragraph(doc, decl_p2, font_size=12, align=WD_ALIGN_PARAGRAPH.JUSTIFY, space_before=0, space_after=12)
    
    decl_p3 = (
        "We declare that this is a true copy of our Project report, including any final revisions, as approved "
        "by our Project report review committee."
    )
    add_styled_paragraph(doc, decl_p3, font_size=12, align=WD_ALIGN_PARAGRAPH.JUSTIFY, space_before=0, space_after=36)
    
    add_styled_paragraph(doc, "Date: ____________________\nPlace: Ahmedabad, Gujarat", font_size=12, align=WD_ALIGN_PARAGRAPH.LEFT, space_before=0, space_after=36)
    
    t_signs = doc.add_table(rows=3, cols=2)
    t_signs.alignment = WD_TABLE_ALIGNMENT.CENTER
    signs_data = [
        ("Parmar Kamal", "(Enrolment No: 202527600007)"),
        ("Pandya Krushna", "(Enrolment No: 202527600006)"),
        ("Jadeja Meetrajsinh", "(Enrolment No: 202527600001)"),
    ]
    for r_i, (nm, enr) in enumerate(signs_data):
        c0 = t_signs.rows[r_i].cells[0]
        c1 = t_signs.rows[r_i].cells[1]
        c0.text = f"___________________________\n{nm}"
        c1.text = f"\n{enr}"
        c0.paragraphs[0].runs[0].font.name = "Bookman Old Style"
        c0.paragraphs[0].runs[0].font.size = Pt(11)
        c0.paragraphs[0].runs[0].font.bold = True
        c1.paragraphs[0].runs[0].font.name = "Bookman Old Style"
        c1.paragraphs[0].runs[0].font.size = Pt(11)

    # ── PROJECT REPORT APPROVAL PAGE ───────────────────────────────────────────
    doc.add_page_break()
    add_styled_paragraph(doc, "PROJECT REPORT APPROVAL", font_size=18, bold=True, align=WD_ALIGN_PARAGRAPH.CENTER, space_before=12, space_after=20, color_rgb=RGBColor(30, 41, 59))
    
    app_text = (
        "This is to certify that the research work embodied in this Project report entitled "
        "“AirSense: Real-Time Urban Air Quality Forecasting and Grounded GenAI Health Advisory System” "
        "was carried out by Parmar Kamal (Enrolment No: 202527600007), Pandya Krushna (Enrolment No: 202527600006), "
        "and Jadeja Meetrajsinh (Enrolment No: 202527600001) at the Centre for Professional Courses (CPC) "
        "for partial fulfilment of M.Sc. IT Business Intelligence & Analytics (2 Years) to be awarded by "
        "Gujarat University."
    )
    add_styled_paragraph(doc, app_text, font_size=12, align=WD_ALIGN_PARAGRAPH.JUSTIFY, space_before=12, space_after=40)
    
    add_styled_paragraph(doc, "Date: ____________________\nPlace: Ahmedabad, Gujarat", font_size=12, align=WD_ALIGN_PARAGRAPH.LEFT, space_before=0, space_after=48)
    
    add_styled_paragraph(doc, "Examiner(s):", font_size=13, bold=True, align=WD_ALIGN_PARAGRAPH.LEFT, space_before=0, space_after=24)
    add_styled_paragraph(doc, "1. ________________________________________ (Internal Examiner)", font_size=12, space_before=0, space_after=24)
    add_styled_paragraph(doc, "2. ________________________________________ (External Examiner)", font_size=12, space_before=0, space_after=24)

    # ── ACKNOWLEDGMENT PAGE ────────────────────────────────────────────────────
    doc.add_page_break()
    add_styled_paragraph(doc, "ACKNOWLEDGMENT", font_size=18, bold=True, align=WD_ALIGN_PARAGRAPH.CENTER, space_before=12, space_after=20, color_rgb=RGBColor(30, 41, 59))
    
    ack_text = (
        "We are sincerely thankful to our guide, Prof. Swati Solanki, for her constant support, stimulating suggestions, "
        "and encouragement, which greatly assisted us in completing our capstone project work. Her close supervision "
        "over the past few months and helpful insights have been invaluable. Despite her busy schedule, her valuable "
        "advice and unwavering support have been an inspiration and a driving force for us. Her experience and deep "
        "technical knowledge have continuously helped shape our initial ideas into a comprehensive, production-grade form.\n\n"
        "We hereby take this opportunity to convey our gratitude for the generous assistance and cooperation that we received "
        "from Prof. Amandeep Kaur, Program In-Charge, and to all those who helped us directly and indirectly.\n\n"
        "We are deeply indebted and thankful to our Department Faculty at the Centre for Professional Courses (CPC) "
        "who helped and rendered their valuable time, knowledge, and information, and whose suggestions and guidance have "
        "enlightened us on the subject of big data streaming architectures, advanced machine learning, and business intelligence.\n\n"
        "We also extend our sincere thanks to Dr. B. S. Agrawal, Director (I/C), CPC-GU, for extending all administrative help, "
        "computational infrastructure, and cooperation during our study period.\n\n"
        "Finally, we are deeply indebted to our parents, family members, and friends, without whose constant patience, "
        "moral support, and blessings, we would have struggled to manage everything on our own."
    )
    add_styled_paragraph(doc, ack_text, font_size=12, align=WD_ALIGN_PARAGRAPH.JUSTIFY, space_before=10, space_after=30)
    
    add_styled_paragraph(doc, "Parmar Kamal (202527600007)\nPandya Krushna (202527600006)\nJadeja Meetrajsinh (202527600001)", 
                         font_size=12, bold=True, align=WD_ALIGN_PARAGRAPH.RIGHT, space_before=12, space_after=0)

    # ── ABSTRACT PAGE ──────────────────────────────────────────────────────────
    doc.add_page_break()
    add_styled_paragraph(doc, "ABSTRACT", font_size=18, bold=True, align=WD_ALIGN_PARAGRAPH.CENTER, space_before=12, space_after=20, color_rgb=RGBColor(30, 41, 59))
    
    abstract_text = (
        "Urban air pollution constitutes one of the most critical public health emergencies across developing economies, "
        "accounting for over seven million premature deaths annually worldwide. In India, urban centers such as Delhi, "
        "Ahmedabad, and Mumbai regularly experience hazardous atmospheric particulate matter concentrations that exceed "
        "both national and global safety thresholds. Despite widespread availability of ground-level sensor data, existing "
        "environmental platforms suffer from fundamental architectural bottlenecks: they rely on static batch processing, "
        "present retrospective metrics rather than actionable forward-looking forecasts, and lack personalized health advisory "
        "capabilities grounded in established medical literature.\n\n"
        "This project presents AirSense, an end-to-end, edge-deployable environmental intelligence platform engineered to "
        "bridge the divide between raw sensor telemetry and personalized health preservation. Architected across five decoupled "
        "layers, AirSense ingests real-time hourly telemetry for major Indian urban hubs via Apache Kafka message brokers, "
        "validates data integrity using strict Pydantic v2 schemas, and persists validated time-series events into TimescaleDB "
        "hypertables. For predictive modeling, a LightGBM gradient boosting regressor is trained via walk-forward cross-validation "
        "with recursive multi-step forecasting, achieving a Root Mean Squared Error (RMSE) of 7.61 AQI units and an R² of 0.961 "
        "across a 48-hour forward projection horizon. To translate these forecasts into safe public health actions, a local "
        "Retrieval-Augmented Generation (RAG) knowledge engine combines ChromaDB vector search across WHO 2021 and CPCB NAAQS 2009 "
        "standards with edge-quantized Ollama LLMs, providing evidence-based, zero-hallucination medical advisories. "
        "Interactive analytics are surfaced via Streamlit geospatial dashboards and enterprise Power BI reporting models. "
        "The entire platform operates 100% locally on standard consumer hardware at zero recurring cloud cost, ensuring total "
        "data privacy and high operational reliability."
    )
    add_styled_paragraph(doc, abstract_text, font_size=12, align=WD_ALIGN_PARAGRAPH.JUSTIFY, space_before=10, space_after=18)
    
    add_styled_paragraph(doc, "Keywords: Real-Time Data Engineering, Apache Kafka, TimescaleDB Hypertables, Air Quality Index (AQI), LightGBM Forecasting, Walk-Forward Validation, Retrieval-Augmented Generation (RAG), ChromaDB, Edge Generative AI, Ollama LLM, Power BI Analytics.", 
                         font_size=11, bold=True, align=WD_ALIGN_PARAGRAPH.JUSTIFY, space_before=6, space_after=0)

    # ── LIST OF FIGURES ────────────────────────────────────────────────────────
    doc.add_page_break()
    add_styled_paragraph(doc, "LIST OF FIGURES", font_size=18, bold=True, align=WD_ALIGN_PARAGRAPH.CENTER, space_before=12, space_after=20, color_rgb=RGBColor(30, 41, 59))
    
    figures_list = [
        ("Fig 1.1", "End-to-End Decoupled 5-Layer Edge Architecture of AirSense", "4"),
        ("Fig 2.1", "Apache Kafka Distributed Pub-Sub Message Broker Pipeline", "9"),
        ("Fig 2.2", "TimescaleDB Hypertable Temporal Partitioning & Chunk Management", "12"),
        ("Fig 2.3", "Recursive Autoregressive Multi-Step 48-Hour Forecasting Scheme", "15"),
        ("Fig 2.4", "Retrieval-Augmented Generation (RAG) Semantic Verification Framework", "18"),
        ("Fig 4.1", "AirSense 12-Week Agile Implementation Lifecycle & Milestones", "28"),
        ("Fig 6.1", "AirSense Real-Time Telemetry Dashboard & CPCB Dynamic Gauge UI", "38"),
        ("Fig 6.2", "Interactive Folium Geospatial Air Quality Bubble Map of India", "40"),
        ("Fig 6.3", "Diurnal Pattern Analysis Across Indian Metros Showing Rush-Hour Inversion", "42"),
        ("Fig 6.4", "PM2.5 to PM10 Combustion Source Diagnostic Ratios Across Monitored Hubs", "44"),
        ("Fig 7.1", "LightGBM Walk-Forward Validation Curve & MLflow Run Diagnostics", "48"),
        ("Fig 7.2", "48-Hour Forward Trajectory Projection with Confidence Interval Bands", "50"),
        ("Fig 7.3", "ChromaDB Semantic Vector Retrieval & Cosine Similarity Distribution", "53"),
        ("Fig 7.4", "AirSense AI Health Advisor Interface with Grounded WHO/CPCB Citations", "55"),
        ("Fig 7.5", "Power BI Executive Dashboard & Star-Schema Data Model", "58"),
        ("Fig 7.6", "Automated Telegram Emergency Spike Notification & Retrain Architecture", "61"),
    ]
    t_figs = doc.add_table(rows=len(figures_list) + 1, cols=3)
    t_figs.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(t_figs)
    t_figs.rows[0].cells[0].text = "Figure No."
    t_figs.rows[0].cells[1].text = "Figure Caption / Description"
    t_figs.rows[0].cells[2].text = "Page No."
    for c in t_figs.rows[0].cells:
        set_cell_background(c, COLOR_HEADER_BG_HEX)
        c.paragraphs[0].runs[0].font.name = "Bookman Old Style"
        c.paragraphs[0].runs[0].font.size = Pt(11)
        c.paragraphs[0].runs[0].font.bold = True
        c.paragraphs[0].runs[0].font.color.rgb = RGBColor(255, 255, 255)
    
    for idx, (f_num, f_cap, f_pg) in enumerate(figures_list):
        row = t_figs.rows[idx + 1]
        row.cells[0].text = f_num
        row.cells[1].text = f_cap
        row.cells[2].text = f_pg
        for c_i, cell in enumerate(row.cells):
            p = cell.paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER if c_i != 1 else WD_ALIGN_PARAGRAPH.LEFT
            for run in p.runs:
                run.font.name = "Bookman Old Style"
                run.font.size = Pt(10)
    
    # ── LIST OF TABLES ─────────────────────────────────────────────────────────
    doc.add_page_break()
    add_styled_paragraph(doc, "LIST OF TABLES", font_size=18, bold=True, align=WD_ALIGN_PARAGRAPH.CENTER, space_before=12, space_after=20, color_rgb=RGBColor(30, 41, 59))
    
    tables_list = [
        ("Table 1.1", "Physical Host System Hardware & Resource Allocation Specifications", "5"),
        ("Table 2.1", "Central Pollution Control Board (CPCB) NAAQS 6-Tier AQI Breakpoints", "8"),
        ("Table 3.1", "Comparative Feature Matrix: Traditional Environmental Systems vs. AirSense", "24"),
        ("Table 4.1", "AirSense Network Architecture, Service Endpoints, and Port Allocation", "29"),
        ("Table 5.1", "Software Technology Stack, Core Libraries, and Version Manifest", "34"),
        ("Table 6.1", "Target Monitored Urban Hubs and Ground-Level Sensor Coordinates", "36"),
        ("Table 6.2", "Engineered Feature Dictionary and Mathematical Transformations", "39"),
        ("Table 7.1", "Comparative Evaluation Benchmark Across Forecasting Models", "49"),
        ("Table 7.2", "LightGBM Walk-Forward Hyperparameter Optimization Search Space", "51"),
        ("Table 7.3", "Regulatory Document Chunking Distribution in ChromaDB Vector Collection", "52"),
        ("Table 7.4", "Automated Repository Test Suite Coverage Matrix (32/32 Passed)", "56"),
        ("Table 7.5", "Power BI Analytical Data Model Key Measures and DAX Formulations", "59"),
    ]
    t_tbls = doc.add_table(rows=len(tables_list) + 1, cols=3)
    t_tbls.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(t_tbls)
    t_tbls.rows[0].cells[0].text = "Table No."
    t_tbls.rows[0].cells[1].text = "Table Title / Description"
    t_tbls.rows[0].cells[2].text = "Page No."
    for c in t_tbls.rows[0].cells:
        set_cell_background(c, COLOR_HEADER_BG_HEX)
        c.paragraphs[0].runs[0].font.name = "Bookman Old Style"
        c.paragraphs[0].runs[0].font.size = Pt(11)
        c.paragraphs[0].runs[0].font.bold = True
        c.paragraphs[0].runs[0].font.color.rgb = RGBColor(255, 255, 255)
    
    for idx, (t_num, t_cap, t_pg) in enumerate(tables_list):
        row = t_tbls.rows[idx + 1]
        row.cells[0].text = t_num
        row.cells[1].text = t_cap
        row.cells[2].text = t_pg
        for c_i, cell in enumerate(row.cells):
            p = cell.paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER if c_i != 1 else WD_ALIGN_PARAGRAPH.LEFT
            for run in p.runs:
                run.font.name = "Bookman Old Style"
                run.font.size = Pt(10)

    # ── TABLE OF CONTENTS ──────────────────────────────────────────────────────
    doc.add_page_break()
    add_styled_paragraph(doc, "TABLE OF CONTENTS", font_size=18, bold=True, align=WD_ALIGN_PARAGRAPH.CENTER, space_before=12, space_after=20, color_rgb=RGBColor(30, 41, 59))
    
    toc_items = [
        ("Title Page", "i"),
        ("Certificate of the Institute", "ii"),
        ("Declaration of Originality", "iii"),
        ("Project Report Approval", "iv"),
        ("Acknowledgment", "v"),
        ("Abstract", "vi"),
        ("List of Figures", "vii"),
        ("List of Tables", "viii"),
        ("Chapter 1: Introduction", "1"),
        ("    1.1 Introduction", "1"),
        ("    1.2 Motivation", "2"),
        ("    1.3 Objectives", "3"),
        ("    1.4 Organization of the Report", "4"),
        ("Chapter 2: Background Theory", "6"),
        ("    2.1 Air Quality Standards & Health Impacts", "6"),
        ("    2.2 Distributed Event Streaming with Apache Kafka", "8"),
        ("    2.3 Time-Series Storage Engine (TimescaleDB / PostgreSQL)", "11"),
        ("    2.4 Gradient Boosting for Tabular Time-Series (LightGBM)", "13"),
        ("    2.5 Retrieval-Augmented Generation & Edge GenAI (ChromaDB & Ollama)", "16"),
        ("Chapter 3: Literature Survey & Comparative Study", "20"),
        ("    3.1 Literature Survey", "20"),
        ("    3.2 Comparative Study", "24"),
        ("Chapter 4: Proposed Work", "26"),
        ("    4.1 Problem Statement and Research Gap", "26"),
        ("    4.2 Proposed Approach (Decoupled 5-Layer Edge Architecture)", "27"),
        ("    4.3 Expected Outcome and SLA Targets", "30"),
        ("    4.4 12-Week Agile Project Workplan", "31"),
        ("Chapter 5: Implementation Environment", "33"),
        ("    5.1 System Specifications", "33"),
        ("    5.2 Programming & Runtime Environment", "34"),
        ("    5.3 Development, Experimentation & Testing Tools", "35"),
        ("Chapter 6: Dataset And Visualization", "36"),
        ("    6.1 Dataset Gathering", "36"),
        ("    6.2 Data Preprocessing & Validation", "38"),
        ("    6.3 Exploratory Data Analysis & Visualizations", "41"),
        ("Chapter 7: Implementation And Evaluation", "46"),
        ("    7.1 Training the Forecasting Model", "46"),
        ("    7.2 Testing & Validation Strategy", "47"),
        ("    7.3 Evaluation of Model", "48"),
        ("        7.3.1 Result Gathering", "48"),
        ("        7.3.2 Result Analysis", "49"),
        ("        7.3.3 Comparison with ML Techniques", "50"),
        ("        7.3.4 Different Tuning Parameters", "51"),
        ("    7.4 Deployment of the Model", "52"),
        ("        7.4.1 Production Model Artifact & 48h Forecaster", "52"),
        ("        7.4.2 RAG Knowledge Base & Ollama Integration", "53"),
        ("        7.4.3 Result Application (Streamlit 5-View Platform)", "54"),
        ("        7.4.4 Power BI Executive Analytics Dashboard", "57"),
        ("        7.4.5 Automated Telegram Spike Alerting & MLOps Loop", "60"),
        ("Chapter 8: Conclusion & Future Scope", "63"),
        ("    8.1 Conclusion", "63"),
        ("    8.2 Future Scope", "64"),
        ("References", "66"),
    ]
    t_toc = doc.add_table(rows=len(toc_items) + 1, cols=2)
    t_toc.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(t_toc)
    t_toc.rows[0].cells[0].text = "Chapter / Section Content"
    t_toc.rows[0].cells[1].text = "Page No."
    for c in t_toc.rows[0].cells:
        set_cell_background(c, COLOR_HEADER_BG_HEX)
        c.paragraphs[0].runs[0].font.name = "Bookman Old Style"
        c.paragraphs[0].runs[0].font.size = Pt(11)
        c.paragraphs[0].runs[0].font.bold = True
        c.paragraphs[0].runs[0].font.color.rgb = RGBColor(255, 255, 255)
    
    for idx, (sec_title, sec_pg) in enumerate(toc_items):
        row = t_toc.rows[idx + 1]
        row.cells[0].text = sec_title
        row.cells[1].text = sec_pg
        for c_i, cell in enumerate(row.cells):
            p = cell.paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.LEFT if c_i == 0 else WD_ALIGN_PARAGRAPH.RIGHT
            for run in p.runs:
                run.font.name = "Bookman Old Style"
                run.font.size = Pt(10)
                if not sec_title.startswith("    "):
                    run.font.bold = True

from report_chapters_part1 import build_chapter_1, build_chapter_2, build_chapter_3
from report_chapters_part2 import build_chapter_4, build_chapter_5, build_chapter_6
from report_chapters_part3 import build_chapter_7, build_chapter_8, build_references

HELPERS = {
    'add_chapter_title': add_chapter_title,
    'add_heading_1': add_heading_1,
    'add_heading_2': add_heading_2,
    'add_heading_3': add_heading_3,
    'add_styled_paragraph': add_styled_paragraph,
    'add_bullet_point': add_bullet_point,
    'add_callout_box': add_callout_box,
    'add_figure_placeholder': add_figure_placeholder,
    'add_academic_table': add_academic_table,
}

def main():
    print("==================================================")
    print("AirSense Master Capstone Report Generator")
    print(f"Target: {OUTPUT_DOCX}")
    print("==================================================")
    
    doc = docx.Document()
    
    # Configure A4 Paper Size & Exact Margins (Left 1.25\", Top/Right/Bottom 1.0\")
    for section in doc.sections:
        section.page_width = Inches(8.27)
        section.page_height = Inches(11.69)
        section.left_margin = Inches(1.25)
        section.right_margin = Inches(1.0)
        section.top_margin = Inches(1.0)
        section.bottom_margin = Inches(1.0)
        
    print("[1/5] Building Preliminary Pages (Cover, Certificate, Declaration, Approval, Acknowledgment, Abstract, TOC)...")
    build_preliminary_pages(doc)
    
    print("[2/5] Building Chapter 1 (Introduction), Chapter 2 (Background Theory), Chapter 3 (Literature Survey)...")
    build_chapter_1(doc, HELPERS)
    build_chapter_2(doc, HELPERS)
    build_chapter_3(doc, HELPERS)
    
    print("[3/5] Building Chapter 4 (Proposed Work), Chapter 5 (Implementation Environment), Chapter 6 (Dataset & Visuals)...")
    build_chapter_4(doc, HELPERS)
    build_chapter_5(doc, HELPERS)
    build_chapter_6(doc, HELPERS)
    
    print("[4/5] Building Chapter 7 (Implementation & Evaluation), Chapter 8 (Conclusion), References...")
    build_chapter_7(doc, HELPERS)
    build_chapter_8(doc, HELPERS)
    build_references(doc, HELPERS)
    
    print(f"[5/5] Compiling and saving final document to {OUTPUT_DOCX}...")
    doc.save(str(OUTPUT_DOCX))
    
    size_mb = OUTPUT_DOCX.stat().st_size / (1024 * 1024)
    print(f"[SUCCESS] Report successfully generated! File size: {size_mb:.2f} MB ({OUTPUT_DOCX.stat().st_size:,} bytes)")

if __name__ == "__main__":
    main()

