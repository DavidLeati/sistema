# config/configs.py

# --- CONFIGURAÇÕES GERAIS DE NAVEGAÇÃO (usado em app.py) ---
PAGES = ["Gerador de Propostas", "Gerador de Recibos"]
GENERATOR_OPTIONS = ["Coordenação", "DCM"]

# --- CONSTANTES COMPARTILHADAS (usado em core/dcm_logic.py, core/coordenacao_logic.py) ---
MESES_PT = ["janeiro", "fevereiro", "março", "abril", "maio", "junho",
            "julho", "agosto", "setembro", "outubro", "novembro", "dezembro"]
TERRA_NOME_COMPLETO = "TERRA INVESTIMENTOS DISTRIBUIDORA DE TÍTULOS E VALORES MOBILIÁRIOS LTDA."

# --- CONFIGURAÇÕES DO GERADOR DCM (usado em core/dcm_logic.py) ---
DCM_OFFER_TYPES_DETAILS = {
    "CRI": {
        "extenso": "Certificados de Recebíveis Imobiliários",
        "gender": "m",
        "fields": ["lastro", "remuneracao_titulo", "amortizacao_principal", "pagamento_juros", "destinacao", "garantias"]
    },
    "CRA": {
        "extenso": "Certificados de Recebíveis do Agronegócio",
        "gender": "m",
        "fields": ["lastro", "remuneracao_titulo", "amortizacao_principal", "pagamento_juros", "destinacao", "garantias"]
    },
    "Debêntures": {
        "extenso": "Debêntures",
        "gender": "f",
        "fields": ["remuneracao_titulo", "amortizacao_principal", "pagamento_juros", "destinacao", "garantias", "uso_recursos_debenture"]
    },
    "Notas Comerciais": {
        "extenso": "Notas Comerciais",
        "gender": "f",
        "fields": ["remuneracao_titulo", "amortizacao_principal", "pagamento_juros", "destinacao", "garantias", "covenants"]
    }
}

DCM_PLACEHOLDERS_TO_BOLD = {
    "[[Devedora]]", "[[Emissora]]", "[[Re]]",
    "[[Tipo_Oferta_Ext]]", "[[Terra]]"
}

DCM_REQUIRED_FIELDS_CHECK = {
    "devedora": "Nome da Devedora",
    "cnpj_devedora": "CNPJ da Devedora",
    "cidade_devedora": "Cidade da Devedora",
    "estado_devedora": "Estado da Devedora",
    "prazo": "Prazo da Operação",
    "destinacao": "Destinação dos Recursos",
    "remuneracao_titulo": "Remuneração do Título",
    "amortizacao_principal": "Amortização do Principal",
    "pagamento_juros": "Pagamento de Juros",
    "garantias": "Garantias da Operação",
    "signatario_nome": "Nome do Signatário",
    "signatario_email": "E-mail do Signatário",
    "emissora": "Nome da Emissora",
    "cnpj_emissora": "CNPJ da Emissora",
}


# --- CONFIGURAÇÕES DO GERADOR COORDENAÇÃO (usado em core/coordenacao_logic.py e ui/coordenacao_page.py) ---
COORD_FIELD_CONFIGS = {
    "CRI": [
        ("Emissora:", "coord_emissora", "Empresa Emissora Exemplo S.A."),
        ("CNPJ Emissora:", "coord_cnpj_emissora", "00.000.000/0001-00"),
        ("Cópia (Nome):", "coord_copia_nome", ""),
        ("Email Cópia:", "coord_copia_email", ""),
        ("Valor Total:", "coord_valor_total_str", "100000000,00"),
        ("Remuneração:", "coord_remuneracao_str", "60000,00"),
        ("Prazo:", "coord_prazo", "10 anos"),
        ("Lastro:", "coord_lastro", "Ex. (CCI)"),
        ("Devedora:", "coord_devedora", "Empresa Devedora Exemplo Ltda."),
        ("Destinação:", "coord_destinacao", "Alocação dos recursos arrecadados com a emissão dos CRI."),
        ("Remuneração Título:", "coord_remuneracao_titulo", "Ex. (CDI + 6%)"),
        ("Amortização Principal:", "coord_amortizacao_principal", "Ex. (Mensal)"),
        ("Pagamento Juros:", "coord_pagamento_juros", "Ex. (Mensal)"),
        ("Garantias:", "coord_garantias", "1) Exemplo de Garantia 1\n2) Exemplo de Garantia 2"),
        ("Assessor Legal:", "coord_assessor_legal", "Escritório de Advocacia Exemplo")
    ],
    "CRA": [
        ("Emissora:", "coord_emissora", "Empresa Emissora Exemplo S.A."),
        ("CNPJ Emissora:", "coord_cnpj_emissora", "00.000.000/0001-00"),
        ("Cópia (Nome):", "coord_copia_nome", ""),
        ("Email Cópia:", "coord_copia_email", ""),
        ("Valor Total:", "coord_valor_total_str", "50000000,00"),
        ("Remuneração:", "coord_remuneracao_str", "50000,00"),
        ("Prazo:", "coord_prazo", "5 anos"),
        ("Lastro:", "coord_lastro", "Ex. (CDA/WA)"),
        ("Devedora:", "coord_devedora", "Agropecuária Exemplo S.A."),
        ("Destinação:", "coord_destinacao", "Alocação dos recursos arrecadados com a emissão dos CRA."),
        ("Remuneração Título:", "coord_remuneracao_titulo", "Ex. (IPCA + 7%)"),
        ("Amortização Principal:", "coord_amortizacao_principal", "Ex. (Anual)"),
        ("Pagamento Juros:", "coord_pagamento_juros", "Ex. (Semestral)"),
        ("Garantias:", "coord_garantias", "1) Penhor Agrícola\n2) Fiança"),
        ("Assessor Legal:", "coord_assessor_legal", "Consultoria Jurídica Exemplo")
    ],
    "Debênture": [
        ("Emissora:", "coord_emissora", "Empresa Emissora Debêntures S.A."),
        ("CNPJ Emissora:", "coord_cnpj_emissora", "11.111.111/0001-11"),
        ("Cópia (Nome):", "coord_copia_nome", ""),
        ("Email Cópia:", "coord_copia_email", ""),
        ("Valor Total:", "coord_valor_total_str", "200000000,00"),
        ("Remuneração:", "coord_remuneracao_str", "120000,00"),
        ("Prazo:", "coord_prazo", "7 anos"),
        ("Remuneração Título:", "coord_remuneracao_titulo", "Ex. (NTN-B + 1,5%)"),
        ("Amortização Principal:", "coord_amortizacao_principal", "Ex. (Ao final)"),
        ("Pagamento Juros:", "coord_pagamento_juros", "Ex. (Anual)"),
        ("Garantias:", "coord_garantias", "1) Fiança Bancária\n2) Alienação Fiduciária de Ações")
    ]
}

COORD_PLACEHOLDERS_TO_BOLD = {
    "[[Devedora]]", "[[Emissora]]", "[[Tipo_Oferta_Ext]]", "[[Terra]]"
}