# proposal_system/document_processing/document_generator.py
from io import BytesIO
from docx import Document #
from . import docx_utils # Importação relativa

def generate_dcm_document(template_path_or_file, data_replacements, bold_placeholders, comissao_existe): #
    document = Document(template_path_or_file) #
    filled_document = docx_utils.replace_placeholders_in_document(document, data_replacements, bold_placeholders) #
    filled_document = docx_utils.process_comissao_performance(filled_document, comissao_existe) #
    filled_document = docx_utils.adjust_anexo_layout(filled_document) #

    doc_io = BytesIO() #
    filled_document.save(doc_io) #
    doc_io.seek(0) #
    return doc_io #

def generate_coordenacao_document(template_path_or_file, data_replacements, bold_placeholders): #
    document = Document(template_path_or_file) #
    filled_document = docx_utils.replace_placeholders_in_document(document, data_replacements, bold_placeholders) #
    # Nota: process_comissao_performance não é chamado para coordenação
    filled_document = docx_utils.adjust_anexo_layout(filled_document) #

    doc_io = BytesIO() #
    filled_document.save(doc_io) #
    doc_io.seek(0) #
    return doc_io #