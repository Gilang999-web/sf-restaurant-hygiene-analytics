"""
Script untuk menghasilkan file Presentasi PowerPoint Eksekutif (.pptx)
secara otomatis dengan rasio 16:9 widescreen, desain modern kelas konsultan,
kartu metrik KPI, bullet points berbobot, dan grafik visual hasil EDA tersemat.
"""

import os
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.enum.shapes import MSO_SHAPE

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(CURRENT_DIR)
FIGURES_DIR = os.path.join(BASE_DIR, "reports", "figures")
OUTPUT_PPTX = os.path.join(BASE_DIR, "reports", "SF_Restaurant_Hygiene_Executive_Presentation.pptx")

# Palette Warna Modern Eksekutif
NAVY_DARK = RGBColor(15, 23, 42)      # #0F172A
BLUE_PRIMARY = RGBColor(37, 99, 235)  # #2563EB
BLUE_LIGHT = RGBColor(239, 246, 255)  # #EFF6FF
SLATE_GRAY = RGBColor(100, 116, 139)  # #64748B
BG_LIGHT = RGBColor(248, 250, 252)    # #F8FAFC
WHITE = RGBColor(255, 255, 255)
CORAL_ALERT = RGBColor(225, 29, 72)   # #E11D48
EMERALD = RGBColor(16, 185, 129)      # #10B981
CARD_BORDER = RGBColor(226, 232, 240) # #E2E8F0


def create_presentation():
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5) # 16:9 HD standard
    blank_layout = prs.slide_layouts[6]

    # Helper: Set background color
    def set_slide_bg(slide, color):
        background = slide.background
        fill = background.fill
        fill.solid()
        fill.fore_color.rgb = color

    # Helper: Add modern header
    def add_header(slide, title_text, category_text="SAN FRANCISCO RESTAURANT INSPECTIONS ANALYTICS"):
        # Category / Eyebrow
        tx_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.4), Inches(11.7), Inches(0.4))
        tf = tx_box.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        p.text = category_text.upper()
        p.font.size = Pt(10)
        p.font.bold = True
        p.font.color.rgb = BLUE_PRIMARY

        # Main Title
        tx_box2 = slide.shapes.add_textbox(Inches(0.8), Inches(0.7), Inches(11.7), Inches(0.6))
        tf2 = tx_box2.text_frame
        tf2.word_wrap = True
        p2 = tf2.paragraphs[0]
        p2.text = title_text
        p2.font.size = Pt(22)
        p2.font.bold = True
        p2.font.color.rgb = NAVY_DARK

        # Thin divider line
        line = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.8), Inches(1.35), Inches(11.73), Inches(0.02))
        line.fill.solid()
        line.fill.fore_color.rgb = CARD_BORDER
        line.line.color.rgb = CARD_BORDER

    # Helper: Add Card Box
    def add_card(slide, left, top, width, height, title, value, subtext="", border_accent=BLUE_PRIMARY):
        card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
        card.fill.solid()
        card.fill.fore_color.rgb = WHITE
        card.line.color.rgb = CARD_BORDER
        card.line.width = Pt(1)

        # Top color accent
        accent = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, Inches(0.08))
        accent.fill.solid()
        accent.fill.fore_color.rgb = border_accent
        accent.line.fill.background()

        # Text Frame
        tb = slide.shapes.add_textbox(left + Inches(0.2), top + Inches(0.15), width - Inches(0.4), height - Inches(0.3))
        tf = tb.text_frame
        tf.word_wrap = True
        
        p_title = tf.paragraphs[0]
        p_title.text = title.upper()
        p_title.font.size = Pt(9)
        p_title.font.bold = True
        p_title.font.color.rgb = SLATE_GRAY

        p_val = tf.add_paragraph()
        p_val.text = str(value)
        p_val.font.size = Pt(22)
        p_val.font.bold = True
        p_val.font.color.rgb = border_accent

        if subtext:
            p_sub = tf.add_paragraph()
            p_sub.text = subtext
            p_sub.font.size = Pt(8.5)
            p_sub.font.color.rgb = SLATE_GRAY

    # =========================================================================
    # SLIDE 1: COVER SLIDE
    # =========================================================================
    slide1 = prs.slides.add_slide(blank_layout)
    set_slide_bg(slide1, NAVY_DARK)

    # Accent decorative block
    dec = slide1.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.8), Inches(1.5), Inches(0.15), Inches(4.5))
    dec.fill.solid()
    dec.fill.fore_color.rgb = BLUE_PRIMARY
    dec.line.fill.background()

    tb1 = slide1.shapes.add_textbox(Inches(1.2), Inches(1.5), Inches(11.0), Inches(4.5))
    tf1 = tb1.text_frame
    tf1.word_wrap = True

    p = tf1.paragraphs[0]
    p.text = "DATA ANALYST PORTFOLIO PROJECT"
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = RGBColor(96, 165, 250)

    p2 = tf1.add_paragraph()
    p2.text = "San Francisco Restaurant Hygiene & Safety Analytics"
    p2.font.size = Pt(36)
    p2.font.bold = True
    p2.font.color.rgb = WHITE

    p3 = tf1.add_paragraph()
    p3.text = "Data-Driven Public Health Surveillance & Risk Mitigation Strategy (2014 - 2016)"
    p3.font.size = Pt(16)
    p3.font.color.rgb = RGBColor(203, 213, 225)

    p4 = tf1.add_paragraph()
    p4.text = "\n\nAuthor: Gilang Anugrah  |  Tools: Python, SQL, DAX, Power BI  |  Client: SF Department of Public Health (SFDPH)"
    p4.font.size = Pt(11)
    p4.font.color.rgb = RGBColor(148, 163, 184)

    # =========================================================================
    # SLIDE 2: EXECUTIVE SUMMARY & METRIC OVERVIEW
    # =========================================================================
    slide2 = prs.slides.add_slide(blank_layout)
    set_slide_bg(slide2, BG_LIGHT)
    add_header(slide2, "Executive Summary: Transforming Inspection Data into Action", "Context & Business Overview")

    # 4 KPI Cards
    add_card(slide2, Inches(0.8), Inches(1.6), Inches(2.7), Inches(1.3), "Total Inspections", "25,834", "Across 6,078 unique restaurants", BLUE_PRIMARY)
    add_card(slide2, Inches(3.8), Inches(1.6), Inches(2.7), Inches(1.3), "Avg Hygiene Score", "91.3 / 100", "Citywide standard: Good / Excellent", EMERALD)
    add_card(slide2, Inches(6.8), Inches(1.6), Inches(2.7), Inches(1.3), "Total Violations", "40,673", "86% routine maintenance non-compliances", RGBColor(245, 158, 11))
    add_card(slide2, Inches(9.8), Inches(1.6), Inches(2.7), Inches(1.3), "High-Risk Exposure", "13.8%", "Critical public health hazards (Vermin/Temp)", CORAL_ALERT)

    # Left content box: Strategic Context
    box_l = slide2.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(3.2), Inches(5.7), Inches(3.6))
    box_l.fill.solid()
    box_l.fill.fore_color.rgb = WHITE
    box_l.line.color.rgb = CARD_BORDER
    tf_l = box_l.text_frame
    tf_l.word_wrap = True
    p = tf_l.paragraphs[0]
    p.text = "Business Context & Mission"
    p.font.size = Pt(14)
    p.font.bold = True
    p.font.color.rgb = NAVY_DARK

    bullets_l = [
        "Stakeholder: San Francisco Department of Public Health (SFDPH).",
        "The Challenge: SFDPH oversees 6,000+ commercial food establishments with finite inspector headcounts and tight municipal budget constraints.",
        "The Core Problem: Prioritizing routine inspections reactively leads to blind spots in severe contamination prevention.",
        "The Mission: Harness 53,000+ historical records to identify high-risk hotspots, seasonal pest outbreaks, and optimize patrol scheduling."
    ]
    for b in bullets_l:
        p_b = tf_l.add_paragraph()
        p_b.text = "• " + b
        p_b.font.size = Pt(10.5)
        p_b.font.color.rgb = NAVY_DARK

    # Right content box: Key Analytical Discoveries
    box_r = slide2.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(6.8), Inches(3.2), Inches(5.7), Inches(3.6))
    box_r.fill.solid()
    box_r.fill.fore_color.rgb = WHITE
    box_r.line.color.rgb = CARD_BORDER
    tf_r = box_r.text_frame
    tf_r.word_wrap = True
    p_r = tf_r.paragraphs[0]
    p_r.text = "Key Analytical Discoveries"
    p_r.font.size = Pt(14)
    p_r.font.bold = True
    p_r.font.color.rgb = NAVY_DARK

    bullets_r = [
        "Citywide Baseline: 68% of food venues operate at Excellent/Good scores (>=90). Less than 2% fall into severe non-compliance (<70).",
        "Geographic Disparity: Commercial downtown corridors (Financial District 94104/94111) suffer from 20-23% high-risk rates, vs residential suburbs (~10-12%).",
        "Summer Seasonality: Vermin & pest infractions surge by +85% in May-June compared to winter months, establishing a clear timing for preventive intervention.",
        "Enforcement ROI: Mandatory re-inspections for failing venues yielded an average +8.57 score rebound, confirming enforcement efficacy."
    ]
    for b in bullets_r:
        p_b = tf_r.add_paragraph()
        p_b.text = "• " + b
        p_b.font.size = Pt(10.5)
        p_b.font.color.rgb = NAVY_DARK

    # =========================================================================
    # SLIDE 3: END-TO-END ANALYTICS METHODOLOGY & ARCHITECTURE
    # =========================================================================
    slide3 = prs.slides.add_slide(blank_layout)
    set_slide_bg(slide3, BG_LIGHT)
    add_header(slide3, "Analytics Architecture: CRISP-DM Framework & Toolchain", "Methodology & Tech Stack")

    cols = [
        {"title": "1. Data Cleaning (Python)", "desc": "Handled grain duplication, corrected (0,0) GPS anomalies, standard 5-digit zip parsing, removed 50 exact duplicates, exported clean CSVs.", "tech": "Pandas, NumPy, KaggleHub"},
        {"title": "2. Database & SQL EDA", "desc": "Loaded data into SQLite & T-SQL (SSMS). Implemented CTEs, Window Functions (LAG, DENSE_RANK, SUM OVER) for Pareto & seasonality analysis.", "tech": "SQLite, SSMS (T-SQL)"},
        {"title": "3. DAX & BI Modeling", "desc": "Constructed Star-Schema style summary data model, authored dynamic DAX measures (% High Risk Rate, Compliance Tiers), professional custom palette.", "tech": "Power BI Desktop, DAX"},
        {"title": "4. Decision Delivery", "desc": "Translated diagnostic metrics into executive insights, formulated seasonal prevention protocols, and delivered high-impact interactive visuals.", "tech": "Executive Dashboard, PDF/PPTX"}
    ]

    col_w = Inches(2.7)
    gap = Inches(0.3)
    start_l = Inches(0.8)

    for i, c in enumerate(cols):
        cl = start_l + i * (col_w + gap)
        cbox = slide3.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, cl, Inches(1.8), col_w, Inches(5.0))
        cbox.fill.solid()
        cbox.fill.fore_color.rgb = WHITE
        cbox.line.color.rgb = CARD_BORDER

        # Number header
        num_header = slide3.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, cl, Inches(1.8), col_w, Inches(0.6))
        num_header.fill.solid()
        num_header.fill.fore_color.rgb = BLUE_PRIMARY
        num_header.line.fill.background()
        tf_nh = num_header.text_frame
        p_nh = tf_nh.paragraphs[0]
        p_nh.text = c["title"]
        p_nh.font.size = Pt(11)
        p_nh.font.bold = True
        p_nh.font.color.rgb = WHITE
        p_nh.alignment = PP_ALIGN.CENTER

        tf_c = cbox.text_frame
        tf_c.word_wrap = True
        p_dummy = tf_c.paragraphs[0]
        p_dummy.text = "\n\n"

        p_desc = tf_c.add_paragraph()
        p_desc.text = c["desc"]
        p_desc.font.size = Pt(10)
        p_desc.font.color.rgb = NAVY_DARK

        p_tech_lbl = tf_c.add_paragraph()
        p_tech_lbl.text = "\nKey Technologies:"
        p_tech_lbl.font.size = Pt(9.5)
        p_tech_lbl.font.bold = True
        p_tech_lbl.font.color.rgb = BLUE_PRIMARY

        p_tech = tf_c.add_paragraph()
        p_tech.text = c["tech"]
        p_tech.font.size = Pt(9.5)
        p_tech.font.color.rgb = SLATE_GRAY

    # =========================================================================
    # SLIDE 4: INSIGHT 1 - CITYWIDE SCORE BENCHMARKING
    # =========================================================================
    slide4 = prs.slides.add_slide(blank_layout)
    set_slide_bg(slide4, BG_LIGHT)
    add_header(slide4, "Citywide Compliance: 68% Operate in Good/Excellent Standing", "Finding 1: Score Distribution")

    # Embed Figure 2
    f2_path = os.path.join(FIGURES_DIR, "fig2_score_categories.png")
    if os.path.exists(f2_path):
        slide4.shapes.add_picture(f2_path, Inches(0.8), Inches(1.6), width=Inches(6.2))

    # Narrative Box Right
    r_box = slide4.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(7.3), Inches(1.6), Inches(5.2), Inches(5.2))
    r_box.fill.solid()
    r_box.fill.fore_color.rgb = WHITE
    r_box.line.color.rgb = CARD_BORDER
    tf_r = r_box.text_frame
    tf_r.word_wrap = True

    p = tf_r.paragraphs[0]
    p.text = "Key Takeaways & The Double-Counting Trap"
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = NAVY_DARK

    bullets = [
        "Robust Baseline: The median and mean inspection score across SF sits comfortably at 91.3 / 100.",
        "Concentrated Risk: Severe hygiene degradation is not systemic across the city—only 1.86% (275 sessions) scored in the critical 'Poor (<70)' bracket.",
        "The Double-Counting Pitfall: In raw data, each row represents 1 violation. Restorans with multiple violations appeared up to 8 times, artificially depressing raw averages to 86.2.",
        "Session-Level Aggregation: Aggregating to 1 row per inspection session recovered true operational reality (91.3), preventing false regulatory alarms."
    ]
    for b in bullets:
        p_b = tf_r.add_paragraph()
        p_b.text = "• " + b
        p_b.font.size = Pt(10)
        p_b.font.color.rgb = NAVY_DARK

    # =========================================================================
    # SLIDE 5: INSIGHT 2 - PARETO OF SANITATION VIOLATIONS
    # =========================================================================
    slide5 = prs.slides.add_slide(blank_layout)
    set_slide_bg(slide5, BG_LIGHT)
    add_header(slide5, "Pareto Principle: Top 10 Infractions Account for 58% of Total", "Finding 2: Violation Analysis")

    # Embed Figure 3
    f3_path = os.path.join(FIGURES_DIR, "fig3_top10_violations.png")
    if os.path.exists(f3_path):
        slide5.shapes.add_picture(f3_path, Inches(0.8), Inches(1.6), width=Inches(6.2))

    # Narrative Box Right
    r_box = slide5.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(7.3), Inches(1.6), Inches(5.2), Inches(5.2))
    r_box.fill.solid()
    r_box.fill.fore_color.rgb = WHITE
    r_box.line.color.rgb = CARD_BORDER
    tf_r = r_box.text_frame
    tf_r.word_wrap = True

    p = tf_r.paragraphs[0]
    p.text = "Operational Hygiene vs Critical Hazards"
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = NAVY_DARK

    bullets = [
        "Physical Facility Issues Dominate: #1 most frequent violation is 'Unclean floors, walls, ceilings' (3,545 incidents), followed by handwashing sink accessibility.",
        "86% Low/Moderate Risk: The overwhelming majority of recorded non-compliances are structural and sanitary maintenance issues, not active biological pathogens.",
        "Critical High-Risk Exception: 'High-risk food holding temperature' ranks #10 overall with 1,629 occurrences. This is the single largest biological food-poisoning hazard.",
        "Action Strategy: SFDPH checklist should decouple minor structural citations from urgent bacterial incubation risks."
    ]
    for b in bullets:
        p_b = tf_r.add_paragraph()
        p_b.text = "• " + b
        p_b.font.size = Pt(10)
        p_b.font.color.rgb = NAVY_DARK

    # =========================================================================
    # SLIDE 6: INSIGHT 3 - GEOSPATIAL RISK HOTSPOTS
    # =========================================================================
    slide6 = prs.slides.add_slide(blank_layout)
    set_slide_bg(slide6, BG_LIGHT)
    add_header(slide6, "Geospatial Exposure: High-Density Dining Hubs Carry Elevated Risk", "Finding 3: Geographic Profiling")

    # Embed Figure 6
    f6_path = os.path.join(FIGURES_DIR, "fig6_high_risk_postal_codes.png")
    if os.path.exists(f6_path):
        slide6.shapes.add_picture(f6_path, Inches(0.8), Inches(1.6), width=Inches(6.2))

    # Narrative Box Right
    r_box = slide6.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(7.3), Inches(1.6), Inches(5.2), Inches(5.2))
    r_box.fill.solid()
    r_box.fill.fore_color.rgb = WHITE
    r_box.line.color.rgb = CARD_BORDER
    tf_r = r_box.text_frame
    tf_r.word_wrap = True

    p = tf_r.paragraphs[0]
    p.text = "Statistical Thresholding & Risk Zones"
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = NAVY_DARK

    bullets = [
        "Small-Sample Distortion Avoided: Postal codes with <100 inspections (e.g. 94014, 94120) showed deceptive 50% rates due to sample sizes of 5-8 restaurants.",
        "Core Business District Vulnerability: Downtown corridors—94104 (Financial South, 22.9%) and 94122 (Sunset North, 20.5%)—exhibit statistically significant higher high-risk proportions.",
        "Why High-Density Corridors Suffer: Fast kitchen turnover, older infrastructure, and high dining traffic stress cold-storage equipment and pest barriers.",
        "Resource Reallocation: Moving 20% of inspector hours from low-risk suburbs to 94104, 94122, and 94133 maximizes public health impact."
    ]
    for b in bullets:
        p_b = tf_r.add_paragraph()
        p_b.text = "• " + b
        p_b.font.size = Pt(10)
        p_b.font.color.rgb = NAVY_DARK

    # =========================================================================
    # SLIDE 7: INSIGHT 4 - SEASONALITY & SUMMER PEST SPIKE
    # =========================================================================
    slide7 = prs.slides.add_slide(blank_layout)
    set_slide_bg(slide7, BG_LIGHT)
    add_header(slide7, "Early Warning: +85% Surge in Vermin Infestations During Summer", "Finding 4: Temporal Seasonality")

    # Embed Figure 5
    f5_path = os.path.join(FIGURES_DIR, "fig5_vermin_seasonality.png")
    if os.path.exists(f5_path):
        slide7.shapes.add_picture(f5_path, Inches(0.8), Inches(1.6), width=Inches(6.2))

    # Narrative Box Right
    r_box = slide7.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(7.3), Inches(1.6), Inches(5.2), Inches(5.2))
    r_box.fill.solid()
    r_box.fill.fore_color.rgb = WHITE
    r_box.line.color.rgb = CARD_BORDER
    tf_r = r_box.text_frame
    tf_r.word_wrap = True

    p = tf_r.paragraphs[0]
    p.text = "Predictive Public Health Intervention"
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = NAVY_DARK

    bullets = [
        "Clear Seasonal Cyclicality: Rodent and insect infestations exhibit intense weather dependency, peaking in May (332 incidents) and June (353 incidents).",
        "Winter Lows: In contrast, December and January register only 162-190 incidents (a +85% climb from winter to summer).",
        "The Double Hazard: Summer temperature surges simultaneously degrade outdoor waste and stress refrigeration units, compounding pest attraction.",
        "Preventive Campaign Window: Rather than issuing fines in July, SFDPH should mandate pre-summer pest control audit notices across all districts in April."
    ]
    for b in bullets:
        p_b = tf_r.add_paragraph()
        p_b.text = "• " + b
        p_b.font.size = Pt(10)
        p_b.font.color.rgb = NAVY_DARK

    # =========================================================================
    # SLIDE 8: INSIGHT 5 - ENFORCEMENT & REMEDIATION IMPACT
    # =========================================================================
    slide8 = prs.slides.add_slide(blank_layout)
    set_slide_bg(slide8, BG_LIGHT)
    add_header(slide8, "Enforcement Efficacy: Failing Venues Rebound by +8.57 Points", "Finding 5: Remediation Impact")

    # Embed Figure 7
    f7_path = os.path.join(FIGURES_DIR, "fig7_remediation_impact.png")
    if os.path.exists(f7_path):
        slide8.shapes.add_picture(f7_path, Inches(0.8), Inches(1.6), width=Inches(6.2))

    # Narrative Box Right
    r_box = slide8.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(7.3), Inches(1.6), Inches(5.2), Inches(5.2))
    r_box.fill.solid()
    r_box.fill.fore_color.rgb = WHITE
    r_box.line.color.rgb = CARD_BORDER
    tf_r = r_box.text_frame
    tf_r.word_wrap = True

    p = tf_r.paragraphs[0]
    p.text = "Measuring Regulatory Compliance ROI"
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = NAVY_DARK

    bullets = [
        "Follow-Up Analysis: Evaluated 730 restaurants that scored Poor/Substandard (<80) using SQL Window Functions (LAG) on subsequent re-inspections.",
        "Statistically Significant Recovery: Average initial score of 72.92 rose to 81.49 on follow-up—an average recovery of +8.57 points.",
        "76% Success Rate: Over three-quarters of inspected venues successfully exited the danger zone upon mandatory re-inspection.",
        "Policy Takeaway: Routine follow-up inspections are not merely punitive; they serve as a powerful behavioral correction mechanism."
    ]
    for b in bullets:
        p_b = tf_r.add_paragraph()
        p_b.text = "• " + b
        p_b.font.size = Pt(10)
        p_b.font.color.rgb = NAVY_DARK

    # =========================================================================
    # SLIDE 9: EXECUTIVE POWER BI DASHBOARD
    # =========================================================================
    slide9 = prs.slides.add_slide(blank_layout)
    set_slide_bg(slide9, BG_LIGHT)
    add_header(slide9, "Executive Power BI Dashboard: Interactive Surveillance Center", "BI Deliverable Showcase")

    # Embed Dashboard Mockup
    dm_path = os.path.join(FIGURES_DIR, "dashboard_mockup.png")
    if os.path.exists(dm_path):
        slide9.shapes.add_picture(dm_path, Inches(0.8), Inches(1.6), width=Inches(8.2))

    # Right Spec Box
    r_box = slide9.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(9.3), Inches(1.6), Inches(3.2), Inches(5.2))
    r_box.fill.solid()
    r_box.fill.fore_color.rgb = WHITE
    r_box.line.color.rgb = CARD_BORDER
    tf_r = r_box.text_frame
    tf_r.word_wrap = True

    p = tf_r.paragraphs[0]
    p.text = "Dashboard Highlights"
    p.font.size = Pt(12)
    p.font.bold = True
    p.font.color.rgb = NAVY_DARK

    bullets = [
        "16:9 HD Widescreen Executive Layout.",
        "4 Synchronized KPI Cards with dynamic DAX calculations.",
        "Cross-Filtering Enabled: Selecting a district updates violations and monthly trends simultaneously.",
        "Color Hierarchy: Emerald (Safe), Amber (Attention), Crimson (Critical High-Risk).",
        "Executive micro-copy tailored for non-technical leadership."
    ]
    for b in bullets:
        p_b = tf_r.add_paragraph()
        p_b.text = "• " + b
        p_b.font.size = Pt(9.5)
        p_b.font.color.rgb = NAVY_DARK

    # =========================================================================
    # SLIDE 10: STRATEGIC RECOMMENDATIONS & ROADMAP
    # =========================================================================
    slide10 = prs.slides.add_slide(blank_layout)
    set_slide_bg(slide10, BG_LIGHT)
    add_header(slide10, "Strategic Action Plan: 3 High-Impact Recommendations for SFDPH", "Department Next Steps")

    recs = [
        {
            "num": "01",
            "title": "Geographic Resource Reallocation",
            "subtitle": "Shift 20% Inspector Capacity to Downtown Hotspots",
            "detail": "Reallocate inspector patrol shifts from low-density, compliant residential areas into high-risk commercial zones (94104, 94122, 94133). Introduce unannounced peak-hour visits during lunch/dinner rushes where food temperature violations peak.",
            "color": BLUE_PRIMARY
        },
        {
            "num": "02",
            "title": "Pre-Summer Pest Abatement Campaign",
            "subtitle": "Mandatory April Notification & Waste Audits",
            "detail": "Launch a targeted preventive pest abatement campaign every April, one month prior to the historical May-June infestation surge (+85%). Partner with municipal waste management to inspect outdoor dumpster seals and grease traps.",
            "color": CORAL_ALERT
        },
        {
            "num": "03",
            "title": "Standardized 14-Day Re-Inspection Protocol",
            "subtitle": "Institutionalize Rapid Regulatory Follow-Up",
            "detail": "Maintain and formalize the mandatory 14-day re-inspection requirement for any establishment scoring below 80. Data proves that 76% of venues achieve compliance on re-check (+8.57 point gain), preventing repeat contamination.",
            "color": EMERALD
        }
    ]

    card_h = Inches(1.5)
    for i, r in enumerate(recs):
        top_pos = Inches(1.7) + i * Inches(1.75)
        rcard = slide10.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), top_pos, Inches(11.73), card_h)
        rcard.fill.solid()
        rcard.fill.fore_color.rgb = WHITE
        rcard.line.color.rgb = CARD_BORDER

        # Number Badge
        badge = slide10.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.8), top_pos, Inches(1.1), card_h)
        badge.fill.solid()
        badge.fill.fore_color.rgb = r["color"]
        badge.line.fill.background()
        tf_b = badge.text_frame
        p_b = tf_b.paragraphs[0]
        p_b.text = r["num"]
        p_b.font.size = Pt(22)
        p_b.font.bold = True
        p_b.font.color.rgb = WHITE
        p_b.alignment = PP_ALIGN.CENTER

        # Content Text
        t_box = slide10.shapes.add_textbox(Inches(2.1), top_pos + Inches(0.12), Inches(10.2), card_h - Inches(0.24))
        tf_t = t_box.text_frame
        tf_t.word_wrap = True

        p_t = tf_t.paragraphs[0]
        p_t.text = r["title"].upper() + "  —  "
        p_t.font.size = Pt(12)
        p_t.font.bold = True
        p_t.font.color.rgb = r["color"]

        # Append subtitle
        p_sub = tf_t.add_paragraph()
        p_sub.text = r["subtitle"]
        p_sub.font.size = Pt(10)
        p_sub.font.bold = True
        p_sub.font.color.rgb = NAVY_DARK

        p_det = tf_t.add_paragraph()
        p_det.text = r["detail"]
        p_det.font.size = Pt(9.5)
        p_det.font.color.rgb = SLATE_GRAY

    # =========================================================================
    # SLIDE 11: CLOSING & Q&A
    # =========================================================================
    slide11 = prs.slides.add_slide(blank_layout)
    set_slide_bg(slide11, NAVY_DARK)

    tb11 = slide11.shapes.add_textbox(Inches(1.5), Inches(2.0), Inches(10.3), Inches(3.5))
    tf11 = tb11.text_frame
    tf11.word_wrap = True

    p = tf11.paragraphs[0]
    p.text = "Thank You!"
    p.font.size = Pt(40)
    p.font.bold = True
    p.font.color.rgb = WHITE

    p2 = tf11.add_paragraph()
    p2.text = "Questions & Discussion"
    p2.font.size = Pt(20)
    p2.font.color.rgb = RGBColor(96, 165, 250)

    p3 = tf11.add_paragraph()
    p3.text = "\n\nPortfolio Project: San Francisco Restaurant Hygiene & Safety Analytics"
    p3.font.size = Pt(12)
    p3.font.color.rgb = RGBColor(203, 213, 225)

    p4 = tf11.add_paragraph()
    p4.text = "Author: Gilang Anugrah | Data Analyst"
    p4.font.size = Pt(11)
    p4.font.color.rgb = RGBColor(148, 163, 184)

    # Simpan file presentasi
    os.makedirs(os.path.dirname(OUTPUT_PPTX), exist_ok=True)
    prs.save(OUTPUT_PPTX)
    print(f"File presentasi berhasil dibuat di: {OUTPUT_PPTX}")


if __name__ == "__main__":
    create_presentation()

