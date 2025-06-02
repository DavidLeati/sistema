import requests
import re

def consultar_cnpj(cnpj: str) -> dict:
    """
    Consulta um CNPJ na API publica.cnpj.ws.

    Args:
        cnpj: O número do CNPJ, podendo conter caracteres especiais.

    Returns:
        Um dicionário com a resposta da API em caso de sucesso,
        ou um dicionário com uma mensagem de erro em caso de falha.
    """
    # Define o endpoint da API
    cnpj = re.sub(r'[^0-9]', '', cnpj)
    endpoint = f"https://open.cnpja.com/office/{cnpj}"

    try:
        # Faz a requisição GET, especificando o verify com o caminho do certifi
        response = requests.get(endpoint, verify=False)
        response.raise_for_status()  # Lança uma exceção para códigos de erro HTTP (4xx ou 5xx)
        return response.json()  # Retorna a resposta da API em formato JSON (dicionário)
    except requests.exceptions.HTTPError as http_err:
        # Tenta obter a resposta da API mesmo em caso de erro HTTP para mais detalhes
        error_details = {"erro": f"Erro HTTP: {http_err}", "status_code": response.status_code if 'response' in locals() and hasattr(response, 'status_code') else None}
        try:
            if 'response' in locals() and response.text:
                error_details["resposta_api"] = response.json() # Tenta parsear como JSON
        except ValueError:
            error_details["resposta_bruta_api"] = response.text # Se não for JSON, retorna texto bruto
        return error_details
    except requests.exceptions.ConnectionError as conn_err:
        return {"erro": f"Erro de Conexão: {conn_err}"}
    except requests.exceptions.Timeout as timeout_err:
        return {"erro": f"Erro de Timeout: {timeout_err}"}
    except requests.exceptions.RequestException as req_err:
        return {"erro": f"Erro na Requisição: {req_err}"}
    except ValueError as json_err: # Erro ao decodificar JSON
        return {"erro": f"Erro ao decodificar JSON da resposta: {json_err}", "resposta_bruta": response.text if 'response' in locals() and hasattr(response, 'text') else None}

if __name__ == '__main__':
    # Exemplo de uso da função
    cnpj_exemplo = "34.006.497/0001-77" # CNPJ de exemplo

    print(f"Consultando o CNPJ: {cnpj_exemplo}")
    resultado = consultar_cnpj(cnpj_exemplo)
    print(resultado)

    if "erro" in resultado:
        print(f"Ocorreu um erro: {resultado['erro']}")
        if "status_code" in resultado and resultado["status_code"]:
            print(f"Status Code: {resultado['status_code']}")
        if "resposta_api" in resultado and resultado["resposta_api"]:
            print(f"Resposta da API (detalhes do erro): {resultado['resposta_api']}")
        elif "resposta_bruta_api" in resultado and resultado["resposta_bruta_api"]:
            print(f"Resposta Bruta da API (detalhes do erro): {resultado['resposta_bruta_api']}")
        if "resposta_bruta" in resultado and resultado["resposta_bruta"]:
            print(f"Resposta Bruta (falha no JSON): {resultado['resposta_bruta']}")
    else:
        print("Consulta realizada com sucesso!")
        # Imprime alguns dados do resultado (exemplo)
        print(f"Razão Social: {resultado.get('razao_social')}")
        print(f"Municipio: {resultado.get('municipio')}")
        print(f"Situação Cadastral: {resultado.get('forma_de_tributacao')}")