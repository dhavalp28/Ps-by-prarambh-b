import qrcode
from PIL import Image, ImageDraw, ImageFont
import io
import zipfile
from typing import List, Tuple
from datetime import datetime


def create_qr_code(data: str, size: int = 10, border: int = 2) -> Image.Image:
    """Create a QR code image"""
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=size,
        border=border,
    )
    qr.add_data(data)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    return img


def create_sticker_with_header(
    business_name: str,
    business_code: str,
    qr_image: Image.Image,
    sticker_size: Tuple[int, int] = (800, 1000),
    header_color: Tuple[int, int, int] = (76, 175, 80),  # Green #4CAF50
) -> Image.Image:
    """Create a sticker with header, QR code, and business code"""
    
    # Create white background
    sticker = Image.new('RGB', sticker_size, color='white')
    draw = ImageDraw.Draw(sticker)
    
    # Header section with green background
    header_height = 150
    draw.rectangle(
        [(0, 0), (sticker_size[0], header_height)],
        fill=header_color
    )
    
    # Add rounded corners effect to header (using a simple approach)
    # Draw header text
    try:
        # Try to use a larger font for the header
        title_font = ImageFont.truetype("arial.ttf", 36)
        subtitle_font = ImageFont.truetype("arial.ttf", 20)
    except:
        # Fallback to default font
        title_font = ImageFont.load_default()
        subtitle_font = ImageFont.load_default()
    
    # Draw "PS By Prarambh" title
    title_text = "PS By Prarambh"
    title_bbox = draw.textbbox((0, 0), title_text, font=title_font)
    title_width = title_bbox[2] - title_bbox[0]
    title_x = (sticker_size[0] - title_width) // 2
    draw.text((title_x, 30), title_text, fill='white', font=title_font)
    
    # Draw "Coupon Redemption" subtitle
    subtitle_text = "Coupon Redemption"
    subtitle_bbox = draw.textbbox((0, 0), subtitle_text, font=subtitle_font)
    subtitle_width = subtitle_bbox[2] - subtitle_bbox[0]
    subtitle_x = (sticker_size[0] - subtitle_width) // 2
    draw.text((subtitle_x, 85), subtitle_text, fill='white', font=subtitle_font)
    
    # Add business name
    try:
        business_font = ImageFont.truetype("arial.ttf", 28)
    except:
        business_font = ImageFont.load_default()
    
    business_bbox = draw.textbbox((0, 0), business_name, font=business_font)
    business_width = business_bbox[2] - business_bbox[0]
    business_x = (sticker_size[0] - business_width) // 2
    draw.text((business_x, 200), business_name, fill='black', font=business_font)
    
    # Add underline under business name
    underline_y = 250
    underline_width = 200
    underline_x = (sticker_size[0] - underline_width) // 2
    draw.rectangle(
        [(underline_x, underline_y), (underline_x + underline_width, underline_y + 3)],
        fill=header_color
    )
    
    # Resize QR code to fit
    qr_size = 350
    qr_resized = qr_image.resize((qr_size, qr_size), Image.Resampling.LANCZOS)
    
    # Add white border around QR code
    qr_with_border = Image.new('RGB', (qr_size + 20, qr_size + 20), color='white')
    qr_with_border.paste(qr_resized, (10, 10))
    
    # Paste QR code
    qr_x = (sticker_size[0] - qr_size - 20) // 2
    qr_y = 300
    sticker.paste(qr_with_border, (qr_x, qr_y))
    
    # Add "Scan to redeem coupons" text
    try:
        scan_font = ImageFont.truetype("arial.ttf", 18)
    except:
        scan_font = ImageFont.load_default()
    
    scan_text = "Scan to redeem coupons"
    scan_bbox = draw.textbbox((0, 0), scan_text, font=scan_font)
    scan_width = scan_bbox[2] - scan_bbox[0]
    scan_x = (sticker_size[0] - scan_width) // 2
    draw.text((scan_x, 680), scan_text, fill='#999999', font=scan_font)
    
    # Add business code section
    code_section_y = 750
    draw.rectangle(
        [(50, code_section_y), (sticker_size[0] - 50, code_section_y + 150)],
        outline='#CCCCCC',
        width=2
    )
    
    # Add "Business Code" label
    try:
        code_label_font = ImageFont.truetype("arial.ttf", 16)
        code_value_font = ImageFont.truetype("arial.ttf", 48)
    except:
        code_label_font = ImageFont.load_default()
        code_value_font = ImageFont.load_default()
    
    code_label = "Business Code"
    code_label_bbox = draw.textbbox((0, 0), code_label, font=code_label_font)
    code_label_width = code_label_bbox[2] - code_label_bbox[0]
    code_label_x = (sticker_size[0] - code_label_width) // 2
    draw.text((code_label_x, code_section_y + 20), code_label, fill='#666666', font=code_label_font)
    
    # Add business code value
    code_bbox = draw.textbbox((0, 0), business_code, font=code_value_font)
    code_width = code_bbox[2] - code_bbox[0]
    code_x = (sticker_size[0] - code_width) // 2
    draw.text((code_x, code_section_y + 60), business_code, fill='black', font=code_value_font)
    
    # Add footer text
    try:
        footer_font = ImageFont.truetype("arial.ttf", 14)
    except:
        footer_font = ImageFont.load_default()
    
    footer_text = "Show this code to customers for coupon redemption"
    footer_bbox = draw.textbbox((0, 0), footer_text, font=footer_font)
    footer_width = footer_bbox[2] - footer_bbox[0]
    footer_x = (sticker_size[0] - footer_width) // 2
    draw.text((footer_x, 920), footer_text, fill='#999999', font=footer_font)
    
    return sticker


def generate_sticker_zip(
    businesses: List[dict],
    output_format: str = "png"
) -> io.BytesIO:
    """Generate a ZIP file containing stickers for multiple businesses"""
    
    zip_buffer = io.BytesIO()
    
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        for business in businesses:
            business_name = business.get('business_name', 'Business')
            business_code = business.get('business_code', 'CODE')
            
            # Create QR code
            qr_image = create_qr_code(business_code)
            
            # Create sticker
            sticker = create_sticker_with_header(business_name, business_code, qr_image)
            
            # Save to bytes
            img_buffer = io.BytesIO()
            sticker.save(img_buffer, format=output_format.upper())
            img_buffer.seek(0)
            
            # Add to ZIP
            filename = f"{business_code}_{business_name.replace(' ', '_')}.{output_format.lower()}"
            zip_file.writestr(filename, img_buffer.getvalue())
    
    zip_buffer.seek(0)
    return zip_buffer


def generate_single_sticker(
    business_name: str,
    business_code: str,
    output_format: str = "png"
) -> io.BytesIO:
    """Generate a single sticker image"""
    
    # Create QR code
    qr_image = create_qr_code(business_code)
    
    # Create sticker
    sticker = create_sticker_with_header(business_name, business_code, qr_image)
    
    # Save to bytes
    img_buffer = io.BytesIO()
    sticker.save(img_buffer, format=output_format.upper())
    img_buffer.seek(0)
    
    return img_buffer
