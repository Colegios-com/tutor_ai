import io
from pypdf import PdfReader


SUPPORTED_FORMATS = ['text/plain', 'application/pdf']
MAX_SIZE = 50 * 1024 * 1024  # 100MB in bytes
MAX_TEXT_LENGTH = 50000


def check_file_size(data: bytes) -> None:
    if len(data) > MAX_SIZE:
        raise ValueError('Lo siento, el documento que subiste es demasiado grande. El tamaño máximo es de 100MB.')


def check_text_length(text: str) -> str:
    if len(text) > MAX_TEXT_LENGTH:
        raise ValueError('Lo siento, el documento que subiste es demasiado largo. El límite es de 50,000 caracteres. Intenta subir un documento más corto o dividirlo en partes.')
    return text


def parse_txt(data: bytes) -> str:
    try:
        return data.decode('utf-8')
    except UnicodeDecodeError:
        return data.decode('latin-1')


def parse_pdf(data: bytes) -> str:
    text = []
    pdf_file = io.BytesIO(data)
    pdf_reader = PdfReader(pdf_file)
    for page in pdf_reader.pages:
        text.append(page.extract_text())
    return '\n'.join(text)


def parse_document(data: bytes, file_type: str) -> str:
    try:
        # Validate file size
        check_file_size(data)

        # Validate file extension
        file_type = file_type.lower()
        if file_type not in SUPPORTED_FORMATS:
            raise TypeError('Lo siento, no puedo procesar este tipo de documento aún. He tomado nota y trabajaré para agregar soporte en el futuro.')

        # Parse based on file extension
        if file_type == 'text/plain':
            text = parse_txt(data)
        elif file_type == 'application/pdf':
            text = parse_pdf(data)
        else:
            raise ValueError(f"Unsupported file type: {file_type}")

        # Validate text length
        return check_text_length(text)

    except Exception as e:
        raise Exception(e)