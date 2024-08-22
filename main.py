from fpdf import FPDF
from PyPDF2 import PdfWriter, PdfReader

def create_signed_pdf(input_pdf_path, output_pdf_path, signature_text):
    # PDF'yi oku
    existing_pdf = PdfReader(open(input_pdf_path, "rb"))
    output = PdfWriter()
    
    # İlk sayfayı al ve yeni PDF'ye ekle
    page = existing_pdf.pages[0]
    output.add_page(page)
    
    # İmza PDF'si oluştur
    signature_pdf = FPDF()
    signature_pdf.add_page()
    signature_pdf.set_xy(0, 0)
    signature_pdf.set_font('Arial', 'B', 12)
    signature_pdf.cell(ln=0, h=10.0, align='L', w=0, txt=signature_text, border=0)
    
    # Geçici dosyaya kaydet
    signature_pdf.output('signature.pdf')
    
    # İmza PDF'sini oku
    signature = PdfReader(open('signature.pdf', "rb"))
    signature_page = signature.pages[0]
    
    # İmza sayfasını birleştir
    output.add_page(signature_page)
    
    # Yeni PDF'yi kaydet
    with open(output_pdf_path, "wb") as outputStream:
        output.write(outputStream)

create_signed_pdf("input.pdf", "signed_output.pdf", "Your Signature Here")
