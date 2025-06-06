# proposal_system/document_processing/pdf_converter.py
import os
import traceback
from io import BytesIO
from tempfile import NamedTemporaryFile
from docx2pdf import convert #

def convert_docx_to_pdf(docx_bytesio: BytesIO, base_filename: str) -> tuple[BytesIO | None, str | None, str | None]:
    """
    Converte um BytesIO de um arquivo DOCX para um BytesIO de um arquivo PDF.

    Args:
        docx_bytesio: BytesIO contendo os dados do arquivo DOCX.
        base_filename: Nome base para o arquivo PDF de saída (sem extensão).

    Returns:
        Uma tupla contendo (pdf_bytesio, output_filename_pdf, error_message).
        pdf_bytesio será None em caso de erro.
        output_filename_pdf será o nome do arquivo PDF gerado.
        error_message conterá a mensagem de erro, ou None em caso de sucesso.
    """
    output_filename_pdf = f"{base_filename}.pdf"
    tmp_docx_path = None
    tmp_pdf_out_path = None

    try:
        docx_bytesio.seek(0) # Garante que o cursor está no início
        with NamedTemporaryFile(delete=False, suffix=".docx") as tmp_docx_file: #
            tmp_docx_file.write(docx_bytesio.getvalue()) #
            tmp_docx_path = tmp_docx_file.name #

        with NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_pdf_outfile: #
            tmp_pdf_out_path = tmp_pdf_outfile.name #
        
        convert(tmp_docx_path, tmp_pdf_out_path) #

        with open(tmp_pdf_out_path, "rb") as f_pdf: #
            pdf_bytes = f_pdf.read() #
        
        return BytesIO(pdf_bytes), output_filename_pdf, None #

    except Exception as pdf_e:
        error_msg = f"Falha ao converter para PDF: {pdf_e}\nDetalhes: {traceback.format_exc()}" #
        return None, output_filename_pdf, error_msg
    finally:
        if tmp_docx_path and os.path.exists(tmp_docx_path):
            os.unlink(tmp_docx_path) #
        if tmp_pdf_out_path and os.path.exists(tmp_pdf_out_path):
            os.unlink(tmp_pdf_out_path) #