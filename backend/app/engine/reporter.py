import os
from pathlib import Path
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image as RLImage
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

class PDFReportGenerator:
    @staticmethod
    def generate(
        run_data: dict,
        output_pdf_path: str
    ) -> str:
        Path(output_pdf_path).parent.mkdir(parents=True, exist_ok=True)
        doc = SimpleDocTemplate(
            output_pdf_path,
            pagesize=letter,
            rightMargin=36,
            leftMargin=36,
            topMargin=36,
            bottomMargin=36
        )

        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'TitleStyle',
            parent=styles['Heading1'],
            fontSize=22,
            leading=26,
            textColor=colors.HexColor('#0f172a'),
            spaceAfter=6
        )
        subtitle_style = ParagraphStyle(
            'SubtitleStyle',
            parent=styles['Normal'],
            fontSize=11,
            leading=14,
            textColor=colors.HexColor('#64748b'),
            spaceAfter=15
        )
        badge_style_pass = ParagraphStyle(
            'BadgePass',
            parent=styles['Normal'],
            fontSize=12,
            fontName='Helvetica-Bold',
            textColor=colors.HexColor('#166534')
        )
        badge_style_fail = ParagraphStyle(
            'BadgeFail',
            parent=styles['Normal'],
            fontSize=12,
            fontName='Helvetica-Bold',
            textColor=colors.HexColor('#991b1b')
        )
        cell_style = ParagraphStyle(
            'CellText',
            parent=styles['Normal'],
            fontSize=9,
            leading=12,
            textColor=colors.HexColor('#334155')
        )
        cell_bold = ParagraphStyle(
            'CellBold',
            parent=styles['Normal'],
            fontSize=9,
            leading=12,
            fontName='Helvetica-Bold',
            textColor=colors.HexColor('#0f172a')
        )

        elements = []

        # 1. Header
        elements.append(Paragraph("AutoQA Execution Audit Report", title_style))
        elements.append(Paragraph(f"Autonomous E2E Verification Report • Generated {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}", subtitle_style))

        # 2. Executive Metadata Box
        status = run_data.get("status", "UNKNOWN")
        badge = Paragraph(f"STATUS: {status}", badge_style_pass if status == "PASSED" else badge_style_fail)

        meta_table_data = [
            [Paragraph("Scenario Title:", cell_bold), Paragraph(run_data.get("scenario_title", "N/A"), cell_style)],
            [Paragraph("Target URL:", cell_bold), Paragraph(run_data.get("base_url", "N/A"), cell_style)],
            [Paragraph("Goal Description:", cell_bold), Paragraph(run_data.get("goal_prompt", "N/A"), cell_style)],
            [Paragraph("Duration:", cell_bold), Paragraph(f"{run_data.get('duration_ms', 0) / 1000:.2f} seconds", cell_style)],
            [Paragraph("Total Steps:", cell_bold), Paragraph(str(len(run_data.get("steps", []))), cell_style)],
            [Paragraph("Final Outcome:", cell_bold), badge]
        ]

        meta_table = Table(meta_table_data, colWidths=[110, 430])
        meta_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#f8fafc')),
            ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#e2e8f0')),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('BOTTOMPADDING', (0,0), (-1,-1), 5),
            ('TOPPADDING', (0,0), (-1,-1), 5),
            ('LEFTPADDING', (0,0), (-1,-1), 8),
        ]))
        elements.append(meta_table)
        elements.append(Spacer(1, 15))

        # 3. Step by Step Log Table
        elements.append(Paragraph("Chronological Execution Steps", styles['Heading2']))
        elements.append(Spacer(1, 6))

        step_table_headers = [
            Paragraph("#", cell_bold),
            Paragraph("Action", cell_bold),
            Paragraph("Target / Selector", cell_bold),
            Paragraph("Agent Reasoning", cell_bold),
            Paragraph("Status", cell_bold)
        ]
        step_table_rows = [step_table_headers]

        for s in run_data.get("steps", []):
            step_table_rows.append([
                Paragraph(str(s.get("step_number", "")), cell_style),
                Paragraph(s.get("action_type", "").upper(), cell_bold),
                Paragraph(s.get("resolved_selector", "") or "-", cell_style),
                Paragraph(s.get("thought", "") or "-", cell_style),
                Paragraph(s.get("status", "SUCCESS"), cell_style)
            ])

        step_table = Table(step_table_rows, colWidths=[25, 65, 150, 240, 60])
        step_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#f1f5f9')),
            ('LINEBELOW', (0,0), (-1,0), 1, colors.HexColor('#cbd5e1')),
            ('LINEBELOW', (0,1), (-1,-1), 0.5, colors.HexColor('#e2e8f0')),
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
            ('TOPPADDING', (0,0), (-1,-1), 4),
            ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ]))
        elements.append(step_table)

        doc.build(elements)
        return output_pdf_path
