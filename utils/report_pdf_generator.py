"""
PharmaValidate v0.5 - Validation Report PDF Generator
Generates comprehensive validation reports with all module results
"""

from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, KeepTogether
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfgen import canvas


class NumberedCanvas(canvas.Canvas):
    """Canvas subclass for page numbers and headers."""
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

    def draw_page_decorations(self, page_count):
        self.saveState()
        self.setFont("Helvetica-Bold", 8)
        self.setFillColor(colors.HexColor("#475569"))
        
        if self._pageNumber > 1:
            self.drawString(54, 750, "VALIDATION SUMMARY REPORT")
            self.setStrokeColor(colors.HexColor("#CBD5E1"))
            self.setLineWidth(0.5)
            self.line(54, 742, 558, 742)
            
            self.line(54, 55, 558, 55)
            page_text = f"Page {self._pageNumber} of {page_count}"
            self.drawRightString(558, 40, page_text)
            self.drawString(54, 40, "CONFIDENTIAL - PHARMAVALIDATE QUALITY ASSURANCE SYSTEM")
            
        self.restoreState()


def generate_validation_report_pdf(output_path, data):
    """Generates the complete validation report PDF."""
    
    project = data.get("project")
    if not project:
        raise ValueError("No project data provided")
    
    protocol = data.get("protocol")
    specificity = data.get("specificity", [])
    linearity = data.get("linearity", [])
    accuracy = data.get("accuracy")
    precision = data.get("precision")
    ofat = data.get("ofat", [])
    doe = data.get("doe")
    impurities = data.get("impurities", [])
    summary = data.get("summary")

    _, name, product, method, val_type, protocol_num, analyst = project
    current_date = datetime.now().strftime("%B %d, %Y")

    # Document setup
    doc = SimpleDocTemplate(
        output_path,
        pagesize=letter,
        leftMargin=54,
        rightMargin=54,
        topMargin=72,
        bottomMargin=72
    )

    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'CoverTitle', parent=styles['Normal'],
        fontName='Helvetica-Bold', fontSize=22, leading=26,
        textColor=colors.HexColor("#1E3A8A"), spaceAfter=10
    )
    subtitle_style = ParagraphStyle(
        'CoverSubtitle', parent=styles['Normal'],
        fontName='Helvetica', fontSize=12, leading=16,
        textColor=colors.HexColor("#475569"), spaceAfter=20
    )
    h1_style = ParagraphStyle(
        'Heading1', parent=styles['Normal'],
        fontName='Helvetica-Bold', fontSize=14, leading=18,
        textColor=colors.HexColor("#0F172A"), spaceBefore=14, spaceAfter=8,
        keepWithNext=True
    )
    h2_style = ParagraphStyle(
        'Heading2', parent=styles['Normal'],
        fontName='Helvetica-Bold', fontSize=12, leading=16,
        textColor=colors.HexColor("#1E3A8A"), spaceBefore=10, spaceAfter=6
    )
    body_style = ParagraphStyle(
        'BodyText', parent=styles['Normal'],
        fontName='Helvetica', fontSize=9.5, leading=14,
        textColor=colors.HexColor("#334155"), spaceAfter=6
    )
    table_header_style = ParagraphStyle(
        'TableHeader', parent=styles['Normal'],
        fontName='Helvetica-Bold', fontSize=8.5, leading=10,
        textColor=colors.white
    )
    table_body_style = ParagraphStyle(
        'TableBody', parent=styles['Normal'],
        fontName='Helvetica', fontSize=8, leading=10,
        textColor=colors.HexColor("#334155")
    )

    story = []

    # ============================================
    # COVER PAGE
    # ============================================
    story.append(Spacer(1, 10))
    
    accent_bar = Table([[""]], colWidths=[7.0*inch], rowHeights=[4])
    accent_bar.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#1E3A8A")),
        ('TOPPADDING', (0, 0), (-1, -1), 0),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
    ]))
    story.append(accent_bar)
    story.append(Spacer(1, 15))
    
    story.append(Paragraph("VALIDATION SUMMARY REPORT", title_style))
    story.append(Paragraph(f"PROJECT: {name.upper()}", subtitle_style))
    story.append(Paragraph(f"Product: {product} | Method: {method} | Protocol: {protocol_num}", subtitle_style))
    story.append(Spacer(1, 15))

    # Metadata
    meta_data = [
        [Paragraph("<b>Project Name:</b>", body_style), Paragraph(name, body_style)],
        [Paragraph("<b>Product:</b>", body_style), Paragraph(product, body_style)],
        [Paragraph("<b>Method:</b>", body_style), Paragraph(method, body_style)],
        [Paragraph("<b>Validation Type:</b>", body_style), Paragraph(val_type, body_style)],
        [Paragraph("<b>Protocol Number:</b>", body_style), Paragraph(protocol_num, body_style)],
        [Paragraph("<b>Analyst:</b>", body_style), Paragraph(analyst, body_style)],
        [Paragraph("<b>Report Date:</b>", body_style), Paragraph(current_date, body_style)],
    ]
    meta_table = Table(meta_data, colWidths=[2.0*inch, 5.0*inch])
    meta_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('LINEBELOW', (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(meta_table)
    story.append(Spacer(1, 20))

    # Overall Status
    if summary:
        overall = summary.get("overall_status", "PENDING")
        color = "#10B981" if overall == "PASS" else "#EF4444" if overall == "FAIL" else "#F59E0B"
        status_data = [
            [Paragraph("<b>OVERALL VALIDATION STATUS</b>", body_style), 
             Paragraph(f"<font color='{color}' size='16'><b>{overall}</b></font>", body_style)]
        ]
        status_table = Table(status_data, colWidths=[3.5*inch, 3.5*inch])
        status_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#F8FAFC")),
            ('BOX', (0, 0), (-1, -1), 1, colors.HexColor("#CBD5E1")),
            ('TOPPADDING', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
        ]))
        story.append(status_table)

    story.append(Spacer(1, 30))
    story.append(Paragraph("<b>APPROVAL SIGN-OFF</b>", h1_style))
    sig_data = [
        [Paragraph("Role", table_header_style), Paragraph("Name", table_header_style), Paragraph("Signature / Date", table_header_style)],
        [Paragraph("<b>Prepared By:</b><br/>QC Analyst", table_body_style), 
         Paragraph(analyst, table_body_style), 
         Paragraph("<br/><br/>___________________________", table_body_style)],
        [Paragraph("<b>Reviewed By:</b><br/>QC Supervisor", table_body_style), 
         Paragraph("<br/><br/>___________________________", table_body_style), 
         Paragraph("<br/><br/>___________________________", table_body_style)],
        [Paragraph("<b>Approved By:</b><br/>QA Manager", table_body_style), 
         Paragraph("<br/><br/>___________________________", table_body_style), 
         Paragraph("<br/><br/>___________________________", table_body_style)],
    ]
    sig_table = Table(sig_data, colWidths=[2.4*inch, 2.3*inch, 2.3*inch])
    sig_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#1E3A8A")),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(sig_table)
    story.append(PageBreak())

    # ============================================
    # MODULE RESULTS
    # ============================================

    # 1. Specificity
    if specificity:
        story.append(Paragraph("1. SPECIFICITY RESULTS", h1_style))
        spec_data = [
            [Paragraph("Sample Type", table_header_style),
             Paragraph("Peak", table_header_style),
             Paragraph("Rt (min)", table_header_style),
             Paragraph("Area", table_header_style),
             Paragraph("Resolution", table_header_style),
             Paragraph("Interference (%)", table_header_style),
             Paragraph("Status", table_header_style)]
        ]
        for row in specificity:
            sample_type, peak, rt, area, res, interference, status = row
            color = "green" if status == "PASS" else "red" if status == "FAIL" else "gray"
            spec_data.append([
                Paragraph(str(sample_type) if sample_type else "N/A", table_body_style),
                Paragraph(str(peak) if peak else "N/A", table_body_style),
                Paragraph(str(rt) if rt else "N/A", table_body_style),
                Paragraph(str(area) if area else "N/A", table_body_style),
                Paragraph(str(res) if res else "N/A", table_body_style),
                Paragraph(str(interference) if interference else "0.0", table_body_style),
                Paragraph(f"<font color='{color}'><b>{status}</b></font>", table_body_style)
            ])
        spec_table = Table(spec_data, colWidths=[1.2*inch, 0.8*inch, 0.8*inch, 0.8*inch, 0.8*inch, 1.0*inch, 0.8*inch])
        spec_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#1E3A8A")),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor("#F8FAFC")]),
            ('TOPPADDING', (0, 0), (-1, -1), 5),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ]))
        story.append(KeepTogether([spec_table]))
        story.append(Spacer(1, 10))

    # 2. Linearity
    if linearity:
        story.append(Paragraph("2. LINEARITY RESULTS", h1_style))
        
        first = linearity[0]
        story.append(Paragraph(f"<b>Slope:</b> {first[10]}  <b>Intercept:</b> {first[11]}  <b>R²:</b> {first[12]}  <b>% Y-Intercept:</b> {first[13]}", body_style))
        story.append(Paragraph(f"<b>Overall Status:</b> {first[20] if len(first) > 20 else 'PENDING'}", body_style))
        story.append(Spacer(1, 5))
        
        linearity_data = [
            [Paragraph("Level", table_header_style),
             Paragraph("Nom (%)", table_header_style),
             Paragraph("W1", table_header_style),
             Paragraph("W2", table_header_style),
             Paragraph("W3", table_header_style),
             Paragraph("A1", table_header_style),
             Paragraph("A2", table_header_style),
             Paragraph("A3", table_header_style),
             Paragraph("Mean", table_header_style),
             Paragraph("% RSD", table_header_style)]
        ]
        for row in linearity:
            linearity_data.append([
                Paragraph(str(row[1]), table_body_style),
                Paragraph(str(row[2]), table_body_style),
                Paragraph(str(row[3]), table_body_style),
                Paragraph(str(row[4]), table_body_style),
                Paragraph(str(row[5]), table_body_style),
                Paragraph(str(row[6]), table_body_style),
                Paragraph(str(row[7]), table_body_style),
                Paragraph(str(row[8]), table_body_style),
                Paragraph(str(row[9]), table_body_style),
                Paragraph(str(row[10]), table_body_style)
            ])
        lin_table = Table(linearity_data, colWidths=[0.6*inch, 0.7*inch, 0.7*inch, 0.7*inch, 0.7*inch, 0.7*inch, 0.7*inch, 0.7*inch, 0.8*inch, 0.8*inch])
        lin_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#1E3A8A")),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor("#F8FAFC")]),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ('FONTSIZE', (0, 0), (-1, -1), 7),
        ]))
        story.append(KeepTogether([lin_table]))
        story.append(Spacer(1, 10))

    # 3. Accuracy
    if accuracy:
        story.append(Paragraph("3. ACCURACY RESULTS", h1_style))
        
        story.append(Paragraph("<b>SST Results:</b>", h2_style))
        story.append(Paragraph(f"Mean: {accuracy[6] if len(accuracy) > 6 else 'N/A'}  |  % RSD: {accuracy[7] if len(accuracy) > 7 else 'N/A'}", body_style))
        
        acc_data = [
            [Paragraph("Level", table_header_style),
             Paragraph("Mean Recovery (%)", table_header_style),
             Paragraph("% RSD", table_header_style),
             Paragraph("Bias (%)", table_header_style),
             Paragraph("Status", table_header_style)]
        ]
        
        if len(accuracy) > 24:
            acc_data.append([
                Paragraph("80%", table_body_style),
                Paragraph(str(accuracy[21]) if len(accuracy) > 21 else "N/A", table_body_style),
                Paragraph(str(accuracy[22]) if len(accuracy) > 22 else "N/A", table_body_style),
                Paragraph(str(accuracy[23]) if len(accuracy) > 23 else "N/A", table_body_style),
                Paragraph(accuracy[24] if len(accuracy) > 24 else "PENDING", table_body_style)
            ])
        if len(accuracy) > 39:
            acc_data.append([
                Paragraph("100%", table_body_style),
                Paragraph(str(accuracy[36]) if len(accuracy) > 36 else "N/A", table_body_style),
                Paragraph(str(accuracy[37]) if len(accuracy) > 37 else "N/A", table_body_style),
                Paragraph(str(accuracy[38]) if len(accuracy) > 38 else "N/A", table_body_style),
                Paragraph(accuracy[39] if len(accuracy) > 39 else "PENDING", table_body_style)
            ])
        if len(accuracy) > 54:
            acc_data.append([
                Paragraph("120%", table_body_style),
                Paragraph(str(accuracy[51]) if len(accuracy) > 51 else "N/A", table_body_style),
                Paragraph(str(accuracy[52]) if len(accuracy) > 52 else "N/A", table_body_style),
                Paragraph(str(accuracy[53]) if len(accuracy) > 53 else "N/A", table_body_style),
                Paragraph(accuracy[54] if len(accuracy) > 54 else "PENDING", table_body_style)
            ])
        
        acc_table = Table(acc_data, colWidths=[1.0*inch, 1.5*inch, 1.0*inch, 1.0*inch, 1.5*inch])
        acc_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#1E3A8A")),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor("#F8FAFC")]),
            ('TOPPADDING', (0, 0), (-1, -1), 5),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ]))
        story.append(KeepTogether([acc_table]))
        story.append(Spacer(1, 5))
        
        if len(accuracy) > 59:
            story.append(Paragraph(
                f"<b>Overall Mean Recovery:</b> {accuracy[55]}%  |  "
                f"<b>Overall % RSD:</b> {accuracy[56]}%  |  "
                f"<b>Overall Status:</b> {accuracy[59]}",
                body_style
            ))
        story.append(Spacer(1, 10))

    # 4. Precision
    if precision:
        story.append(Paragraph("4. PRECISION RESULTS", h1_style))
        
        story.append(Paragraph("<b>Repeatability (Analyst 1 / Day 1):</b>", h2_style))
        story.append(Paragraph(
            f"Replicates: {precision[1]}, {precision[2]}, {precision[3]}, {precision[4]}, {precision[5]}, {precision[6]}  |  "
            f"Mean: {precision[7]}  |  SD: {precision[8]}  |  % RSD: {precision[9]}  |  Status: {precision[10]}",
            body_style
        ))
        
        story.append(Paragraph("<b>Intermediate Precision (Analyst 2 / Day 2):</b>", h2_style))
        if precision[11]:
            story.append(Paragraph(
                f"Replicates: {precision[11]}, {precision[12]}, {precision[13]}, {precision[14]}, {precision[15]}, {precision[16]}  |  "
                f"Mean: {precision[17]}  |  SD: {precision[18]}  |  % RSD: {precision[19]}  |  Status: {precision[20]}",
                body_style
            ))
        else:
            story.append(Paragraph("No Intermediate Precision data available.", body_style))
        
        story.append(Paragraph("<b>Combined Precision:</b>", h2_style))
        story.append(Paragraph(
            f"Combined Mean: {precision[21]}  |  Pooled SD: {precision[22]}  |  Combined % RSD: {precision[23]}  |  Overall Status: {precision[24]}",
            body_style
        ))
        story.append(Spacer(1, 10))

    # 5. Robustness
    if ofat or doe:
        story.append(Paragraph("5. ROBUSTNESS RESULTS", h1_style))
        
        if ofat:
            story.append(Paragraph("<b>OFAT Robustness:</b>", h2_style))
            ofat_data = [
                [Paragraph("Parameter", table_header_style),
                 Paragraph("Rt", table_header_style),
                 Paragraph("Tailing", table_header_style),
                 Paragraph("Plates", table_header_style),
                 Paragraph("Assay (%)", table_header_style),
                 Paragraph("Dev (%)", table_header_style),
                 Paragraph("Status", table_header_style)]
            ]
            for row in ofat:
                color = "green" if row[9] == "PASS" else "red" if row[9] == "FAIL" else "gray"
                nominal_marker = "⭐ " if row[8] else ""
                ofat_data.append([
                    Paragraph(f"{nominal_marker}{row[2]}", table_body_style),
                    Paragraph(str(row[3]) if row[3] else "N/A", table_body_style),
                    Paragraph(str(row[4]) if row[4] else "N/A", table_body_style),
                    Paragraph(str(row[5]) if row[5] else "N/A", table_body_style),
                    Paragraph(str(row[6]) if row[6] else "N/A", table_body_style),
                    Paragraph(str(row[7]) if row[7] else "N/A", table_body_style),
                    Paragraph(f"<font color='{color}'><b>{row[9]}</b></font>", table_body_style)
                ])
            ofat_table = Table(ofat_data, colWidths=[1.5*inch, 0.7*inch, 0.7*inch, 0.7*inch, 0.8*inch, 0.8*inch, 0.8*inch])
            ofat_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#1E3A8A")),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor("#F8FAFC")]),
                ('TOPPADDING', (0, 0), (-1, -1), 4),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
                ('FONTSIZE', (0, 0), (-1, -1), 7),
            ]))
            story.append(KeepTogether([ofat_table]))
            story.append(Spacer(1, 5))
        
        if doe:
            story.append(Paragraph("<b>DOE (2³ Full Factorial):</b>", h2_style))
            story.append(Paragraph(
                f"<b>Factor A:</b> {doe[2]} (Low: {doe[5]}, High: {doe[6]})  |  "
                f"<b>Factor B:</b> {doe[3]} (Low: {doe[7]}, High: {doe[8]})  |  "
                f"<b>Factor C:</b> {doe[4]} (Low: {doe[9]}, High: {doe[10]})",
                body_style
            ))
            story.append(Paragraph(
                f"<b>Effect A:</b> {doe[19]}  |  <b>Effect B:</b> {doe[20]}  |  <b>Effect C:</b> {doe[21]}  |  "
                f"<b>Dominant Factor:</b> {doe[22]}",
                body_style
            ))
            story.append(Spacer(1, 5))
            
            doe_runs = [
                [Paragraph("Run", table_header_style),
                 Paragraph("A", table_header_style),
                 Paragraph("B", table_header_style),
                 Paragraph("C", table_header_style),
                 Paragraph("Response", table_header_style)]
            ]
            run_levels = [
                ("-", "-", "-"),
                ("+", "-", "-"),
                ("-", "+", "-"),
                ("+", "+", "-"),
                ("-", "-", "+"),
                ("+", "-", "+"),
                ("-", "+", "+"),
                ("+", "+", "+")
            ]
            for i, (a, b, c) in enumerate(run_levels):
                response = doe[11 + i] if len(doe) > 11 + i else "N/A"
                doe_runs.append([
                    Paragraph(str(i+1), table_body_style),
                    Paragraph(a, table_body_style),
                    Paragraph(b, table_body_style),
                    Paragraph(c, table_body_style),
                    Paragraph(str(response), table_body_style)
                ])
            doe_table = Table(doe_runs, colWidths=[0.8*inch, 0.8*inch, 0.8*inch, 0.8*inch, 1.5*inch])
            doe_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#1E3A8A")),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor("#F8FAFC")]),
                ('TOPPADDING', (0, 0), (-1, -1), 4),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
                ('FONTSIZE', (0, 0), (-1, -1), 7),
            ]))
            story.append(KeepTogether([doe_table]))
        story.append(Spacer(1, 10))

    # 6. Related Substances
    if impurities:
        story.append(Paragraph("6. RELATED SUBSTANCES", h1_style))
        rs_data = [
            [Paragraph("Impurity", table_header_style),
             Paragraph("Spec Limit (%)", table_header_style),
             Paragraph("Use RRF", table_header_style),
             Paragraph("RRF Value", table_header_style)]
        ]
        for imp in impurities:
            imp_id, name, spec_limit, use_rrf, rrf_value = imp
            rs_data.append([
                Paragraph(name, table_body_style),
                Paragraph(str(spec_limit), table_body_style),
                Paragraph("Yes" if use_rrf else "No", table_body_style),
                Paragraph(str(rrf_value), table_body_style)
            ])
        rs_table = Table(rs_data, colWidths=[2.5*inch, 1.5*inch, 1.5*inch, 1.5*inch])
        rs_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#1E3A8A")),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor("#F8FAFC")]),
            ('TOPPADDING', (0, 0), (-1, -1), 5),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ]))
        story.append(KeepTogether([rs_table]))

    # ============================================
    # SUMMARY TABLE
    # ============================================
    story.append(PageBreak())
    story.append(Paragraph("7. VALIDATION SUMMARY", h1_style))
    
    summary_data = [
        [Paragraph("Module", table_header_style),
         Paragraph("Status", table_header_style),
         Paragraph("Comments", table_header_style)]
    ]
    
    if summary:
        modules = [
            ("Specificity", summary.get("specificity_status", "PENDING")),
            ("Linearity", summary.get("linearity_status", "PENDING")),
            ("Accuracy", summary.get("accuracy_status", "PENDING")),
            ("Precision", summary.get("precision_status", "PENDING")),
            ("Robustness", summary.get("robustness_status", "PENDING")),
            ("Related Substances", summary.get("rel_sub_status", "PENDING")),
        ]
        for name, status in modules:
            color = "green" if status == "PASS" else "red" if status == "FAIL" else "gray"
            comments = {
                "PASS": "✓ All acceptance criteria met",
                "FAIL": "✗ One or more criteria failed",
                "PENDING": "⏳ Data not yet available"
            }.get(status, "")
            summary_data.append([
                Paragraph(name, table_body_style),
                Paragraph(f"<font color='{color}'><b>{status}</b></font>", table_body_style),
                Paragraph(comments, table_body_style)
            ])
    
    summary_table = Table(summary_data, colWidths=[2.0*inch, 1.5*inch, 3.5*inch])
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#1E3A8A")),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor("#F8FAFC")]),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(KeepTogether([summary_table]))
    
    if summary:
        overall = summary.get("overall_status", "PENDING")
        color = "#10B981" if overall == "PASS" else "#EF4444" if overall == "FAIL" else "#F59E0B"
        story.append(Spacer(1, 10))
        story.append(Paragraph(
            f"<b>OVERALL VALIDATION STATUS: <font color='{color}'>{overall}</font></b>",
            h1_style
        ))

    # Build the document
    doc.build(story, canvasmaker=NumberedCanvas)