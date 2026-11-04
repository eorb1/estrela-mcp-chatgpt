import os
import pyodbc
from fastmcp import FastMCP

mcp = FastMCP("Estrela DB Explorer")

def get_connection():
    # Pega as variáveis do Render
    server = os.environ.get("DB_SERVER") # Ex: 138.0.xxx.xxx,1433
    user = os.environ.get("DB_USER")
    password = os.environ.get("DB_PASS")
    database = os.environ.get("DB_NAME", "master") # Se não tiver o nome, tenta o 'master' só pra testar a conexão
    
    # String de conexão forçando TCP/IP e ignorando validação de certificado
    conn_str = (
        f"DRIVER={{ODBC Driver 18 for SQL Server}};"
        f"SERVER={server};"
        f"DATABASE={database};"
        f"UID={user};"
        f"PWD={password};"
        f"Encrypt=yes;"
        f"TrustServerCertificate=yes;" # ESSENCIAL para IPs sem certificado SSL
    )
    
    try:
        return pyodbc.connect(conn_str, timeout=10)
    except Exception as e:
        print(f"ERRO DE CONEXAO: {str(e)}")
        raise e

@mcp.tool()
def testar_conexao() -> str:
    """Testa se o servidor Render consegue falar com o banco de dados."""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT @@VERSION")
        versao = cursor.fetchone()[0]
        conn.close()
        return f"Conexão bem-sucedida! Versão do SQL Server: {versao}"
    except Exception as e:
        return f"Falha na conexão. Verifique o Firewall do servidor ou a senha. Erro: {str(e)}"

@mcp.tool()
def listar_bancos() -> str:
    """Lista todos os bancos de dados disponíveis neste servidor."""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sys.databases WHERE database_id > 4")
        rows = cursor.fetchall()
        conn.close()
        
        if not rows:
            return "Conexão ok, mas nenhum banco de usuário foi encontrado."
            
        lista = "Bancos encontrados:\n" + "\n".join([f"- {r[0]}" for r in rows])
        return lista
    except Exception as e:
        return f"Erro ao listar bancos: {str(e)}"

# --- As outras funções (listar_tabelas, descrever_tabela, executar_consulta) entram aqui embaixo ---

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    mcp.run(
        transport="streamable-http",
        host="0.0.0.0",
        port=port,
        path="/mcp",              # Garante que o endpoint seja /mcp
        stateless_http=True       # Evita problemas de estado entre requisições
    )