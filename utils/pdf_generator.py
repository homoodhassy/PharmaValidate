"""
PharmaValidate v0.5 - GMP Compliant PDF Generation Utility
Compiles comprehensive, versatile analytical validation protocols based on physical lab specimens.
Supports Assay, Dissolution, and Related Substances (RS) dynamic testing procedures.
"""

from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfgen import canvas

class NumberedCanvas(canvas.Canvas):
    """Canvas subclass to dynamically calculate and draw running headers and footers."""
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
        
        # Suppress headers and footers on the cover page (Page 1)
        if self._pageNumber > 1:
            # Draw running header on all subsequent pages
            self.drawString(54, 750, "ANALYTICAL METHOD VALIDATION PROTOCOL")
            self.setStrokeColor(colors.HexColor("#CBD5E1"))
            self.setLineWidth(0.5)
            self.line(54, 742, 558, 742)
            
            # Draw footer
            self.line(54, 55, 558, 55)
            page_text = f"Page {self._pageNumber} of {page_count}"
            self.drawRightString(558, 40, page_text)
            self.drawString(54, 40, "CONFIDENTIAL - PHARMAVALIDATE QUALITY ASSURANCE SYSTEM")
            
        self.restoreState()


def generate_assay_pdf(output_path, project_details, survey_data):
    """Generates a complete, versatile protocol PDF with custom test methodologies and math models."""
    _, name, product, method, val_type, protocol, analyst = project_details
    company_name = survey_data.get("company_name", "Analytical Laboratory Services")
    study_type = survey_data.get("study_type", "Validation")
    test_type = survey_data.get("test_type", "Assay")
    
    current_date = datetime.now().strftime("%B %d, %Y")

    # Document setup (0.75 in/54pt margins, 72pt top/bottom)
    doc = SimpleDocTemplate(
        output_path,
        pagesize=letter,
        leftMargin=54,
        rightMargin=54,
        topMargin=72,
        bottomMargin=72
    )

    styles = getSampleStyleSheet()
    
    # Custom Typography Styles
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
        fontName='Helvetica-Bold', fontSize=12, leading=16,
        textColor=colors.HexColor("#0F172A"), spaceBefore=14, spaceAfter=8,
        keepWithNext=True
    )
    body_style = ParagraphStyle(
        'BodyText', parent=styles['Normal'],
        fontName='Helvetica', fontSize=9.5, leading=14,
        textColor=colors.HexColor("#334155"), spaceAfter=8
    )
    formula_style = ParagraphStyle(
        'FormulaText', parent=styles['Normal'],
        fontName='Courier-Oblique', fontSize=10, leading=14,
        textColor=colors.HexColor("#1E293B"), leftIndent=25, spaceBefore=8, spaceAfter=8
    )
    table_header_style = ParagraphStyle(
        'TableHeader', parent=styles['Normal'],
        fontName='Helvetica-Bold', fontSize=8.5, leading=10, textColor=colors.white
    )
    table_body_style = ParagraphStyle(
        'TableBody', parent=styles['Normal'],
        fontName='Helvetica', fontSize=8.5, leading=11, textColor=colors.HexColor("#334155")
    )

    story = []

    # -------------------------------------------------------------------------
    # COVER PAGE
    # -------------------------------------------------------------------------
    story.append(Spacer(1, 10))
    
    # Elegant Top Color Block (Width aligned to margins: 7.0 inches)
    accent_bar = Table([[""]], colWidths=[7.0*inch], rowHeights=[4])
    accent_bar.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#1E3A8A")),
        ('TOPPADDING', (0, 0), (-1, -1), 0),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
    ]))
    story.append(accent_bar)
    story.append(Spacer(1, 15))
    
    story.append(Paragraph(f"🏢 {company_name.upper()}", subtitle_style))
    story.append(Paragraph("ANALYTICAL METHOD VALIDATION PROTOCOL", title_style))
    story.append(Paragraph(f"METHOD STUDY: {study_type.upper()} FOR {product.upper()} ({test_type.upper()}) BY {method.upper()}", subtitle_style))
    story.append(Spacer(1, 10))

    # Protocol Metadata Table (Total Width: 7.0 inches)
    meta_data = [
        [Paragraph("<b>Target Product:</b>", body_style), Paragraph(product, body_style)],
        [Paragraph("<b>Testing Category:</b>", body_style), Paragraph(test_type, body_style)],
        [Paragraph("<b>Method Technique:</b>", body_style), Paragraph(method, body_style)],
        [Paragraph("<b>Protocol ID Ref:</b>", body_style), Paragraph(protocol, body_style)],
        [Paragraph("<b>Responsible Analyst:</b>", body_style), Paragraph(analyst, body_style)],
        [Paragraph("<b>Date Generated:</b>", body_style), Paragraph(current_date, body_style)],
    ]
    meta_table = Table(meta_data, colWidths=[2.2*inch, 4.8*inch])
    meta_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('LINEBELOW', (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(meta_table)
    story.append(Spacer(1, 30))

    # Approval Sign-off Table (Total Width: 7.0 inches)
    story.append(Paragraph("<b>REPORT APPROVAL SIGN-OFF</b>", h1_style))
    story.append(Spacer(1, 5))
    
    sig_data = [
        [Paragraph("Designation", table_header_style), Paragraph("Name", table_header_style), Paragraph("Signature / Date", table_header_style)],
        [Paragraph("<b>Prepared By:</b><br/>QC Analyst", table_body_style), Paragraph(analyst, table_body_style), Paragraph("<br/><br/>___________________________", table_body_style)],
        [Paragraph("<b>Reviewed By:</b><br/>QC Lab Supervisor", table_body_style), Paragraph("<br/><br/>___________________________", table_body_style), Paragraph("<br/><br/>___________________________", table_body_style)],
        [Paragraph("<b>Approved By:</b><br/>Quality Assurance Manager", table_body_style), Paragraph("<br/><br/>___________________________", table_body_style), Paragraph("<br/><br/>___________________________", table_body_style)],
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

    # -------------------------------------------------------------------------
    # MAIN PROTOCOL BODY
    # -------------------------------------------------------------------------
    
    # 1.0 Purpose
    story.append(Paragraph("1.0 PURPOSE", h1_style))
    story.append(Paragraph(
        f"To establish documentary evidence through target test parameters defined in this protocol "
        f"to demonstrate that the analytical procedure for the determination of {test_type.lower()} content will yield consistent, "
        f"reliable, and reproducible results meeting pre-determined laboratory quality specifications.",
        body_style
    ))

    # 2.0 Scope
    story.append(Paragraph("2.0 SCOPE", h1_style))
    story.append(Paragraph(
        f"The scope of this protocol provides specific experimental guidance to conduct performance test studies "
        f"for the {study_type} of the {method} method used for measuring <b>{product}</b> ({test_type.lower()}).",
        body_style
    ))

    # 3.0 Responsibility
    story.append(Paragraph("3.0 RESPONSIBILITY", h1_style))
    story.append(Paragraph(
        "<b>Quality Control Analyst:</b> Responsible for executing the physical analytical tests, "
        "preparing solutions accurately, and strictly following the procedure described in this protocol.<br/>"
        "<b>QC Supervisor/Manager:</b> Responsible for overseeing experimental executions, reviewing raw instrument output data, and compiling findings.<br/>"
        "<b>QA Manager:</b> Responsible for evaluating, authorization signing, and enforcing strict compliance to GMP guidelines throughout the lifecycle of the study.",
        body_style
    ))

    # 4.0 Prerequisites
    story.append(Paragraph("4.0 PREREQUISITES", h1_style))
    story.append(Paragraph(
        f"Prior to initiating testing, all HPLC instruments/analytical equipment must be in a calibrated state. "
        f"The primary QC Analyst must be fully trained in safety SOPs and chromatographic techniques. "
        f"Standard operating limits for Active Pharmaceutical Ingredient (API) nominal recovery range is set as defined in this document.",
        body_style
    ))

    # 5.0 Methodology
    story.append(Paragraph("5.0 METHODOLOGY & PREPARATIONS", h1_style))
    
    std_prep = survey_data.get("std_prep", "Accurately weigh reference standard and dilute to mark.")
    sample_prep = survey_data.get("sample_prep", "Weigh and powder composite sample, dilute and filter.")
    
    story.append(Paragraph("<b>5.1 Preparation of Reference Standard Solution:</b>", body_style))
    story.append(Paragraph(std_prep, body_style))
    
    story.append(Paragraph("<b>5.2 Preparation of Target Sample Solution:</b>", body_style))
    story.append(Paragraph(sample_prep, body_style))

    # Dynamic HPLC Chromatographic Conditions Table (Total Width: 7.0 inches)
    if survey_data.get("is_hplc", False):
        hplc_header = Paragraph("<b>5.3 Chromatographic Operating Conditions (HPLC):</b>", body_style)
        hplc_data = [
            [Paragraph("Chromatographic Variable", table_header_style), Paragraph("Approved Protocol Parameter Setup", table_header_style)],
            [Paragraph("<b>Analytical Column:</b>", table_body_style), Paragraph(survey_data.get("hplc_column", "C18 Column"), table_body_style)],
            [Paragraph("<b>Isocratic/Gradient Mode:</b>", table_body_style), Paragraph(survey_data.get("hplc_mode", "Isocratic"), table_body_style)],
            [Paragraph("<b>Flow Rate Limit:</b>", table_body_style), Paragraph(survey_data.get("hplc_flow", "1.0 mL/min"), table_body_style)],
            [Paragraph("<b>Column Temperature:</b>", table_body_style), Paragraph(survey_data.get("hplc_temp", "30 °C"), table_body_style)],
            [Paragraph("<b>Detection Wavelength:</b>", table_body_style), Paragraph(survey_data.get("hplc_wavelength", "228 nm"), table_body_style)],
            [Paragraph("<b>Injection Volume:</b>", table_body_style), Paragraph(survey_data.get("hplc_inj_vol", "20 µL"), table_body_style)],
            [Paragraph("<b>Mobile Phase Composition:</b>", table_body_style), Paragraph(survey_data.get("hplc_mobile", "Water : Methanol"), table_body_style)]
        ]
        hplc_table = Table(hplc_data, colWidths=[2.5*inch, 4.5*inch])
        hplc_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#475569")),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor("#F8FAFC")]),
            ('TOPPADDING', (0, 0), (-1, -1), 5),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ]))
        # Keep table bound with its subheader
        story.append(KeepTogether([hplc_header, Spacer(1, 4), hplc_table]))
        story.append(Spacer(1, 10))

    # -------------------------------------------------------------------------
    # 5.4 ROBUSTNESS SECTION - EXPLANATORY CONTENT (NO HARDCODED VALUES)
    # -------------------------------------------------------------------------
    robustness_type = survey_data.get("robustness_type")
    include_robustness_table = survey_data.get("robustness_include_table", False)
    limit_rsd = survey_data.get("limit_rsd", "2.0%")
    limit_tailing = survey_data.get("limit_tailing", "2.0")
    
    if robustness_type:
        story.append(Paragraph("<b>5.4 Robustness Experimental Design</b>", h1_style))
        
        # Determine robustness method type
        is_ofat = "OFAT" in robustness_type and "Both" not in robustness_type
        is_doe = "Full Factorial" in robustness_type
        is_both = "Both" in robustness_type
        
        # Build EXPLANATORY description - NO HARDCODED VALUES
        if is_ofat:
            robustness_desc = (
                "The OFAT (One Factor at a Time) approach evaluates robustness by varying one chromatographic parameter "
                "at a time while keeping all other conditions constant. For each selected parameter, the analyst will: "
                "1) Define a nominal (target) value, 2) Establish low and high variation limits (e.g., ±5% or ±2 units), "
                "3) Perform replicate analyses (n=3) at each level, 4) Compare system suitability parameters against "
                "acceptance criteria at both extremes. This identifies which individual parameters have the greatest "
                "impact on method performance."
            )
            robustness_method = "OFAT (One Factor at a Time)"
        elif is_doe:
            robustness_desc = (
                "The DOE (Design of Experiments) approach uses a Partial Factorial design to simultaneously evaluate "
                "multiple parameters and their interactions. The analyst will: 1) Select 3-4 critical parameters, "
                "2) Define low (-1) and high (+1) levels for each, 3) Execute a fractional factorial design matrix "
                "(e.g., 2^(k-1) runs where k = number of factors), 4) Analyze results and calculate: "
                "Main effects (individual parameter impact), Two-way interactions (combined parameter effects)."
            )
            robustness_method = "Partial Factorial DOE"
        elif is_both:
            robustness_desc = (
                "This combined approach provides comprehensive robustness characterization in two phases: "
                "PHASE 1 - OFAT Screening: Each parameter is varied individually (n=3 replicates per level) to "
                "identify sensitive parameters. PHASE 2 - DOE Analysis: A Partial Factorial design is applied to "
                "the identified critical parameters to quantify main effects, interaction effects, and statistical. "
                "This dual approach ensures both individual sensitivity and "
                "combined interaction effects are thoroughly evaluated."
            )
            robustness_method = "OFAT + Partial Factorial DOE"
        else:
            robustness_desc = "Robustness evaluation will be performed according to ICH Q2(R1) guidelines."
            robustness_method = "Standard Approach"
        
        story.append(Paragraph(f"<b>Selected Evaluation Model:</b> {robustness_method}", body_style))
        story.append(Spacer(1, 4))
        story.append(Paragraph(robustness_desc, body_style))
        story.append(Spacer(1, 6))
        
        # Add EXPLANATORY parameters table if requested - NO HARDCODED VALUES
        if include_robustness_table:
            # OFAT EXPLANATORY TABLE
            if is_ofat or is_both:
                story.append(Paragraph("<b>OFAT Experimental Design Guide:</b>", body_style))
                story.append(Paragraph(
                    "For each parameter below, perform independent experiments at the defined levels while keeping all other parameters at nominal values. "
                    f"Record system suitability parameters (RSD, tailing, resolution) at each level to determine sensitivity.",
                    body_style
                ))
                
                # Get current values from survey data
                current_flow = survey_data.get("hplc_flow", "1.0 mL/min")
                current_temp = survey_data.get("hplc_temp", "30 °C")
                current_mobile = survey_data.get("hplc_mobile", "Buffer : Methanol")
                current_wavelength = survey_data.get("hplc_wavelength", "228 nm")
                
                ofat_data = [
                    [Paragraph("Parameter", table_header_style), 
                     Paragraph("Nominal Value", table_header_style),
                     Paragraph("Low Level", table_header_style),
                     Paragraph("High Level", table_header_style)],
                    [Paragraph("<b>Mobile Phase Ratio</b>", table_body_style),
                     Paragraph(current_mobile, table_body_style),
                     Paragraph("Nominal - 5% (adjust composition)", table_body_style),
                     Paragraph("Nominal + 5% (adjust composition)", table_body_style)],
                    [Paragraph("<b>Flow Rate</b>", table_body_style),
                     Paragraph(current_flow, table_body_style),
                     Paragraph("Nominal - 0.2 mL/min", table_body_style),
                     Paragraph("Nominal + 0.2 mL/min", table_body_style)],
                    [Paragraph("<b>Column Temperature</b>", table_body_style),
                     Paragraph(current_temp, table_body_style),
                     Paragraph("Nominal - 2°C", table_body_style),
                     Paragraph("Nominal + 2°C", table_body_style)],
                    [Paragraph("<b>Detection Wavelength</b>", table_body_style),
                     Paragraph(current_wavelength, table_body_style),
                     Paragraph("Nominal - 2 nm", table_body_style),
                     Paragraph("Nominal + 2 nm", table_body_style)],
                ]
                
                ofat_table = Table(ofat_data, colWidths=[1.8*inch, 1.5*inch, 1.8*inch, 1.9*inch])
                ofat_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#1E3A8A")),
                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                    ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                    ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
                    ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor("#F8FAFC")]),
                    ('TOPPADDING', (0, 0), (-1, -1), 6),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                ]))
                story.append(KeepTogether([ofat_table]))
                story.append(Spacer(1, 4))
                
                story.append(Paragraph(
                    f"<i>Evaluation: At each level, verify that system suitability criteria (RSD ≤ {limit_rsd}, "
                    f"Tailing ≤ {limit_tailing}) are met. Document any significant changes in performance.</i>",
                    body_style
                ))
                story.append(Spacer(1, 6))
            
            # DOE EXPLANATORY TABLE
            if is_doe or is_both:
                if is_both:
                    story.append(Paragraph("<b>DOE Experimental Design Guide:</b>", body_style))
                else:
                    story.append(Paragraph("<b>DOE Partial Factorial Design Guide:</b>", body_style))
                
                story.append(Paragraph(
                    "Execute a 2^(k-1) fractional factorial design where k = number of factors. Analyze results and identify the effects.",
                    body_style
                ))
                
                doe_data = [
                    [Paragraph("Factor", table_header_style), 
                     Paragraph("Low Level (-1)", table_header_style),
                     Paragraph("High Level (+1)", table_header_style),
                     Paragraph("Analysis Goal", table_header_style)],
                    [Paragraph("<b>Factor A: Mobile Phase</b>", table_body_style),
                     Paragraph("Nominal - 5%", table_body_style),
                     Paragraph("Nominal + 5%", table_body_style),
                     Paragraph("Calculate main effect", table_body_style)],
                    [Paragraph("<b>Factor B: Flow Rate</b>", table_body_style),
                     Paragraph("Nominal - 0.2 mL/min", table_body_style),
                     Paragraph("Nominal + 0.2 mL/min", table_body_style),
                     Paragraph("Calculate main effect", table_body_style)],
                    [Paragraph("<b>Factor C: Temperature</b>", table_body_style),
                     Paragraph("Nominal - 2°C", table_body_style),
                     Paragraph("Nominal + 2°C", table_body_style),
                     Paragraph("Calculate main effect", table_body_style)],
                    [Paragraph("<b>Interaction AB</b>", table_body_style),
                     Paragraph("Combined effect", table_body_style),
                     Paragraph("of A and B", table_body_style),
                     Paragraph("Calculate interaction effect", table_body_style)],
                    [Paragraph("<b>Interaction AC</b>", table_body_style),
                     Paragraph("Combined effect", table_body_style),
                     Paragraph("of A and C", table_body_style),
                     Paragraph("Calculate interaction effect", table_body_style)],
                    [Paragraph("<b>Interaction BC</b>", table_body_style),
                     Paragraph("Combined effect", table_body_style),
                     Paragraph("of B and C", table_body_style),
                     Paragraph("Calculate interaction effect", table_body_style)],
                ]
                
                doe_table = Table(doe_data, colWidths=[1.8*inch, 1.7*inch, 1.7*inch, 1.8*inch])
                doe_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#1E3A8A")),
                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                    ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                    ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
                    ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor("#F8FAFC")]),
                    ('TOPPADDING', (0, 0), (-1, -1), 6),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                ]))
                story.append(KeepTogether([doe_table]))
                story.append(Spacer(1, 4))
                
                story.append(Paragraph(
                    "<i>Statistical Analysis: Perform ANOVA to identify significant factors (p < 0.05). "
                    "Factors with p < 0.05 are considered statistically significant. Effect estimates indicate the magnitude of impact "
                    "on method performance (e.g., recovery %, retention time, peak area).</i>",
                    body_style
                ))
                story.append(Spacer(1, 6))
            
            if is_both:
                story.append(Paragraph(
                    "<i>Note: This combined approach provides comprehensive robustness characterization. "
                    "Use OFAT results to identify sensitive parameters, then apply DOE to these parameters "
                    "to quantify interactions and statistical significance for method optimization.</i>",
                    body_style
                ))
        
        story.append(Spacer(1, 10))

    # 6.0 Calculations
    story.append(Paragraph("6.0 CALCULATION FORMULAE", h1_style))
    story.append(Paragraph(
        f"The quantitative mathematical model to determine {test_type.lower()} content is represented as follows:",
        body_style
    ))
    
    formula_text = survey_data.get("formula_text", "")
    formula_defs = survey_data.get("formula_defs", "")
    
    story.append(Paragraph(f"<b>{formula_text}</b>", formula_style))
    story.append(Paragraph(formula_defs.replace("\n", "<br/>"), body_style))
    story.append(Spacer(1, 10))

    # 7.0 Validation Parameters & Criteria Table (Total Width: 7.0 inches)
    specs_header = Paragraph(f"<b>7.0 DETAILED {study_type.upper()} PROTOCOL SPECIFICATIONS</b>", h1_style)
    specs_intro = Paragraph(
        f"The following target parameters and criteria are established as thresholds. "
        f"Experimental output must comply with these metrics to qualify analytical suitability:",
        body_style
    )

    # Dynamic limits customized from UI survey
    limit_rsd = survey_data.get("limit_rsd", "2.0%")
    limit_tailing = survey_data.get("limit_tailing", "2.0")
    limit_recovery = survey_data.get("limit_recovery", "98.0% - 102.0%")

    # Intelligent GMP Adjustments depending on Test Type
    test_upper = test_type.upper()
    if "RS" in test_upper or "RELATED" in test_upper or "IMPURITY" in test_upper:
        rsd_val = "10.0% (at LOQ)"
        recovery_val = "80.0% - 120.0% (at trace validation limits)"
    elif "DISSOLUTION" in test_upper:
        rsd_val = "2.0% - 10.0% (profile dependent)"
        recovery_val = "95.0% - 105.0%"
    else:
        rsd_val = limit_rsd
        recovery_val = limit_recovery

    # Build robustness strategy text for parameter table - EXPLANATORY
    if robustness_type:
        if "OFAT" in robustness_type and "Both" not in robustness_type:
            robust_strategy = "Introduce minor changes to chromatographic variables using <b>OFAT</b> model design. Each parameter varied individually (n=3 replicates per condition) while maintaining all other parameters at nominal values."
        elif "Full Factorial" in robustness_type:
            robust_strategy = "Introduce minor changes using <b>Partial Factorial DOE</b> design (2-level, n=2 replicates per run). Multi-variable changes with analysis of main effects."
        elif "Both" in robustness_type:
            robust_strategy = "Introduce minor changes using <b>OFAT + DOE</b> dual approach: OFAT screening (n=3 per condition) followed by DOE analysis (2-level, n=2 replicates) for comprehensive characterization."
        else:
            robust_strategy = "Introduce minor changes to chromatographic variables using standard robustness approach."
    else:
        robust_strategy = "Introduce minor changes to chromatographic variables using standard robustness approach."

    PARAMETER_STRATEGIES = {
        "System Suitability": {
            "strategy": "Inject 5 or 6 replicate injections of working standard preparations.",
            "criteria": f"RSD of Peak Area ≤ {limit_rsd}<br/>Tailing factor (T) ≤ {limit_tailing}<br/>Theoretical plates (N) > 2000"
        },
        "Specificity": {
            "strategy": "Analyze blank diluents, inactive placebo matrix, and active standards to demonstrate no peak co-elution.",
            "criteria": "No target peak interference from blank, placebo, or excipients at retention time."
        },
        "LOD": {
            "strategy": "Inject decreasing concentration levels of analyte to establish detection thresholds.",
            "criteria": "Signal-to-Noise ratio (S/N) ≥ 3:1 with clear and identifiable peak response."
        },
        "LOQ": {
            "strategy": "Inject decreasing concentration levels of analyte to establish quantitation limits.",
            "criteria": f"Signal-to-Noise ratio (S/N) ≥ 10:1.<br/>Precision Area RSD (n=6) ≤ {rsd_val}."
        },
        "Linearity & Range": {
            "strategy": "Inject 5 coordinate standard concentrations ranging across expected target limits.",
            "criteria": "Correlation coefficient (r²) ≥ 0.999<br/>Y-intercept is statistically validated."
        },
        "Accuracy (Recovery)": {
            "strategy": "Complete triplicate recovery preparations spiked across target concentrations.",
            "criteria": f"Mean recovery must fall within {recovery_val}<br/>RSD across levels ≤ {limit_rsd}"
        },
        "Precision (Repeatability)": {
            "strategy": "Run 6 independent active preparations from a homogeneous product sample.",
            "criteria": f"Relative Standard Deviation (RSD) of Results ≤ {limit_rsd}"
        },
        "Intermediate Precision": {
            "strategy": "Evaluate target sample runs prepared by a second analyst on a separate day/column.",
            "criteria": f"Combined inter-analyst inter-day RSD (n=12) ≤ 3.0% (or meeting custom {limit_rsd} criteria)."
        },
        "Robustness": {
            "strategy": robust_strategy,
            "criteria": "System suitability parameters (RSD, tailing, resolution) remain within defined acceptance criteria under all modified test conditions. For DOE, effect estimates guide critical parameter identification."
        }
    }

    selected_params = survey_data.get("parameters", [])
    criteria_data = [
        [Paragraph("Target Parameter", table_header_style), Paragraph("Execution Strategy", table_header_style), Paragraph("Acceptance Criteria", table_header_style)]
    ]

    for p in selected_params:
        if p in PARAMETER_STRATEGIES:
            criteria_data.append([
                Paragraph(f"<b>{p}</b>", table_body_style),
                Paragraph(PARAMETER_STRATEGIES[p]["strategy"], table_body_style),
                Paragraph(PARAMETER_STRATEGIES[p]["criteria"], table_body_style)
            ])

    if len(criteria_data) == 1:
        criteria_data.append([
            Paragraph("N/A", table_body_style), 
            Paragraph("No parameters selected.", table_body_style), 
            Paragraph("N/A", table_body_style)
        ])

    criteria_table = Table(criteria_data, colWidths=[1.8*inch, 2.6*inch, 2.6*inch])
    criteria_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#1E3A8A")),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor("#F8FAFC")]),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    
    # Keep validation specs together so they don't break across pages poorly
    story.append(KeepTogether([specs_header, specs_intro, Spacer(1, 6), criteria_table]))

    # Build the document
    doc.build(story, canvasmaker=NumberedCanvas)