# proposal_system/shared_utils/text_utils.py
from num2words import num2words

def genero_quantidade(frase: str) -> str:
    """
    Ajusta o gênero de palavras de quantidade em uma frase para o feminino.
    Ex: "um milhão e duzentos mil" -> "uma milhão e duzentas mil"
    (Nota: a lógica original para "milhão" pode precisar de revisão,
     mas mantendo a lógica como estava).
    "dois" -> "duas"
    """
    palavras = frase.split()
    nova_frase_lista = []

    for palavra in palavras:
        if len(palavra) >= 2 and palavra.lower().endswith("os"):
            palavra_transformada = palavra[:-2] + "as"
            nova_frase_lista.append(palavra_transformada)
        elif palavra.lower() == 'um': # Ajustado para lower() para robustez
            palavra_transformada = 'uma'
            nova_frase_lista.append(palavra_transformada)
        elif palavra.lower() == 'dois': # Ajustado para lower() para robustez
            palavra_transformada = 'duas'
            nova_frase_lista.append(palavra_transformada)
        else:
            nova_frase_lista.append(palavra)

    return " ".join(nova_frase_lista)

def valor_por_extenso_reais(valor: float) -> str:
    """
    Converte um valor float para sua representação por extenso em reais.
    """
    return num2words(valor, lang='pt_BR', to='currency')

def numero_por_extenso(numero: float, **kwargs) -> str:
    """
    Wrapper para num2words para converter um número genérico para extenso.
    """
    return num2words(numero, lang='pt_BR', **kwargs)