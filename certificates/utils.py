import io
from django.utils import timezone
from django.conf import settings
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image as RLImage
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch

def generate_verification_pdf(cert):
    """Generates a professional PDF verification report in memory and returns a BytesIO buffer."""
    buffer = io.BytesIO()
    
    # Setup document
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=40
    )
    
    story = []
    styles = getSampleStyleSheet()
    
    # Custom Styles
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=24,
        leading=28,
        textColor=colors.HexColor('#0f172a'),
        alignment=1, # Center
        spaceAfter=15
    )
    
    subtitle_style = ParagraphStyle(
        'DocSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        leading=14,
        textColor=colors.HexColor('#64748b'),
        alignment=1, # Center
        spaceAfter=25
    )
    
    section_heading = ParagraphStyle(
        'SectionHeading',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=14,
        leading=18,
        textColor=colors.HexColor('#1e293b'),
        spaceBefore=15,
        spaceAfter=10,
        keepWithNext=True
    )
    
    label_style = ParagraphStyle(
        'LabelStyle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=10,
        leading=14,
        textColor=colors.HexColor('#334155')
    )
    
    value_style = ParagraphStyle(
        'ValueStyle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        leading=14,
        textColor=colors.HexColor('#0f172a')
    )
    
    # Report Header
    story.append(Paragraph("SMART CERTIFICATE PORTAL", title_style))
    story.append(Paragraph(f"Official Verification Report &bull; Generated on {timezone.now().strftime('%Y-%m-%d %H:%M:%S UTC')}", subtitle_style))
    
    # Status Banner Table
    status_text = f"STATUS: {cert.get_status_display().upper()}"
    status_bg = '#10b981' if cert.status == 'APPROVED' else '#ef4444'
    if cert.status == 'PENDING':
        status_bg = '#f59e0b'
    
    status_table_data = [[
        Paragraph(f"<b>{status_text}</b>", ParagraphStyle('StatusStyle', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=12, leading=16, textColor=colors.white, alignment=1))
    ]]
    
    status_table = Table(status_table_data, colWidths=[7.2*inch])
    status_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor(status_bg)),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 8),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
    ]))
    
    story.append(status_table)
    story.append(Spacer(1, 20))
    
    # Certificate Info Table
    story.append(Paragraph("Certificate Details", section_heading))
    
    details_data = [
        [Paragraph("Certificate Number:", label_style), Paragraph(cert.certificate_number, value_style),
         Paragraph("Register Number:", label_style), Paragraph(cert.student.register_number, value_style)],
        
        [Paragraph("Student Name:", label_style), Paragraph(cert.student_name_snapshot, value_style),
         Paragraph("Grade / CGPA:", label_style), Paragraph(f"{cert.grade} / {cert.cgpa}", value_style)],
         
        [Paragraph("Course Name:", label_style), Paragraph(cert.course.name, value_style),
         Paragraph("Department:", label_style), Paragraph(cert.department.name, value_style)],
         
        [Paragraph("College:", label_style), Paragraph(cert.student.college_name, value_style),
         Paragraph("University:", label_style), Paragraph(cert.student.university_name, value_style)],
         
        [Paragraph("Semester:", label_style), Paragraph(cert.semester, value_style),
         Paragraph("Issue Date:", label_style), Paragraph(cert.issue_date.strftime('%Y-%m-%d'), value_style)],
    ]
    
    details_table = Table(details_data, colWidths=[1.8*inch, 1.8*inch, 1.8*inch, 1.8*inch])
    details_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#f8fafc')),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#e2e8f0')),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
        ('RIGHTPADDING', (0,0), (-1,-1), 8),
    ]))
    
    story.append(details_table)
    story.append(Spacer(1, 20))
    
    # Security and Verification Metadata
    story.append(Paragraph("Security & Verification Signature", section_heading))
    
    # Check for QR code path
    qr_element = Paragraph("No QR Code generated", value_style)
    if cert.qr_code_image:
        try:
            qr_element = RLImage(cert.qr_code_image.path, width=1.2*inch, height=1.2*inch)
        except Exception:
            pass # Keep text if loading file fails
            
    security_data = [
        [
            Paragraph(
                f"<b>Digital Signature Hash:</b><br/>{cert.digital_signature}<br/><br/>"
                f"<b>Verification Date:</b><br/>{cert.verification_date.strftime('%Y-%m-%d %H:%M:%S UTC') if cert.verification_date else 'Not Verified'}<br/><br/>"
                f"<i>This document is a computer-generated verification report pulled from the live verification system registry. "
                f"The cryptographic signature confirms the certificate records match the database. Scan the QR code to verify live status.</i>", 
                value_style
            ),
            qr_element
        ]
    ]
    
    security_table = Table(security_data, colWidths=[5.6*inch, 1.6*inch])
    security_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#f1f5f9')),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#cbd5e1')),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 10),
        ('BOTTOMPADDING', (0,0), (-1,-1), 10),
        ('LEFTPADDING', (0,0), (-1,-1), 10),
        ('RIGHTPADDING', (0,0), (-1,-1), 10),
    ]))
    
    story.append(security_table)
    
    # Build Document
    doc.build(story)
    buffer.seek(0)
    return buffer
