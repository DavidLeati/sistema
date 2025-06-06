# proposal_system/core/coordenacao_logic.py
from datetime import datetime, timedelta #
from dateutil.relativedelta import relativedelta #
from shared_utils.text_utils import valor_por_extenso_reais, numero_por_extenso, genero_quantidade #
from shared_utils.formatting_utils import format_valor_brl #


COORD_FIELD_CONFIGS = { #
    "CRI": [ #
        ("Emissora:", "coord_emissora", "Empresa Emissora Exemplo S.A."), #
        ("CNPJ Emissora:", "coord_cnpj_emissora", "00.000.000/0001-00"), #
        ("Cópia (Nome):", "coord_copia_nome", ""), #
        ("Email Cópia:", "coord_copia_email", ""), #
        ("Valor Total:", "coord_valor_total_str", "100000000,00"),  #
        ("Remuneração:", "coord_remuneracao_str", "60000,00"),  #
        ("Prazo:", "coord_prazo", "10 anos"),  #
        ("Lastro:", "coord_lastro", "Ex. (CCI)"),  #
        ("Devedora:", "coord_devedora", "Empresa Devedora Exemplo Ltda."),  #
        ("Destinação:", "coord_destinacao", "Alocação dos recursos arrecadados com a emissão dos CRI."),  #
        ("Remuneração Título:", "coord_remuneracao_titulo", "Ex. (CDI + 6%)"),  #
        ("Amortização Principal:", "coord_amortizacao_principal", "Ex. (Mensal)"),  #
        ("Pagamento Juros:", "coord_pagamento_juros", "Ex. (Mensal)"),  #
        ("Garantias:", "coord_garantias", "1) Exemplo de Garantia 1\n2) Exemplo de Garantia 2"),  #
        ("Assessor Legal:", "coord_assessor_legal", "Escritório de Advocacia Exemplo")  #
    ],
    "CRA": [ #
        ("Emissora:", "coord_emissora", "Empresa Emissora Exemplo S.A."), #
        ("CNPJ Emissora:", "coord_cnpj_emissora", "00.000.000/0001-00"), #
        ("Cópia (Nome):", "coord_copia_nome", ""), #
        ("Email Cópia:", "coord_copia_email", ""), #
        ("Valor Total:", "coord_valor_total_str", "50000000,00"), #
        ("Remuneração:", "coord_remuneracao_str", "50000,00"), #
        ("Prazo:", "coord_prazo", "5 anos"), #
        ("Lastro:", "coord_lastro", "Ex. (CDA/WA)"), #
        ("Devedora:", "coord_devedora", "Agropecuária Exemplo S.A."), #
        ("Destinação:", "coord_destinacao", "Alocação dos recursos arrecadados com a emissão dos CRA."), #
        ("Remuneração Título:", "coord_remuneracao_titulo", "Ex. (IPCA + 7%)"), #
        ("Amortização Principal:", "coord_amortizacao_principal", "Ex. (Anual)"), #
        ("Pagamento Juros:", "coord_pagamento_juros", "Ex. (Semestral)"), #
        ("Garantias:", "coord_garantias", "1) Penhor Agrícola\n2) Fiança"), #
        ("Assessor Legal:", "coord_assessor_legal", "Consultoria Jurídica Exemplo") #
    ],
    "Debênture": [ #
        ("Emissora:", "coord_emissora", "Empresa Emissora Debêntures S.A."), #
        ("CNPJ Emissora:", "coord_cnpj_emissora", "11.111.111/0001-11"), #
        ("Cópia (Nome):", "coord_copia_nome", ""), #
        ("Email Cópia:", "coord_copia_email", ""), #
        ("Valor Total:", "coord_valor_total_str", "200000000,00"), #
        ("Remuneração:", "coord_remuneracao_str", "120000,00"), #
        ("Prazo:", "coord_prazo", "7 anos"), #
        ("Remuneração Título:", "coord_remuneracao_titulo", "Ex. (NTN-B + 1,5%)"), #
        ("Amortização Principal:", "coord_amortizacao_principal", "Ex. (Ao final)"), #
        ("Pagamento Juros:", "coord_pagamento_juros", "Ex. (Anual)"), #
        ("Garantias:", "coord_garantias", "1) Fiança Bancária\n2) Alienação Fiduciária de Ações") #
    ]
}


def prepare_coordenacao_data(inputs: dict, offer_type: str) -> tuple[dict, list]: #
    errors = [] #
    data_to_replace = {} #

    try:
        valor_total_str = inputs.get("coord_valor_total_str", "0").replace(",", ".") #
        valor_total = float(valor_total_str) #
    except ValueError: #
        errors.append(f"Valor Total inválido: '{inputs.get('coord_valor_total_str', '')}'. Use formato numérico como 100000,00.") #
        valor_total = 0.0 #

    try:
        remuneracao_str = inputs.get("coord_remuneracao_str", "0").replace(",", ".") #
        remuneracao_valor = float(remuneracao_str) #
    except ValueError: #
        errors.append(f"Remuneração inválida: '{inputs.get('coord_remuneracao_str', '')}'. Use formato numérico como 60000,00.") #
        remuneracao_valor = 0.0 #

    if errors: #
        return {}, errors #

    data_hoje = datetime.now() #
    dia = data_hoje.day #
    meses_pt = ["janeiro", "fevereiro", "março", "abril", "maio", "junho", #
                "julho", "agosto", "setembro", "outubro", "novembro", "dezembro"] #
    mes = meses_pt[data_hoje.month - 1] #
    ano = data_hoje.year  #

    valor_total_ext_str = valor_por_extenso_reais(valor_total).lower() #
    
    qtd_total = valor_total / 1000 #
    qtd_total_ext_str = numero_por_extenso(qtd_total) #
    qtd_total_ext_str = genero_quantidade(qtd_total_ext_str + ' cotas') # # Utiliza genero_quantidade de text_utils

    remuneracao_ext_str = valor_por_extenso_reais(remuneracao_valor) #

    data_1ano_obj = data_hoje + relativedelta(years=1)  #
    data_1ano_ext = f'{data_1ano_obj.day} de {meses_pt[data_1ano_obj.month - 1]} de {data_1ano_obj.year}'  #

    data_20dias_obj = data_hoje + timedelta(days=20)  #
    data_20dias_ext = f'{data_20dias_obj.day} de {meses_pt[data_20dias_obj.month - 1]} de {data_20dias_obj.year}'  #

    valor_total_fmt_str = format_valor_brl(valor_total) #
    remuneracao_fmt_str = format_valor_brl(remuneracao_valor) #
    qtd_total_fmt_str = f"{qtd_total:_.0f}".replace("_", "X").replace(".", ",").replace("X", ".") #


    data_to_replace = { #
        "[[Dia]]": str(dia), #
        "[[Mes]]": str(mes), #
        "[[Ano]]": str(ano), #
        "[[Terra]]": str("TERRA INVESTIMENTOS DISTRIBUIDORA DE TÍTULOS E VALORES MOBILIÁRIOS LTDA."), #
        "[[Emissora]]": inputs.get("coord_emissora", ""), #
        "[[CNPJ_Emissora]]": inputs.get("coord_cnpj_emissora", ""), #
        "[[Copia]]": inputs.get("coord_copia_nome", ""), #
        "[[Email_Copia]]": inputs.get("coord_copia_email", ""), #
        "[[Valor_Total]]": valor_total_fmt_str, #
        "[[Valor_Total_Ext]]": valor_total_ext_str, #
        "[[Qtd_Total]]": qtd_total_fmt_str, #
        "[[Qtd_Total_Ext]]": qtd_total_ext_str,  #
        "[[Remuneracao]]": remuneracao_fmt_str,  #
        "[[Remuneracao_Ext]]": remuneracao_ext_str,  #
        "[[Data_1ano]]": data_1ano_ext,  #
        "[[Data_20dias]]": data_20dias_ext,  #
        "[[Prazo]]": inputs.get("coord_prazo", ""),  #
        "[[Remuneracao_Titulo]]": inputs.get("coord_remuneracao_titulo", ""),  #
        "[[Amor_Princ]]": inputs.get("coord_amortizacao_principal", ""), #
        "[[Pgto_Juros]]": inputs.get("coord_pagamento_juros", ""), #
        "[[Garantias]]": inputs.get("coord_garantias", ""), #
    }

    if offer_type in ["CRI", "CRA"]: #
        data_to_replace["[[Lastro]]"] = inputs.get("coord_lastro", "")  #
        data_to_replace["[[Devedora]]"] = inputs.get("coord_devedora", "")  #
        data_to_replace["[[Destinacao]]"] = inputs.get("coord_destinacao", "")  #
        data_to_replace["[[Assessor]]"] = inputs.get("coord_assessor_legal", "")  #
    
    return data_to_replace, errors #