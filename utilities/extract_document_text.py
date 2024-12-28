import io
from pypdf import PdfReader
from docx import Document

class DocumentParser:
    def __init__(self):
        self.supported_formats = ['text/plain', 'application/pdf', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document']
        self.MAX_SIZE = 100 * 1024 * 1024  # 100MB in bytes

    def check_file_size(self, file_bytes):
        if len(file_bytes) > self.MAX_SIZE:
            raise ValueError('Lo siento, el documento que subiste es demasiado grande. El tamaño máximo es de 100MB.')
        
    def check_text_length(self, text):
        if len(text) > 10000:
            raise ValueError('Lo siento, el documento que subiste es demasiado largo. El límite es de 10,000 caracteres. Intenta subir un documento más corto o dividirlo en partes.')
        return text

    def parse_txt(self, file_bytes):
        try:
            return file_bytes.decode('utf-8')
        except UnicodeDecodeError:
            return file_bytes.decode('latin-1')

    def parse_pdf(self, file_bytes):
        text = []
        pdf_file = io.BytesIO(file_bytes)
        pdf_reader = PdfReader(pdf_file)
        for page in pdf_reader.pages:
            text.append(page.extract_text())
        return '\n'.join(text)

    def parse_docx(self, file_bytes):
        docx_file = io.BytesIO(file_bytes)
        doc = Document(docx_file)
        return '\n'.join([paragraph.text for paragraph in doc.paragraphs])

    def parse(self, file_bytes, file_type):
        try:
            # Validate file size
            self.check_file_size(file_bytes)
            
            # Validate file extension
            file_type = file_type.lower()
            if file_type not in self.supported_formats:
                raise TypeError('Lo siento, no puedo procesar este tipo de documento aún. He tomado nota y trabajaré para agregar soporte en el futuro.')
            
            # Parse based on file extension
            if file_type == 'text/plain':
                text = self.parse_txt(file_bytes)
            elif file_type == 'application/pdf':
                text = self.parse_pdf(file_bytes)
            elif file_type == 'application/vnd.openxmlformats-officedocument.wordprocessingml.document':
                text = self.parse_docx(file_bytes)

            # Validate text length
            return self.check_text_length(text)
                
        except Exception as e:
            raise Exception(e)
