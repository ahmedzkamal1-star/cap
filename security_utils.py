import os
import io
import secrets
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import padding
from PyPDF2 import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from PIL import Image, ImageDraw, ImageFont

def generate_user_key():
    """Generates a 32-byte (256-bit) AES key as a hex string."""
    return secrets.token_hex(32)

def encrypt_data(data, key_hex):
    """Encrypts bytes using AES-256-CBC."""
    key = bytes.fromhex(key_hex)
    iv = os.urandom(16)
    padder = padding.PKCS7(128).padder()
    padded_data = padder.update(data) + padder.finalize()
    
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
    encryptor = cipher.encryptor()
    ciphertext = encryptor.update(padded_data) + encryptor.finalize()
    
    return iv + ciphertext

def decrypt_data(encrypted_data, key_hex):
    """Decrypts bytes using AES-256-CBC."""
    key = bytes.fromhex(key_hex)
    iv = encrypted_data[:16]
    ciphertext = encrypted_data[16:]
    
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
    decryptor = cipher.decryptor()
    padded_data = decryptor.update(ciphertext) + decryptor.finalize()
    
    unpadder = padding.PKCS7(128).unpadder()
    data = unpadder.update(padded_data) + unpadder.finalize()
    
    return data

def create_pdf_watermark(text):
    """Creates a single-page PDF in-memory containing a diagonal watermark."""
    packet = io.BytesIO()
    can = canvas.Canvas(packet, pagesize=letter)
    
    # Set appearance
    can.setFont("Helvetica", 40)
    can.setStrokeColorRGB(0.8, 0.8, 0.8, alpha=0.3)
    can.setFillColorRGB(0.8, 0.8, 0.8, alpha=0.3)
    
    # Save graphics state
    can.saveState()
    
    # Move to center and rotate
    can.translate(300, 450)
    can.rotate(45)
    can.drawCentredString(0, 0, text)
    
    # Optional QR code or more text can be added here
    can.restoreState()
    
    can.save()
    packet.seek(0)
    return packet

def add_watermark_to_pdf(input_pdf_bytes, watermark_text):
    """Adds a visible text watermark to every page of a PDF bytes object."""
    reader = PdfReader(io.BytesIO(input_pdf_bytes))
    writer = PdfWriter()
    
    watermark_pdf_io = create_pdf_watermark(watermark_text)
    watermark_reader = PdfReader(watermark_pdf_io)
    watermark_page = watermark_reader.pages[0]
    
    for page in reader.pages:
        page.merge_page(watermark_page)
        writer.add_page(page)
        
    output_stream = io.BytesIO()
    writer.write(output_stream)
    return output_stream.getvalue()

def add_watermark_to_image(input_image_bytes, watermark_text):
    """Adds a visible text watermark to an image bytes object."""
    img = Image.open(io.BytesIO(input_image_bytes)).convert("RGBA")
    overlay = Image.new("RGBA", img.size, (255, 255, 255, 0))
    
    draw = ImageDraw.Draw(overlay)
    
    # Dynamic font size based on image width
    font_size = max(20, img.size[0] // 15)
    try:
        # Try to find a system font
        font = ImageFont.truetype("arial.ttf", font_size)
    except:
        font = ImageFont.load_default()
        
    # Draw centered watermark
    text_bbox = draw.textbbox((0, 0), watermark_text, font=font)
    text_width = text_bbox[2] - text_bbox[0]
    text_height = text_bbox[3] - text_bbox[1]
    
    x = (img.size[0] - text_width) // 2
    y = (img.size[1] - text_height) // 2
    
    # Semi-transparent white
    draw.text((x, y), watermark_text, font=font, fill=(255, 255, 255, 80))
    
    # Repeated watermark for better protection
    draw.text((10, 10), watermark_text, font=font, fill=(255, 255, 255, 40))
    draw.text((img.size[0] - text_width - 10, img.size[1] - text_height - 10), watermark_text, font=font, fill=(255, 255, 255, 40))

    combined = Image.alpha_composite(img, overlay)
    
    output_stream = io.BytesIO()
    combined.convert("RGB").save(output_stream, format="JPEG")
    return output_stream.getvalue()
