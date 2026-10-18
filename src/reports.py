"""
Supermarket Sales Intelligence System - Reporting Engine
==========================================================
Generates production-grade, publication-ready executive reports:
1. Executive PDF Briefing (ReportLab Flowable Document)
   - Dynamic page budgeting and NumberedCanvas page numbering (Page X of Y)
   - High-contrast executive KPI summary
   - 4-Tier Business Insights (Observation -> Insight -> Explanation -> Action)
   - Inventory health audit & stock replenishment requirements
   - Anomaly detection & data quality log
   - Sales breakdown by product category

2. Comprehensive Multi-Sheet Excel Workbook (openpyxl)
   - Sheet 1: Executive Summary & KPIs
   - Sheet 2: Sales Transactions (Filtered active dataset)
   - Sheet 3: Product Performance Breakdown
   - Sheet 4: Category Performance Breakdown
   - Sheet 5: Inventory Stock & Velocity Intelligence
   - Sheet 6: Data Quality & Anomaly Audit Log
   - Sheet 7: Structured Business Insights Matrix

Designed for Capstone Demonstrations and Retail Business Intelligence.
"""

import io
import datetime
import pandas as pd
import numpy as np

# ReportLab imports for PDF generation
from reportlab.lib.pagesizes import letter
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    KeepTogether,
    HRFlowable,
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.pdfgen import canvas

# openpyxl imports for Excel generation
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter


# ==============================================================================
# 1. REPORTLAB NUMBERED CANVAS (PAGE X OF Y & EXECUTIVE HEADER/FOOTER)
# ==============================================================================

class NumberedCanvas(canvas.Canvas):
    """
    Two-pass ReportLab Canvas that calculates total page count dynamically
    and paints clean executive headers, footers, and page numbers.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_page_decorations(self, page_count: int):
        self.saveState()
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#64748B"))

        # Running header on subsequent pages (page 2 onwards)
        if self._pageNumber > 1:
            self.setStrokeColor(colors.HexColor("#E2E8F0"))
            self.setLineWidth(0.75)
            self.line(40, 755, 572, 755)
            self.drawString(40, 760, "Supermarket Sales & Retail Intelligence System — Executive Briefing")
            self.drawRightString(572, 760, datetime.datetime.now().strftime("%B %d, %Y"))

        # Running footer on every page
        self.setStrokeColor(colors.HexColor("#CBD5E1"))
        self.setLineWidth(0.75)
        self.line(40, 42, 572, 42)

        footer_left = "Confidential — Retail Business Intelligence & Capstone Evaluation"
        footer_right = f"Page {self._pageNumber} of {page_count}"
        self.drawString(40, 30, footer_left)
        self.drawRightString(572, 30, footer_right)

        self.restoreState()


# ==============================================================================
# 2. PDF REPORT GENERATOR
# ==============================================================================

def generate_pdf_report(
    df: pd.DataFrame,
    dataset_name: str = "Active Sales Dataset",
    filter_summary: dict = None,
    insights: list = None,
    anomalies: list = None,
    inventory_df: pd.DataFrame = None,
) -> io.BytesIO:
    """
    Generate an executive PDF briefing using ReportLab flowable elements.

    Args:
        df: Filtered or active sales transactions DataFrame.
        dataset_name: Name of active data source.
        filter_summary: Dictionary of active sidebar filter selections.
        insights: List of 4-tier insight dictionaries from src.insights.
        anomalies: List of anomaly dictionaries from src.anomaly.
        inventory_df: Inventory intelligence DataFrame from src.inventory.

    Returns:
        io.BytesIO buffer containing the compiled PDF document.
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        leftMargin=40,
        rightMargin=40,
        topMargin=46,
        bottomMargin=46,
    )

    styles = getSampleStyleSheet()

    # Define clean, professional custom styles
    title_style = ParagraphStyle(
        "DocTitle",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=20,
        leading=24,
        textColor=colors.HexColor("#0F172A"),
        spaceAfter=4,
    )

    subtitle_style = ParagraphStyle(
        "DocSubtitle",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=10,
        leading=14,
        textColor=colors.HexColor("#475569"),
        spaceAfter=12,
    )

    section_heading = ParagraphStyle(
        "SectionHeading",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=12,
        leading=16,
        textColor=colors.HexColor("#1E3A8A"),
        spaceBefore=12,
        spaceAfter=6,
        keepWithNext=True,
    )

    meta_label = ParagraphStyle(
        "MetaLabel",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=8,
        leading=11,
        textColor=colors.HexColor("#475569"),
    )

    meta_val = ParagraphStyle(
        "MetaVal",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=8,
        leading=11,
        textColor=colors.HexColor("#0F172A"),
    )

    kpi_title_style = ParagraphStyle(
        "KPITitle",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=7.5,
        leading=10,
        textColor=colors.HexColor("#64748B"),
        alignment=1,  # Center
    )

    kpi_num_style = ParagraphStyle(
        "KPINumber",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=13,
        leading=16,
        textColor=colors.HexColor("#1E3A8A"),
        alignment=1,  # Center
    )

    kpi_sub_style = ParagraphStyle(
        "KPISub",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=7,
        leading=9,
        textColor=colors.HexColor("#94A3B8"),
        alignment=1,  # Center
    )

    cell_style = ParagraphStyle(
        "TableCell",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=7.5,
        leading=10,
        textColor=colors.HexColor("#1E293B"),
    )

    cell_style_bold = ParagraphStyle(
        "TableCellBold",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=7.5,
        leading=10,
        textColor=colors.HexColor("#0F172A"),
    )

    header_cell = ParagraphStyle(
        "TableHeaderCell",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=8,
        leading=11,
        textColor=colors.white,
    )

    tier_label = ParagraphStyle(
        "TierLabel",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=7.5,
        leading=10,
        textColor=colors.HexColor("#1E3A8A"),
    )

    tier_body = ParagraphStyle(
        "TierBody",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=7.5,
        leading=10.5,
        textColor=colors.HexColor("#334155"),
    )

    story = []

    # 1. Document Title & Header Banner
    story.append(Paragraph("Executive Supermarket Sales & Retail Intelligence Report", title_style))
    story.append(
        Paragraph(
            "Holistic operational review: Financial KPIs, 4-tier prescriptive insights, "
            "inventory health audit, and data quality anomaly detection.",
            subtitle_style,
        )
    )

    # 2. Metadata Block
    now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    filters_text = "All Records (Unfiltered)"
    if filter_summary:
        f_parts = []
        for k, v in filter_summary.items():
            if isinstance(v, (list, tuple)):
                v_str = ", ".join(str(item) for item in v) if v else "All"
            else:
                v_str = str(v)
            f_parts.append(f"{k.capitalize()}: {v_str}")
        if f_parts:
            filters_text = " | ".join(f_parts)

    meta_data = [
        [
            Paragraph("<b>Generated:</b>", meta_label),
            Paragraph(now_str, meta_val),
            Paragraph("<b>Dataset Source:</b>", meta_label),
            Paragraph(str(dataset_name), meta_val),
        ],
        [
            Paragraph("<b>Analyzed Records:</b>", meta_label),
            Paragraph(f"{len(df):,} transactions", meta_val),
            Paragraph("<b>Scope / Filters:</b>", meta_label),
            Paragraph(filters_text, meta_val),
        ],
    ]
    meta_table = Table(meta_data, colWidths=[90, 176, 90, 176])
    meta_table.setStyle(
        TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#F8FAFC")),
            ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
            ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
            ("TOPPADDING", (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ("LEFTPADDING", (0, 0), (-1, -1), 6),
            ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ])
    )
    story.append(meta_table)
    story.append(Spacer(1, 10))

    # Compute Core Metrics
    total_sales = float(df["Sales"].sum()) if not df.empty and "Sales" in df.columns else 0.0
    total_qty = int(df["Quantity"].sum()) if not df.empty and "Quantity" in df.columns else 0
    total_txns = len(df)
    avg_order_val = total_sales / total_txns if total_txns > 0 else 0.0
    avg_rating = float(df["Rating"].mean()) if not df.empty and "Rating" in df.columns else 0.0

    # 3. Executive KPI Cards Table
    kpi_cells = [
        [
            [Paragraph("TOTAL REVENUE", kpi_title_style), Paragraph(f"${total_sales:,.2f}", kpi_num_style), Paragraph("Gross turnover", kpi_sub_style)],
            [Paragraph("TOTAL VOLUME", kpi_title_style), Paragraph(f"{total_qty:,}", kpi_num_style), Paragraph("Units sold", kpi_sub_style)],
            [Paragraph("TRANSACTIONS", kpi_title_style), Paragraph(f"{total_txns:,}", kpi_num_style), Paragraph("Invoices analyzed", kpi_sub_style)],
            [Paragraph("AVG ORDER VALUE", kpi_title_style), Paragraph(f"${avg_order_val:,.2f}", kpi_num_style), Paragraph("Per transaction", kpi_sub_style)],
            [Paragraph("AVG RATING", kpi_title_style), Paragraph(f"{avg_rating:.2f} / 5.0", kpi_num_style), Paragraph("Customer satisfaction", kpi_sub_style)],
        ]
    ]
    kpi_table = Table(kpi_cells, colWidths=[106, 106, 106, 107, 107])
    kpi_table.setStyle(
        TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#EFF6FF")),
            ("BOX", (0, 0), (-1, -1), 1, colors.HexColor("#3B82F6")),
            ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#BFDBFE")),
            ("TOPPADDING", (0, 0), (-1, -1), 6),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ])
    )
    story.append(kpi_table)
    story.append(Spacer(1, 10))

    # 4. Section: 4-Tier Strategic Business Insights
    story.append(Paragraph("1. Strategic Business Insights (4-Tier Framework)", section_heading))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#1E3A8A"), spaceAfter=6))

    if insights and len(insights) > 0:
        for idx, item in enumerate(insights[:5], 1):  # Include top 5 structured insights
            cat_badge = item.get("category", "Operational").upper()
            pri_badge = item.get("priority", "Medium").upper()
            title = item.get("title", f"Insight #{idx}")

            card_data = [
                [
                    Paragraph(f"<b>#{idx}. {title}</b> — <font color='#1E40AF'>[{cat_badge}]</font> <font color='#D97706'>[{pri_badge} PRIORITY]</font>", cell_style_bold),
                ],
                [
                    Paragraph(f"<b>Observation:</b> {item.get('observation', 'N/A')}", tier_body),
                ],
                [
                    Paragraph(f"<b>Insight:</b> {item.get('insight', 'N/A')}", tier_body),
                ],
                [
                    Paragraph(f"<b>Possible Explanation:</b> {item.get('explanation', 'N/A')}", tier_body),
                ],
                [
                    Paragraph(f"<b>Recommended Action:</b> <b>{item.get('action', 'N/A')}</b>", tier_body),
                ],
            ]

            card_table = Table(card_data, colWidths=[532])
            card_table.setStyle(
                TableStyle([
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#F1F5F9")),
                    ("BACKGROUND", (0, 1), (-1, -1), colors.white),
                    ("BOX", (0, 0), (-1, -1), 0.75, colors.HexColor("#CBD5E1")),
                    ("LINEBELOW", (0, 0), (-1, 0), 0.5, colors.HexColor("#CBD5E1")),
                    ("TOPPADDING", (0, 0), (-1, -1), 3),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
                    ("LEFTPADDING", (0, 0), (-1, -1), 6),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                ])
            )
            story.append(KeepTogether([card_table, Spacer(1, 6)]))
    else:
        story.append(Paragraph("<i>No strategic insights triggered for the current dataset scope.</i>", tier_body))
        story.append(Spacer(1, 6))

    # 5. Section: Inventory Stock Health & Replenishment
    story.append(Paragraph("2. Inventory Stock Health & Replenishment Audit", section_heading))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#1E3A8A"), spaceAfter=6))

    if inventory_df is not None and not inventory_df.empty:
        # Filter for critical, low stock or items needing reorder first
        priority_inv = inventory_df[inventory_df["reorder_flag"] == 1]
        if priority_inv.empty:
            display_inv = inventory_df.head(8)
        else:
            display_inv = priority_inv.head(8)

        inv_rows = [
            [
                Paragraph("Product", header_cell),
                Paragraph("Category", header_cell),
                Paragraph("Stock", header_cell),
                Paragraph("Velocity", header_cell),
                Paragraph("Days Rem.", header_cell),
                Paragraph("Health", header_cell),
                Paragraph("Reorder Qty", header_cell),
                Paragraph("Reorder Cost", header_cell),
            ]
        ]

        for _, row in display_inv.iterrows():
            health_color = "#DC2626" if row.get("health_status") == "Out of Stock" else ("#D97706" if row.get("health_status") == "Low Stock" else "#059669")
            inv_rows.append([
                Paragraph(str(row.get("product_name", "")), cell_style),
                Paragraph(str(row.get("category_name", "")), cell_style),
                Paragraph(str(int(row.get("current_stock", 0))), cell_style),
                Paragraph(f"{float(row.get('daily_sales_velocity', 0)):.1f}/day", cell_style),
                Paragraph(f"{float(row.get('days_of_stock_remaining', 0)):.1f} d", cell_style),
                Paragraph(f"<font color='{health_color}'><b>{row.get('health_status', 'Healthy')}</b></font>", cell_style),
                Paragraph(str(int(row.get("recommended_reorder_qty", 0))), cell_style),
                Paragraph(f"${float(row.get('estimated_reorder_cost', 0)):,.2f}", cell_style),
            ])

        inv_table = Table(inv_rows, colWidths=[100, 95, 42, 55, 52, 68, 55, 65])
        inv_table.setStyle(
            TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1E3A8A")),
                ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
                ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F8FAFC")]),
                ("TOPPADDING", (0, 0), (-1, -1), 3),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
                ("LEFTPADDING", (0, 0), (-1, -1), 4),
                ("RIGHTPADDING", (0, 0), (-1, -1), 4),
            ])
        )
        story.append(inv_table)
    else:
        story.append(Paragraph("<i>No active inventory database connected for this dataset view.</i>", tier_body))
    story.append(Spacer(1, 10))

    # 6. Section: Data Quality & Anomaly Detection Findings
    story.append(Paragraph("3. Data Quality & Anomaly Audit Findings", section_heading))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#1E3A8A"), spaceAfter=6))

    if anomalies and len(anomalies) > 0:
        anom_rows = [
            [
                Paragraph("Invoice ID", header_cell),
                Paragraph("Error Type", header_cell),
                Paragraph("Severity", header_cell),
                Paragraph("Field", header_cell),
                Paragraph("Audit Description & Recommendation", header_cell),
            ]
        ]
        for item in anomalies[:8]:  # Top 8 anomalies
            sev = item.get("severity", "MEDIUM")
            sev_color = "#DC2626" if sev == "CRITICAL" else ("#EA580C" if sev == "HIGH" else "#475569")
            anom_rows.append([
                Paragraph(str(item.get("invoice_id", "N/A")), cell_style_bold),
                Paragraph(str(item.get("error_type", "")), cell_style),
                Paragraph(f"<font color='{sev_color}'><b>{sev}</b></font>", cell_style),
                Paragraph(str(item.get("affected_field", "")), cell_style),
                Paragraph(f"{item.get('description', '')} — <i>{item.get('action_recommendation', '')}</i>", cell_style),
            ])

        anom_table = Table(anom_rows, colWidths=[70, 95, 55, 62, 250])
        anom_table.setStyle(
            TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1E3A8A")),
                ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
                ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#FFFBEB")]),
                ("TOPPADDING", (0, 0), (-1, -1), 3),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
                ("LEFTPADDING", (0, 0), (-1, -1), 4),
                ("RIGHTPADDING", (0, 0), (-1, -1), 4),
            ])
        )
        story.append(anom_table)
    else:
        clean_box_data = [[
            Paragraph("<b>✅ Clean Data Audit:</b> No calculation discrepancies, corrupt values, or extreme statistical outliers were detected in this dataset.", cell_style)
        ]]
        clean_box = Table(clean_box_data, colWidths=[532])
        clean_box.setStyle(
            TableStyle([
                ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#ECFDF5")),
                ("BOX", (0, 0), (-1, -1), 0.75, colors.HexColor("#10B981")),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                ("LEFTPADDING", (0, 0), (-1, -1), 8),
                ("RIGHTPADDING", (0, 0), (-1, -1), 8),
            ])
        )
        story.append(clean_box)
    story.append(Spacer(1, 10))

    # 7. Section: Category Sales & Volume Breakdown
    if not df.empty and "Product Category" in df.columns and "Sales" in df.columns:
        story.append(Paragraph("4. Category Performance Breakdown", section_heading))
        story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#1E3A8A"), spaceAfter=6))

        cat_summary = (
            df.groupby("Product Category")
            .agg(
                Total_Sales=("Sales", "sum"),
                Units_Sold=("Quantity", "sum") if "Quantity" in df.columns else ("Sales", "count"),
                Txn_Count=("Invoice ID", "count") if "Invoice ID" in df.columns else ("Sales", "count"),
                Avg_Rating=("Rating", "mean") if "Rating" in df.columns else ("Sales", lambda x: 0.0),
            )
            .reset_index()
            .sort_values(by="Total_Sales", ascending=False)
        )

        total_cat_sales = cat_summary["Total_Sales"].sum()

        cat_rows = [
            [
                Paragraph("Product Category", header_cell),
                Paragraph("Total Revenue", header_cell),
                Paragraph("Units Sold", header_cell),
                Paragraph("Transactions", header_cell),
                Paragraph("Revenue Share", header_cell),
                Paragraph("Avg Rating", header_cell),
            ]
        ]

        for _, row in cat_summary.iterrows():
            share_pct = (row["Total_Sales"] / total_cat_sales * 100) if total_cat_sales > 0 else 0.0
            cat_rows.append([
                Paragraph(str(row["Product Category"]), cell_style_bold),
                Paragraph(f"${row['Total_Sales']:,.2f}", cell_style),
                Paragraph(f"{int(row['Units_Sold']):,}", cell_style),
                Paragraph(f"{int(row['Txn_Count']):,}", cell_style),
                Paragraph(f"{share_pct:.1f}%", cell_style),
                Paragraph(f"{float(row['Avg_Rating']):.2f} / 5.0", cell_style),
            ])

        cat_table = Table(cat_rows, colWidths=[142, 85, 75, 75, 80, 75])
        cat_table.setStyle(
            TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1E3A8A")),
                ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
                ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F8FAFC")]),
                ("TOPPADDING", (0, 0), (-1, -1), 3),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
                ("LEFTPADDING", (0, 0), (-1, -1), 4),
                ("RIGHTPADDING", (0, 0), (-1, -1), 4),
            ])
        )
        story.append(cat_table)

    # Build Document with NumberedCanvas
    doc.build(story, canvasmaker=NumberedCanvas)
    buffer.seek(0)
    return buffer


# ==============================================================================
# 3. EXCEL MULTI-SHEET WORKBOOK GENERATOR
# ==============================================================================

def generate_excel_workbook(
    df: pd.DataFrame,
    dataset_name: str = "Active Sales Dataset",
    filter_summary: dict = None,
    insights: list = None,
    anomalies: list = None,
    inventory_df: pd.DataFrame = None,
) -> io.BytesIO:
    """
    Generate an executive-grade, multi-tab Excel workbook formatted with openpyxl.

    Tabs created:
    1. Executive Summary - High-level KPIs and metadata
    2. Sales Transactions - Active filtered transaction records
    3. Product Performance - Product aggregated metrics
    4. Category Performance - Category aggregated metrics
    5. Inventory Intelligence - Inventory stock, velocity, and health
    6. Anomaly Audit Log - Data quality violations and statistical anomalies
    7. Business Insights - 4-Tier structured insights matrix

    Returns:
        io.BytesIO buffer containing the .xlsx workbook.
    """
    wb = openpyxl.Workbook()
    # Remove default sheet
    wb.remove(wb.active)

    # Palette definitions
    navy_header_fill = PatternFill(start_color="1E3A8A", end_color="1E3A8A", fill_type="solid")
    blue_kpi_fill = PatternFill(start_color="EFF6FF", end_color="EFF6FF", fill_type="solid")
    zebra_fill = PatternFill(start_color="F8FAFC", end_color="F8FAFC", fill_type="solid")
    alert_fill = PatternFill(start_color="FFFBEB", end_color="FFFBEB", fill_type="solid")

    font_header = Font(name="Calibri", size=10, bold=True, color="FFFFFF")
    font_bold = Font(name="Calibri", size=10, bold=True, color="0F172A")
    font_regular = Font(name="Calibri", size=10, color="1E293B")
    font_title = Font(name="Calibri", size=14, bold=True, color="1E3A8A")
    font_subtitle = Font(name="Calibri", size=10, italic=True, color="64748B")

    thin_border_side = Side(border_style="thin", color="CBD5E1")
    cell_border = Border(left=thin_border_side, right=thin_border_side, top=thin_border_side, bottom=thin_border_side)

    align_center = Alignment(horizontal="center", vertical="center")
    align_left = Alignment(horizontal="left", vertical="center")
    align_right = Alignment(horizontal="right", vertical="center")
    align_wrap_left = Alignment(horizontal="left", vertical="center", wrap_text=True)

    # ---------------------------------------------------------
    # TAB 1: EXECUTIVE SUMMARY
    # ---------------------------------------------------------
    ws_sum = wb.create_sheet(title="Executive Summary")
    ws_sum.views.sheetView[0].showGridLines = True

    ws_sum["A1"] = "Supermarket Sales & Retail Intelligence System"
    ws_sum["A1"].font = font_title
    ws_sum["A2"] = f"Executive briefing & audit workbook generated on {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    ws_sum["A2"].font = font_subtitle

    # Metadata
    ws_sum["A4"] = "Dataset Source:"
    ws_sum["A4"].font = font_bold
    ws_sum["B4"] = dataset_name
    ws_sum["B4"].font = font_regular

    ws_sum["A5"] = "Total Records:"
    ws_sum["A5"].font = font_bold
    ws_sum["B5"] = len(df)
    ws_sum["B5"].number_format = "#,##0"

    filters_str = "All Records (Unfiltered)"
    if filter_summary:
        filters_str = "; ".join(f"{k}: {v}" for k, v in filter_summary.items())
    ws_sum["A6"] = "Active Filters:"
    ws_sum["A6"].font = font_bold
    ws_sum["B6"] = filters_str

    # KPI Block
    total_sales = float(df["Sales"].sum()) if not df.empty and "Sales" in df.columns else 0.0
    total_qty = int(df["Quantity"].sum()) if not df.empty and "Quantity" in df.columns else 0
    total_txns = len(df)
    avg_order_val = total_sales / total_txns if total_txns > 0 else 0.0
    avg_rating = float(df["Rating"].mean()) if not df.empty and "Rating" in df.columns else 0.0

    kpis = [
        ("Total Sales Revenue", total_sales, "$#,##0.00"),
        ("Total Units Sold", total_qty, "#,##0"),
        ("Total Transactions", total_txns, "#,##0"),
        ("Average Order Value", avg_order_val, "$#,##0.00"),
        ("Average Rating", avg_rating, "0.00"),
    ]

    ws_sum["A8"] = "Key Performance Indicator"
    ws_sum["B8"] = "Analyzed Value"
    for col in ["A8", "B8"]:
        ws_sum[col].fill = navy_header_fill
        ws_sum[col].font = font_header
        ws_sum[col].border = cell_border

    for i, (k, v, fmt) in enumerate(kpis, start=9):
        ws_sum[f"A{i}"] = k
        ws_sum[f"A{i}"].font = font_bold
        ws_sum[f"A{i}"].border = cell_border
        ws_sum[f"A{i}"].fill = zebra_fill if i % 2 == 0 else PatternFill(fill_type=None)

        ws_sum[f"B{i}"] = v
        ws_sum[f"B{i}"].font = font_regular
        ws_sum[f"B{i}"].border = cell_border
        ws_sum[f"B{i}"].number_format = fmt
        ws_sum[f"B{i}"].alignment = align_right

    # ---------------------------------------------------------
    # TAB 2: SALES TRANSACTIONS (Filtered Dataset)
    # ---------------------------------------------------------
    ws_tx = wb.create_sheet(title="Sales Transactions")
    ws_tx.views.sheetView[0].showGridLines = True
    ws_tx.freeze_panes = "A2"

    if not df.empty:
        # Headers
        headers = list(df.columns)
        for col_num, h_text in enumerate(headers, 1):
            cell = ws_tx.cell(row=1, column=col_num, value=h_text)
            cell.fill = navy_header_fill
            cell.font = font_header
            cell.alignment = align_center
            cell.border = cell_border

        # Rows
        for row_idx, row_data in enumerate(df.itertuples(index=False), 2):
            is_zebra = (row_idx % 2 == 0)
            for col_idx, value in enumerate(row_data, 1):
                col_name = headers[col_idx - 1]
                cell = ws_tx.cell(row=row_idx, column=col_idx)

                # Format specific columns
                if col_name in ["Date"] and pd.notna(value):
                    cell.value = str(value)[:10]
                    cell.alignment = align_center
                elif col_name in ["Sales", "Unit Price", "Total"] and pd.notna(value):
                    cell.value = float(value)
                    cell.number_format = "$#,##0.00"
                    cell.alignment = align_right
                elif col_name in ["Quantity"] and pd.notna(value):
                    cell.value = int(value)
                    cell.number_format = "#,##0"
                    cell.alignment = align_right
                elif col_name in ["Rating"] and pd.notna(value):
                    cell.value = float(value)
                    cell.number_format = "0.0"
                    cell.alignment = align_right
                else:
                    cell.value = str(value) if pd.notna(value) else ""
                    cell.alignment = align_left

                cell.font = font_regular
                cell.border = cell_border
                if is_zebra:
                    cell.fill = zebra_fill

    # ---------------------------------------------------------
    # TAB 3: PRODUCT PERFORMANCE
    # ---------------------------------------------------------
    if not df.empty and "Product" in df.columns and "Sales" in df.columns:
        ws_prod = wb.create_sheet(title="Product Performance")
        ws_prod.views.sheetView[0].showGridLines = True
        ws_prod.freeze_panes = "A2"

        prod_agg = (
            df.groupby("Product")
            .agg(
                Category=("Product Category", "first") if "Product Category" in df.columns else ("Product", "first"),
                Units_Sold=("Quantity", "sum") if "Quantity" in df.columns else ("Sales", "count"),
                Total_Sales=("Sales", "sum"),
                Avg_Price=("Unit Price", "mean") if "Unit Price" in df.columns else ("Sales", "mean"),
                Avg_Rating=("Rating", "mean") if "Rating" in df.columns else ("Sales", lambda x: 0.0),
                Transactions=("Invoice ID", "count") if "Invoice ID" in df.columns else ("Sales", "count"),
            )
            .reset_index()
            .sort_values(by="Total_Sales", ascending=False)
        )

        p_headers = ["Product", "Category", "Units Sold", "Total Revenue", "Avg Unit Price", "Avg Rating", "Transactions"]
        for c_idx, h_text in enumerate(p_headers, 1):
            cell = ws_prod.cell(row=1, column=c_idx, value=h_text)
            cell.fill = navy_header_fill
            cell.font = font_header
            cell.alignment = align_center
            cell.border = cell_border

        for r_idx, row in enumerate(prod_agg.itertuples(index=False), 2):
            is_zebra = (r_idx % 2 == 0)
            ws_prod.cell(row=r_idx, column=1, value=row.Product).alignment = align_left
            ws_prod.cell(row=r_idx, column=2, value=row.Category).alignment = align_left
            
            c3 = ws_prod.cell(row=r_idx, column=3, value=int(row.Units_Sold))
            c3.number_format = "#,##0"
            c3.alignment = align_right

            c4 = ws_prod.cell(row=r_idx, column=4, value=float(row.Total_Sales))
            c4.number_format = "$#,##0.00"
            c4.alignment = align_right

            c5 = ws_prod.cell(row=r_idx, column=5, value=float(row.Avg_Price))
            c5.number_format = "$#,##0.00"
            c5.alignment = align_right

            c6 = ws_prod.cell(row=r_idx, column=6, value=float(row.Avg_Rating))
            c6.number_format = "0.00"
            c6.alignment = align_right

            c7 = ws_prod.cell(row=r_idx, column=7, value=int(row.Transactions))
            c7.number_format = "#,##0"
            c7.alignment = align_right

            for c in range(1, 8):
                cell = ws_prod.cell(row=r_idx, column=c)
                cell.font = font_regular
                cell.border = cell_border
                if is_zebra:
                    cell.fill = zebra_fill

    # ---------------------------------------------------------
    # TAB 4: CATEGORY PERFORMANCE
    # ---------------------------------------------------------
    if not df.empty and "Product Category" in df.columns and "Sales" in df.columns:
        ws_cat = wb.create_sheet(title="Category Performance")
        ws_cat.views.sheetView[0].showGridLines = True
        ws_cat.freeze_panes = "A2"

        cat_agg = (
            df.groupby("Product Category")
            .agg(
                Units_Sold=("Quantity", "sum") if "Quantity" in df.columns else ("Sales", "count"),
                Total_Sales=("Sales", "sum"),
                Transactions=("Invoice ID", "count") if "Invoice ID" in df.columns else ("Sales", "count"),
                Avg_Rating=("Rating", "mean") if "Rating" in df.columns else ("Sales", lambda x: 0.0),
            )
            .reset_index()
            .sort_values(by="Total_Sales", ascending=False)
        )
        total_cat_rev = cat_agg["Total_Sales"].sum()

        c_headers = ["Product Category", "Units Sold", "Total Revenue", "Revenue Share", "Transactions", "Avg Rating"]
        for c_idx, h_text in enumerate(c_headers, 1):
            cell = ws_cat.cell(row=1, column=c_idx, value=h_text)
            cell.fill = navy_header_fill
            cell.font = font_header
            cell.alignment = align_center
            cell.border = cell_border

        for r_idx, row in enumerate(cat_agg.itertuples(index=False), 2):
            is_zebra = (r_idx % 2 == 0)
            share_val = (row.Total_Sales / total_cat_rev) if total_cat_rev > 0 else 0.0
            ws_cat.cell(row=r_idx, column=1, value=str(row[0])).alignment = align_left
            c2 = ws_cat.cell(row=r_idx, column=2, value=int(row.Units_Sold))
            c2.number_format = "#,##0"
            c2.alignment = align_right

            c3 = ws_cat.cell(row=r_idx, column=3, value=float(row.Total_Sales))
            c3.number_format = "$#,##0.00"
            c3.alignment = align_right

            c4 = ws_cat.cell(row=r_idx, column=4, value=float(share_val))
            c4.number_format = "0.0%"
            c4.alignment = align_right

            c5 = ws_cat.cell(row=r_idx, column=5, value=int(row.Transactions))
            c5.number_format = "#,##0"
            c5.alignment = align_right

            c6 = ws_cat.cell(row=r_idx, column=6, value=float(row.Avg_Rating))
            c6.number_format = "0.00"
            c6.alignment = align_right

            for c in range(1, 7):
                cell = ws_cat.cell(row=r_idx, column=c)
                cell.font = font_regular
                cell.border = cell_border
                if is_zebra:
                    cell.fill = zebra_fill

    # ---------------------------------------------------------
    # TAB 5: INVENTORY INTELLIGENCE
    # ---------------------------------------------------------
    if inventory_df is not None and not inventory_df.empty:
        ws_inv = wb.create_sheet(title="Inventory Intelligence")
        ws_inv.views.sheetView[0].showGridLines = True
        ws_inv.freeze_panes = "A2"

        inv_headers = [
            "Product Name", "Category", "Current Stock", "Safety Stock",
            "Daily Sales Velocity", "Days Stock Remaining", "Velocity Tier",
            "Health Status", "Reorder Required", "Reorder Qty", "Estimated Reorder Cost"
        ]
        for c_idx, h_text in enumerate(inv_headers, 1):
            cell = ws_inv.cell(row=1, column=c_idx, value=h_text)
            cell.fill = navy_header_fill
            cell.font = font_header
            cell.alignment = align_center
            cell.border = cell_border

        for r_idx, row in enumerate(inventory_df.itertuples(index=False), 2):
            is_zebra = (r_idx % 2 == 0)
            ws_inv.cell(row=r_idx, column=1, value=getattr(row, "product_name", "")).alignment = align_left
            ws_inv.cell(row=r_idx, column=2, value=getattr(row, "category_name", "")).alignment = align_left

            c3 = ws_inv.cell(row=r_idx, column=3, value=int(getattr(row, "current_stock", 0)))
            c3.number_format = "#,##0"
            c3.alignment = align_right

            c4 = ws_inv.cell(row=r_idx, column=4, value=int(getattr(row, "safety_stock_level", 0)))
            c4.number_format = "#,##0"
            c4.alignment = align_right

            c5 = ws_inv.cell(row=r_idx, column=5, value=float(getattr(row, "daily_sales_velocity", 0.0)))
            c5.number_format = "0.00"
            c5.alignment = align_right

            c6 = ws_inv.cell(row=r_idx, column=6, value=float(getattr(row, "days_of_stock_remaining", 0.0)))
            c6.number_format = "0.0"
            c6.alignment = align_right

            ws_inv.cell(row=r_idx, column=7, value=getattr(row, "velocity_tier", "")).alignment = align_center
            
            c8 = ws_inv.cell(row=r_idx, column=8, value=getattr(row, "health_status", ""))
            c8.alignment = align_center
            c8.font = font_bold

            c9 = ws_inv.cell(row=r_idx, column=9, value="YES" if getattr(row, "reorder_flag", 0) == 1 else "NO")
            c9.alignment = align_center

            c10 = ws_inv.cell(row=r_idx, column=10, value=int(getattr(row, "recommended_reorder_qty", 0)))
            c10.number_format = "#,##0"
            c10.alignment = align_right

            c11 = ws_inv.cell(row=r_idx, column=11, value=float(getattr(row, "estimated_reorder_cost", 0.0)))
            c11.number_format = "$#,##0.00"
            c11.alignment = align_right

            for c in range(1, 12):
                cell = ws_inv.cell(row=r_idx, column=c)
                if cell.font != font_bold:
                    cell.font = font_regular
                cell.border = cell_border
                if is_zebra:
                    cell.fill = zebra_fill

    # ---------------------------------------------------------
    # TAB 6: ANOMALY AUDIT LOG
    # ---------------------------------------------------------
    if anomalies is not None:
        ws_anom = wb.create_sheet(title="Anomaly Audit Log")
        ws_anom.views.sheetView[0].showGridLines = True
        ws_anom.freeze_panes = "A2"

        anom_headers = [
            "Rule ID", "Error Type", "Severity", "Invoice ID",
            "Affected Field", "Recorded Value", "Expected Value",
            "Audit Description", "Recommended Action"
        ]
        for c_idx, h_text in enumerate(anom_headers, 1):
            cell = ws_anom.cell(row=1, column=c_idx, value=h_text)
            cell.fill = navy_header_fill
            cell.font = font_header
            cell.alignment = align_center
            cell.border = cell_border

        for r_idx, item in enumerate(anomalies, 2):
            is_zebra = (r_idx % 2 == 0)
            ws_anom.cell(row=r_idx, column=1, value=item.get("rule_id", "")).alignment = align_left
            ws_anom.cell(row=r_idx, column=2, value=item.get("error_type", "")).alignment = align_left
            
            c3 = ws_anom.cell(row=r_idx, column=3, value=item.get("severity", ""))
            c3.alignment = align_center
            c3.font = font_bold

            ws_anom.cell(row=r_idx, column=4, value=str(item.get("invoice_id", ""))).alignment = align_left
            ws_anom.cell(row=r_idx, column=5, value=str(item.get("affected_field", ""))).alignment = align_left
            ws_anom.cell(row=r_idx, column=6, value=str(item.get("recorded_value", ""))).alignment = align_right
            ws_anom.cell(row=r_idx, column=7, value=str(item.get("expected_value", ""))).alignment = align_right
            ws_anom.cell(row=r_idx, column=8, value=str(item.get("description", ""))).alignment = align_wrap_left
            ws_anom.cell(row=r_idx, column=9, value=str(item.get("action_recommendation", ""))).alignment = align_wrap_left

            for c in range(1, 10):
                cell = ws_anom.cell(row=r_idx, column=c)
                if cell.font != font_bold:
                    cell.font = font_regular
                cell.border = cell_border
                if is_zebra:
                    cell.fill = zebra_fill

    # ---------------------------------------------------------
    # TAB 7: BUSINESS INSIGHTS MATRIX
    # ---------------------------------------------------------
    if insights is not None:
        ws_ins = wb.create_sheet(title="Business Insights Matrix")
        ws_ins.views.sheetView[0].showGridLines = True
        ws_ins.freeze_panes = "A2"

        ins_headers = [
            "Category", "Priority", "Title", "Observation",
            "Analytical Insight", "Possible Explanation", "Recommended Action"
        ]
        for c_idx, h_text in enumerate(ins_headers, 1):
            cell = ws_ins.cell(row=1, column=c_idx, value=h_text)
            cell.fill = navy_header_fill
            cell.font = font_header
            cell.alignment = align_center
            cell.border = cell_border

        for r_idx, item in enumerate(insights, 2):
            is_zebra = (r_idx % 2 == 0)
            ws_ins.cell(row=r_idx, column=1, value=item.get("category", "")).alignment = align_center
            
            c2 = ws_ins.cell(row=r_idx, column=2, value=item.get("priority", ""))
            c2.alignment = align_center
            c2.font = font_bold

            ws_ins.cell(row=r_idx, column=3, value=item.get("title", "")).alignment = align_left
            ws_ins.cell(row=r_idx, column=4, value=item.get("observation", "")).alignment = align_wrap_left
            ws_ins.cell(row=r_idx, column=5, value=item.get("insight", "")).alignment = align_wrap_left
            ws_ins.cell(row=r_idx, column=6, value=item.get("explanation", "")).alignment = align_wrap_left
            ws_ins.cell(row=r_idx, column=7, value=item.get("action", "")).alignment = align_wrap_left

            for c in range(1, 8):
                cell = ws_ins.cell(row=r_idx, column=c)
                if cell.font != font_bold:
                    cell.font = font_regular
                cell.border = cell_border
                if is_zebra:
                    cell.fill = zebra_fill

    # Auto-adjust column widths across all sheets
    for sheet in wb.worksheets:
        for col in sheet.columns:
            max_len = 0
            col_letter = get_column_letter(col[0].column)
            for cell in col:
                val = str(cell.value or "")
                if len(val) > max_len:
                    max_len = len(val)
            # Constrain width between 10 and 50 characters
            adjusted_width = min(max(max_len + 3, 10), 50)
            sheet.column_dimensions[col_letter].width = adjusted_width

    buffer = io.BytesIO()
    wb.save(buffer)
    buffer.seek(0)
    return buffer


# ==============================================================================
# 4. CSV EXPORT UTILITY
# ==============================================================================

def generate_csv_export(df: pd.DataFrame) -> str:
    """
    Generate an RFC-4180 compliant CSV string from the active DataFrame.
    """
    if df is None or df.empty:
        return ""
    return df.to_csv(index=False)
