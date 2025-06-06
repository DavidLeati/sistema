# proposal_system/document_processing/docx_utils.py
import re
from docx.shared import Pt, RGBColor
from docx.text.paragraph import Paragraph as DocxParagraphObject
from docx.oxml.text.paragraph import CT_P
# from docx.oxml.table import CT_Tbl # Não usado diretamente aqui

def find_next_placeholder_details(text_to_search: str, placeholders_map: dict, search_start_index: int = 0): #
    first_placeholder_found = None #
    earliest_position = -1 #

    for ph_key in placeholders_map.keys(): #
        position = text_to_search.find(ph_key, search_start_index) #
        if position != -1: #
            if earliest_position == -1 or position < earliest_position: #
                earliest_position = position #
                first_placeholder_found = ph_key #
    
    return first_placeholder_found, earliest_position #

def replace_placeholders_in_paragraph(paragraph: DocxParagraphObject, 
                                                replacements: dict, 
                                                bold_placeholders: set): #
    current_paragraph_text = "".join(run.text for run in paragraph.runs) #

    if not any(ph in current_paragraph_text for ph in replacements.keys()): #
        return #

    text_segments = []   #
    current_search_idx = 0 #

    while current_search_idx < len(current_paragraph_text): #
        placeholder_key, placeholder_start_idx = find_next_placeholder_details( #
            current_paragraph_text, replacements, current_search_idx #
        )

        if placeholder_key is None: #
            if current_search_idx < len(current_paragraph_text): #
                text_segments.append((current_paragraph_text[current_search_idx:], False)) #
            break   #

        if placeholder_start_idx > current_search_idx: #
            text_segments.append((current_paragraph_text[current_search_idx:placeholder_start_idx], False)) #

        replacement_text = str(replacements.get(placeholder_key, placeholder_key))  #
        should_be_bold = placeholder_key in bold_placeholders #
        text_segments.append((replacement_text, should_be_bold)) #

        current_search_idx = placeholder_start_idx + len(placeholder_key) #

    while paragraph.runs: #
        p_element = paragraph._p   #
        r_element = paragraph.runs[0]._r   #
        p_element.remove(r_element) #

    for text_content, should_be_bold_segment in text_segments: #
        if not text_content:   #
            continue #
        run = paragraph.add_run(text_content) #
        run.font.name = 'Calibri' #
        run.font.size = Pt(11) #
        run.font.color.rgb = RGBColor(0x00, 0x00, 0x00) #
        run.font.bold = should_be_bold_segment #

def replace_placeholders_in_document(doc, replacements_map: dict, placeholders_to_make_bold: set = None): #
    if placeholders_to_make_bold is None: #
        placeholders_to_make_bold = set() #

    for paragraph in doc.paragraphs: #
        replace_placeholders_in_paragraph(paragraph, replacements_map, placeholders_to_make_bold) #
    
    for table in doc.tables: #
        for row in table.rows: #
            for cell in row.cells: #
                for paragraph_in_cell in cell.paragraphs: #
                    replace_placeholders_in_paragraph(paragraph_in_cell, replacements_map, placeholders_to_make_bold) #
    return doc #

def process_comissao_performance(doc, comissao_existe: bool): #
    if comissao_existe: #
        return doc #

    body_element = doc.element.body #
    if not body_element: #
        return doc #

    item_6_2_pattern = re.compile(r"^\s*6\.2[\s\.\t]") #
    rationale_start_pattern = re.compile(r"^\s*Comissão de Performance", re.IGNORECASE) #
    generic_item_6_x_pattern = re.compile(r"^\s*6\.\d+[\s\.\t]") #
    item_6_3_pattern = re.compile(r"^\s*6\.3[\s\.\t]") #
    sentence_to_remove_in_6_3_base = "As remunerações previstas nas Cláusulas 6.1 e 6.2 acima são denominadas, em conjunto, como “Comissões”" #

    elements_to_remove = [] #
    paragraph_6_3_element_ref = None  #
    found_6_2_title_flag = False #
    in_rationale_removal_flag = False #
    
    child_elements = list(body_element.iterchildren()) #

    for oxml_el in child_elements: #
        if not isinstance(oxml_el, CT_P): #
            found_6_2_title_flag = False #
            in_rationale_removal_flag = False #
            continue #

        para_obj = DocxParagraphObject(oxml_el, doc) #
        para_text_stripped = para_obj.text.strip() #

        if found_6_2_title_flag: #
            if rationale_start_pattern.match(para_text_stripped): #
                elements_to_remove.append(oxml_el) #
                in_rationale_removal_flag = True #
                found_6_2_title_flag = False #
            elif generic_item_6_x_pattern.match(para_text_stripped): #
                found_6_2_title_flag = False #
                in_rationale_removal_flag = False #
                if item_6_3_pattern.match(para_text_stripped) and paragraph_6_3_element_ref is None: #
                    paragraph_6_3_element_ref = oxml_el #
            else:
                elements_to_remove.append(oxml_el) #
        
        elif in_rationale_removal_flag: #
            if generic_item_6_x_pattern.match(para_text_stripped): #
                in_rationale_removal_flag = False #
                if item_6_3_pattern.match(para_text_stripped) and paragraph_6_3_element_ref is None: #
                    paragraph_6_3_element_ref = oxml_el #
            else:
                elements_to_remove.append(oxml_el) #
        
        elif item_6_2_pattern.match(para_text_stripped): #
            elements_to_remove.append(oxml_el) #
            found_6_2_title_flag = True #
        elif item_6_3_pattern.match(para_text_stripped) and paragraph_6_3_element_ref is None: #
            paragraph_6_3_element_ref = oxml_el #

    for el_to_remove in elements_to_remove: #
        try:
            body_element.remove(el_to_remove) #
        except ValueError: #
            pass #

    if paragraph_6_3_element_ref and isinstance(paragraph_6_3_element_ref, CT_P): #
        para_6_3_obj = DocxParagraphObject(paragraph_6_3_element_ref, doc) #
        current_text_6_3 = para_6_3_obj.text #
        modified_text_6_3 = current_text_6_3 #
        
        possible_endings = [".”", ".", "”.", "!”", "!"]  #
        sentence_found_and_removed = False #
        for ending in possible_endings: #
            sentence_variant = sentence_to_remove_in_6_3_base[:-1] + ending if sentence_to_remove_in_6_3_base.endswith('”') else sentence_to_remove_in_6_3_base + ending #
            if sentence_variant in modified_text_6_3: #
                modified_text_6_3 = modified_text_6_3.replace(sentence_variant, "") #
                sentence_found_and_removed = True #
                break #
        if not sentence_found_and_removed and sentence_to_remove_in_6_3_base in modified_text_6_3: #
            modified_text_6_3 = modified_text_6_3.replace(sentence_to_remove_in_6_3_base, "") #

        modified_text_6_3 = re.sub(r'\s{2,}', ' ', modified_text_6_3).strip() #

        for run_idx in range(len(para_6_3_obj.runs) - 1, -1, -1): #
            para_6_3_obj._p.remove(para_6_3_obj.runs[run_idx]._r) #
        
        if modified_text_6_3: #
            new_run = para_6_3_obj.add_run(modified_text_6_3) #
            new_run.font.name = 'Calibri' #
            new_run.font.size = Pt(11) #
            new_run.font.color.rgb = RGBColor(0x00, 0x00, 0x00) #
            new_run.font.bold = None #
            new_run.font.italic = None #

    all_paragraphs_after_changes = doc.paragraphs #
    for para_obj in all_paragraphs_after_changes: #
        current_para_text = para_obj.text #
        renumber_match = re.match(r"^(\s*6\.)(\d+)([\s\.\t])", current_para_text) #
        
        if renumber_match: #
            captured_prefix_before_num = renumber_match.group(1) #
            captured_original_num_str = renumber_match.group(2) #
            captured_separator_after_num = renumber_match.group(3) #
            text_after_full_prefix = current_para_text[renumber_match.end(0):] #

            try:
                original_num_int = int(captured_original_num_str) #
                if 3 <= original_num_int <= 10: #
                    new_num_int = original_num_int - 1 #
                    new_full_prefix = captured_prefix_before_num + str(new_num_int) + captured_separator_after_num #
                    new_paragraph_text = new_full_prefix + text_after_full_prefix #

                    original_font_name = 'Calibri' #
                    original_font_size = Pt(11) #
                    original_font_color_rgb = RGBColor(0,0,0) #
                    original_bold = None #
                    
                    if para_obj.runs: #
                        first_run = para_obj.runs[0] #
                        original_font_name = first_run.font.name if first_run.font.name else 'Calibri' #
                        original_font_size = first_run.font.size if first_run.font.size else Pt(11) #
                        original_bold = first_run.font.bold #
                        if first_run.font.color and first_run.font.color.rgb: #
                            original_font_color_rgb = first_run.font.color.rgb #

                    for run_idx in range(len(para_obj.runs) - 1, -1, -1): #
                        para_obj._p.remove(para_obj.runs[run_idx]._r) #
                    
                    new_run = para_obj.add_run(new_paragraph_text) #
                    new_run.font.name = original_font_name #
                    new_run.font.size = original_font_size #
                    new_run.font.color.rgb = original_font_color_rgb #
                    new_run.font.bold = original_bold #
            except ValueError: #
                continue #
    return doc #


def adjust_anexo_layout(doc): #
    anexo_pattern = re.compile(r"^\s*ANEXO\s+([IVXLCDM]+)(\s*-|\s\.|\s|$)", re.IGNORECASE) #
    body_element = doc.element.body #
    if not body_element: #
        return doc #

    elements_to_remove = set() #
    child_elements = list(body_element.iterchildren()) #

    for i, current_oxml_el in enumerate(child_elements): #
        if isinstance(current_oxml_el, CT_P): #
            current_para_obj = DocxParagraphObject(current_oxml_el, doc) #
            if anexo_pattern.match(current_para_obj.text.strip()): #
                j = i - 1 #
                while j >= 0: #
                    prev_oxml_el_candidate = child_elements[j] #
                    if isinstance(prev_oxml_el_candidate, CT_P): #
                        prev_para_candidate_obj = DocxParagraphObject(prev_oxml_el_candidate, doc) #
                        if not prev_para_candidate_obj.text.strip(): #
                            elements_to_remove.add(prev_oxml_el_candidate) #
                            j -= 1 #
                        else:
                            break  #
                    else:
                        break #
    
    if elements_to_remove: #
        for el_to_remove in elements_to_remove: #
            try:
                body_element.remove(el_to_remove) #
            except ValueError: #
                pass #

    current_paragraphs_after_cleaning = doc.paragraphs #
    for idx, para_obj in enumerate(current_paragraphs_after_cleaning): #
        if anexo_pattern.match(para_obj.text.strip()): #
            if idx == 0: #
                continue #
            para_obj.paragraph_format.page_break_before = True #
    return doc #