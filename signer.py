from Crypto.PublicKey import RSA
from Crypto.Signature import pkcs1_15
from Crypto.Hash import SHA256
from fpdf import FPDF
from PyPDF2 import PdfWriter, PdfReader, PageObject
import os
import datetime
import qrcode
from PIL import Image, ImageDraw, ImageFont
import base64

# Kullanıcı için anahtar çifti oluşturma
def generate_keys():
    key = RSA.generate(2048)
    private_key = key.export_key()
    public_key = key.publickey().export_key()
    return private_key, public_key

# Belge imzalama
def sign_document(private_key, document_content):
    key = RSA.import_key(private_key)
    h = SHA256.new(document_content)
    signature = pkcs1_15.new(key).sign(h)
    return signature

# UTF-8 karakterlerini latin-1'e dönüştürme
def utf8_to_latin1(text):
    return text.encode('latin-1', 'replace').decode('latin-1')

# QR kod oluşturma
def create_qr_code_with_text(data, filename, text):
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=1,
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)
    
    img = qr.make_image(fill='black', back_color='white').convert('RGB')
    
    # Metni ekle
    draw = ImageDraw.Draw(img)
    font = ImageFont.load_default()
    
    # Metnin genişliğini ve yüksekliğini al
    text_bbox = draw.textbbox((0, 0), text, font=font)
    text_width = text_bbox[2] - text_bbox[0]
    text_height = text_bbox[3] - text_bbox[1]
    
    # Yeni resim boyutları
    new_width = img.width + text_width + 10  # 10 piksel boşluk ekle
    new_height = img.height
    
    # Yeni bir resim oluştur
    new_img = Image.new('RGB', (new_width, new_height), 'white')
    new_img.paste(img, (text_width + 10, 0))  # QR kodunu sağa yerleştir
    
    # Metni çiz
    draw = ImageDraw.Draw(new_img)
    draw.text((0, (new_height - text_height) // 2), text, fill='black', font=font)
    
    new_img.save(filename)

# QR kodu her sayfanın sağ üst köşesine ekleme
def add_qr_code_to_pdf(input_pdf_path, output_pdf_path, qr_image_path):
    reader = PdfReader(input_pdf_path)
    writer = PdfWriter()
    
    for page_number in range(len(reader.pages)):
        page = reader.pages[page_number]
        qr_image = Image.open(qr_image_path)
        
        # QR kodunun boyutlarını al
        qr_width, qr_height = qr_image.size
        
        # Sayfanın boyutlarını al ve float türüne dönüştür
        page_width = float(page.mediabox.upper_right[0])
        page_height = float(page.mediabox.upper_right[1])
        
        # QR kodunun sayfanın sağ üst köşesine yerleştirileceği pozisyon
        x = page_width - qr_width - 10  # Sağdan 10 birim boşluk
        y = page_height - qr_height - 10  # Yukarıdan 10 birim boşluk
        
        page.merge_page(create_qr_code_overlay_page(page_width, page_height, qr_image_path, x, y))
        writer.add_page(page)
    
    with open(output_pdf_path, "wb") as outputStream:
        writer.write(outputStream)

# QR kodu eklemek için boş bir sayfa oluştur ve QR kodunu üzerine yerleştir
def create_qr_code_overlay_page(page_width, page_height, qr_image_path, x, y):
    overlay_pdf = FPDF(unit="pt", format=[page_width, page_height])
    overlay_pdf.add_page()
    overlay_pdf.image(qr_image_path, x=x, y=y)
    overlay_path = "user_files/overlay.pdf"
    overlay_pdf.output(overlay_path)
    
    overlay_reader = PdfReader(overlay_path)
    return overlay_reader.pages[0]

# İmzalı PDF oluşturma
def create_signed_pdf(input_pdf_path, output_pdf_path, signature_text, private_keys, user_info):
    # PDF'yi oku
    private_key= base64.b64decode(private_keys)

    existing_pdf = PdfReader(open(input_pdf_path, "rb"))
    output = PdfWriter()
    print(user_info)
    # Metadata ekle ve PDF'yi yeniden kaydet
    output.add_metadata({
        '/Title': 'Signed Document',
        '/Author': user_info[4],
        '/Subject': 'Dijital İmza',
        '/Keywords': 'Signature, PDF',
        '/Creator': 'PDF Signer',
        '/Producer': 'PyPDF2',
        '/CreationDate': datetime.datetime.now().strftime("%Y-%m-%d"),
        '/ModDate': datetime.datetime.now().strftime("%Y-%m-%d"),
    })
    
    # Tüm sayfaları yeni PDF'ye ekle
    for page in existing_pdf.pages:
        output.add_page(page)
    # Belgeyi dijital olarak imzala
    # Metadata ekle ve PDF'yi yeniden kaydet
   
    # # İmza PDF'si oluştur
    # signature_pdf = FPDF()
    # signature_pdf.add_page()
    # signature_pdf.set_xy(10, 10)
    # signature_pdf.set_font('Arial', 'B', 12)
    # signature_pdf.cell(ln=0, h=10.0, align='L', w=0, txt=utf8_to_latin1(signature_text), border=0)
    
    # # İmza bilgileri ekle
    # signature_pdf.set_xy(10, 20)
    # signature_pdf.set_font('Arial', '', 10)
    # signature_pdf.cell(ln=0, h=10.0, align='L', w=0, txt=utf8_to_latin1(f"Signed by: {user_info['name']}"), border=0)
    # signature_pdf.set_xy(10, 30)
    # signature_pdf.cell(ln=0, h=10.0, align='L', w=0, txt=utf8_to_latin1(f"Date: {user_info['date']}"), border=0)
    
    # Geçici dosyaya kaydet
    # signature_pdf.output('signature.pdf')
    
    # İmza PDF'sini oku
    # signature = PdfReader(open('signature.pdf', "rb"))
    # signature_page = signature.pages[0]
    
    # # İmza sayfasını birleştir
    # output.add_page(signature_page)
    
    # QR kod oluştur ve metni ekle
    qr_data = f"Name: {user_info[4]}\n MAIL: {user_info[1]}"
    qr_filename = 'user_files/qrcode_with_text.png'
    create_qr_code_with_text(qr_data, qr_filename,utf8_to_latin1( user_info[4] +" Tarafindan " + datetime.datetime.now().strftime("%Y-%m-%d")+ " Tarihinde Dijital Imzalanmistir"))
    
    # Yeni PDF'yi kaydet
    temp_pdf_path = "user_files/temp_signed_output.pdf"
    with open(temp_pdf_path, "wb") as outputStream:
        output.write(outputStream)
    
    # QR kodu PDF'ye ekle
    add_qr_code_to_pdf(temp_pdf_path, output_pdf_path, qr_filename)
    
    # Belgeyi dijital olarak imzala
    with open(output_pdf_path, "rb") as f:
        signed_document_content = f.read()
    
    signature = sign_document(private_key, signed_document_content)
    
    # İmza dosyasını .sig uzantılı olarak kaydet
    sig_path = output_pdf_path + '.sig'
    with open(sig_path, "wb") as sig_file:
        sig_file.write(signature)
    
    print(signature.hex())

# İmza doğrulama
def verify_signature(public_key, document_path, signature_path):
    with open(document_path, 'rb') as f:
        document_content = f.read()
    
    with open(signature_path, 'rb') as f:
        signature = f.read()
    
    key = RSA.import_key(public_key)
    h = SHA256.new(document_content)
    
    try:
        pkcs1_15.new(key).verify(h, signature)
        return True
    except (ValueError, TypeError):
        return False


private_key, public_key = generate_keys()
user_info = {
    'name': 'John Doe',
    'date': datetime.datetime.now().strftime("%Y-%m-%d")
}
# create_signed_pdf("input.pdf", "user_files/signed_output.pdf", "", private_key, user_info)

# is_valid = verify_signature(public_key, "user_files/signed_output.pdf", "user_files/signed_output.pdf.sig")
# print(f"İmza geçerli mi? {is_valid}")
