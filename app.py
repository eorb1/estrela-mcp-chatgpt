import os
import pyodbc
from fastmcp import FastMCP

mcp = FastMCP("Estrela DB Explorer")

def get_connection(database_override=None):
    server = os.environ.get("DB_SERVER") 
    user = os.environ.get("DB_USER")
    password = os.environ.get("DB_PASS")
    # Se database_override for passado, usa ele. Senão, usa o DB_NAME do Render.
    database = database_override or os.environ.get("DB_NAME")

    conn_str = (
        f"DRIVER={{ODBC Driver 18 for SQL Server}};"
        f"SERVER={server};"
        f"DATABASE={database};"
        f"UID={user};"
        f"PWD={password};"
        f"Encrypt=yes;"
        f"TrustServerCertificate=yes;"
    )
    return pyodbc.connect(conn_str, timeout=10, readonly=True)

@mcp.tool()
def listar_bancos() -> str:
    """Lista todos os bancos de dados disponíveis no servidor (ignora o DB_NAME atual)."""
    try:
        # Força a conexão no banco 'master' para poder listar todos
        conn = get_connection(database_override="master")
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sys.databases WHERE database_id > 4 ORDER BY name")
        rows = cursor.fetchall()
        conn.close()
        
        if not rows:
            return "Nenhum banco encontrado (ou sem permissão)."
            
        return "Bancos encontrados:\n" + "\n".join([f"- {r[0]}" for r in rows])
    except Exception as e:
        return f"Erro ao listar bancos: {str(e)}"

@mcp.tool()
def testar_conexao() -> str:
    """Testa se o servidor Render consegue falar com o banco de dados."""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT @@VERSION")
        versao = cursor.fetchone()[0]
        conn.close()
        return f"Conexão bem-sucedida! Versão: {versao}"
    except Exception as e:
        return f"Falha na conexão: {str(e)}"

# ... (mantenha as outras ferramentas listar_tabelas e executar_consulta aqui embaixo, iguais)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    mcp.run(
        transport="streamable-http", host="0.0.0.0", port=port,
        path="/mcp", stateless_http=True
    )