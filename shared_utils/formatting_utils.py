# proposal_system/shared_utils/formatting_utils.py
import re

def format_cep(cep_str: str) -> str:
    """
    Formata uma string de CEP para o formato XXXXX-XXX.
    Retorna a string original se não puder ser formatada como um CEP de 8 dígitos.
    """
    if cep_str and isinstance(cep_str, str):
        cleaned_cep = "".join(filter(str.isdigit, cep_str))
        if len(cleaned_cep) == 8:
            return f"{cleaned_cep[:5]}-{cleaned_cep[5:]}"
    return cep_str

def format_valor_brl(valor: float) -> str:
    """
    Formata um float para o padrão monetário brasileiro (ex: 1.234.567,89).
    """
    return f"{valor:_.2f}".replace("_", "X").replace(".", ",").replace("X", ".")