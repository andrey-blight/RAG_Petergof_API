from ocr.api_ocr import ApiOCR
import asyncio
a = ApiOCR()
pdf_file = 'Кижинов Андрей резюме.pdf'
pdf_name = 'Кижинов Андрей резюме'
with open(pdf_file, 'rb') as f:
    pdf_bytes = f.read()
asyncio.run(a.upload_pdf(pdf_file=pdf_bytes, pdf_name=pdf_name))