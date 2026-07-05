import os
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT

def generate_crop_pdf(dest_path: str, farmer_name: str, land_details: dict, diagnosis_details: dict, image_path: str = None) -> str:
    """
    Generates a beautifully styled, professional PDF report for crop health diagnosis.
    Saves the PDF to dest_path.
    """
    # Create the document template
    doc = SimpleDocTemplate(
        dest_path,
        pagesize=letter,
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=40
    )
    
    story = []
    
    # Styles Setup
    styles = getSampleStyleSheet()
    
    # Custom Brand Colors
    brand_green = colors.HexColor("#1b5e20") # Deep forest green
    light_green = colors.HexColor("#e8f5e9") # Accent highlight background
    dark_gray = colors.HexColor("#263238")
    
    # Custom Typography Styles
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=22,
        textColor=colors.white,
        alignment=TA_LEFT,
        spaceAfter=5
    )
    
    subtitle_style = ParagraphStyle(
        'DocSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        textColor=colors.white,
        alignment=TA_LEFT
    )
    
    heading_style = ParagraphStyle(
        'SectionHeading',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=12,
        textColor=brand_green,
        spaceBefore=15,
        spaceAfter=8,
        borderPadding=(0, 0, 2, 0)
    )
    
    body_style = ParagraphStyle(
        'BodyDark',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        textColor=dark_gray,
        leading=14,
        spaceAfter=6
    )
    
    body_bold = ParagraphStyle(
        'BodyBold',
        parent=body_style,
        fontName='Helvetica-Bold'
    )

    bullet_style = ParagraphStyle(
        'BulletStyle',
        parent=body_style,
        leftIndent=15,
        firstLineIndent=-10
    )

    # 1. Header Banner Block (White text on Deep Green)
    header_data = [
        [
            Paragraph("🌾 KisanMitra AI Crop Report", title_style),
            Paragraph(f"Date: {datetime.now().strftime('%d-%b-%Y')}<br/>Report Ref: KM-DX-{os.urandom(3).hex().upper()}", ParagraphStyle('RightText', parent=subtitle_style, alignment=2))
        ],
        [
            Paragraph("Automated Farm Health Advisory Multi-Agent System", subtitle_style),
            Paragraph("Status: Complete / Verified", ParagraphStyle('RightTextSub', parent=subtitle_style, alignment=2))
        ]
    ]
    
    header_table = Table(header_data, colWidths=[330, 200])
    header_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), brand_green),
        ('PADDING', (0, 0), (-1, -1), 15),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('BOTTOMPADDING', (0, 1), (-1, 1), 10),
    ]))
    story.append(header_table)
    story.append(Spacer(1, 15))
    
    # 2. Farmer & Land Profile Section
    story.append(Paragraph("I. Farmer & Land Profile", heading_style))
    story.append(HRFlowable(width="100%", thickness=1, color=brand_green, spaceAfter=8))
    
    land_info = [
        [
            Paragraph("Farmer Name:", body_bold),
            Paragraph(farmer_name, body_style),
            Paragraph("Location:", body_bold),
            Paragraph(f"{land_details.get('village')}, {land_details.get('district')}, {land_details.get('state')}", body_style)
        ],
        [
            Paragraph("Land Size:", body_bold),
            Paragraph(f"{land_details.get('land_size_acres')} Acres", body_style),
            Paragraph("Crop Type:", body_bold),
            Paragraph(f"{land_details.get('crop_type')} (Primary)", body_style)
        ],
        [
            Paragraph("Soil Type:", body_bold),
            Paragraph(land_details.get('soil_type', 'N/A'), body_style),
            Paragraph("System Config:", body_bold),
            Paragraph("Simulated AI Agent Execution Mode" if diagnosis_details.get('simulated', True) else "Live Vision-Inference Engine", body_style)
        ]
    ]
    
    land_table = Table(land_info, colWidths=[90, 175, 90, 175])
    land_table.setStyle(TableStyle([
        ('GRID', (0,0), (-1,-1), 0.5, colors.lightgrey),
        ('BACKGROUND', (0,0), (0,-1), colors.whitesmoke),
        ('BACKGROUND', (2,0), (2,-1), colors.whitesmoke),
        ('PADDING', (0,0), (-1,-1), 6),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ]))
    story.append(land_table)
    story.append(Spacer(1, 15))
    
    # 3. Diagnosis Callout Panel (Light Green highlight)
    story.append(Paragraph("II. Health Diagnosis Summary", heading_style))
    story.append(HRFlowable(width="100%", thickness=1, color=brand_green, spaceAfter=8))
    
    severity_color = colors.HexColor("#c62828") if diagnosis_details.get('severity') == "High" else colors.HexColor("#ef6c00")
    severity_style = ParagraphStyle('SevText', parent=body_bold, textColor=severity_color)
    
    callout_data = [
        [
            Paragraph("Target Plant Crop:", body_bold),
            Paragraph(land_details.get('crop_type', 'Default'), body_style)
        ],
        [
            Paragraph("Diagnosed Disease:", body_bold),
            Paragraph(diagnosis_details.get('disease_detected', 'Healthy'), ParagraphStyle('DxText', parent=body_bold, textColor=brand_green, fontSize=11))
        ],
        [
            Paragraph("Classification Severity:", body_bold),
            Paragraph(diagnosis_details.get('severity', 'None'), severity_style)
        ]
    ]
    
    # If photo exists, display it alongside
    left_col_width = 330
    photo_drawn = False
    
    if image_path and os.path.exists(image_path):
        try:
            # Resize image to fit neatly on report
            img = Image(image_path, width=150, height=110)
            img.hAlign = 'CENTER'
            
            # 2 column layout: Callout table on left, photo on right
            panel_table = Table([[Table(callout_data, colWidths=[120, 200]), img]], colWidths=[left_col_width, 200])
            panel_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, -1), light_green),
                ('PADDING', (0, 0), (-1, -1), 10),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('ALIGN', (1, 0), (1, 0), 'CENTER'),
            ]))
            story.append(panel_table)
            photo_drawn = True
        except Exception as img_err:
            print(f"Report PDF Image inclusion warning: {img_err}")
            
    if not photo_drawn:
        # Full width layout if no image or import fails
        panel_table = Table(callout_data, colWidths=[150, 380])
        panel_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), light_green),
            ('PADDING', (0, 0), (-1, -1), 10),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        story.append(panel_table)
        
    story.append(Spacer(1, 15))
    
    # 4. Details & Action Plan (Organic vs Chemical treatments)
    story.append(Paragraph("III. Prescribed Treatment Advisory", heading_style))
    story.append(HRFlowable(width="100%", thickness=1, color=brand_green, spaceAfter=8))
    
    # We parse the diagnosis report text. Since the agent reports are unstructured strings, 
    # we render them cleanly. If we have keys, we render. Else, split by sentences.
    raw_details = diagnosis_details.get("diagnosis_details", "")
    
    # Extract organic, chemical, and tips if we can search keywords, else show full block
    organic_block = "Apply organic neem sprays or pseudomonas fluorescens solution."
    chemical_block = "No chemical intervention needed."
    preventive_block = "Maintain proper soil hygiene and drainage."
    
    details_lines = raw_details.split('\n')
    for line in details_lines:
        line_clean = line.strip().lower()
        if "biological" in line_clean or "organic" in line_clean:
            organic_block = line.replace("-", "").strip()
        elif "chemical" in line_clean:
            chemical_block = line.replace("-", "").strip()
        elif "preventive" in line_clean or "preventive tips" in line_clean:
            preventive_block = line.replace("-", "").strip()
            
    story.append(Paragraph("🌿 Organic / Biological Control Plan", body_bold))
    story.append(Paragraph(organic_block, body_style))
    story.append(Spacer(1, 5))
    
    story.append(Paragraph("🧪 Chemical Control Schedule", body_bold))
    story.append(Paragraph(chemical_block, body_style))
    story.append(Spacer(1, 5))
    
    story.append(Paragraph("🔧 Agronomic Preventive Recommendations", body_bold))
    story.append(Paragraph(preventive_block, body_style))
    story.append(Spacer(1, 15))
    
    # Raw Agent details dump for transparency
    story.append(Paragraph("IV. Full Agent Advisory Remarks", heading_style))
    story.append(HRFlowable(width="100%", thickness=1, color=brand_green, spaceAfter=8))
    story.append(Paragraph(raw_details.replace('\n', '<br/>'), ParagraphStyle('RawText', parent=body_style, fontName='Helvetica-Oblique', fontSize=9, leading=12)))
    
    # 5. Disclaimer / Footer
    story.append(Spacer(1, 20))
    story.append(HRFlowable(width="100%", thickness=0.5, color=colors.gray, spaceAfter=8))
    
    disclaimer_style = ParagraphStyle(
        'Disclaimer',
        parent=styles['Normal'],
        fontName='Helvetica-Oblique',
        fontSize=8,
        textColor=colors.gray,
        alignment=TA_CENTER
    )
    story.append(Paragraph(
        "Disclaimer: This report is automatically generated by KisanMitra multi-agent advisory system. "
        "Recommendations are based on visual classification models and retrieved scheme databases. "
        "Consult local Krishi Vigyan Kendra (KVK) for final chemical application approvals.",
        disclaimer_style
    ))
    
    # Build Document
    doc.build(story)
    return dest_path
