import os
import pyodbc
from fastmcp import FastMCP

# Inicializa o servidor MCP
mcp = FastMCP("Estrela DB Explorer")

def get_connection(database_override=None):
    server = os.environ.get("DB_SERVER") 
    user = os.environ.get("DB_USER")
    password = os.environ.get("DB_PASS")
    database = database_override or os.environ.get("DB_NAME", "Estrela")

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
def testar_conexao() -> str:
    """Testa se o servidor consegue falar com o banco de dados."""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT @@VERSION")
        versao = cursor.fetchone()[0]
        conn.close()
        return f"Conexão OK! Versão: {versao}"
    except Exception as e:
        return f"Falha na conexão: {str(e)}"

@mcp.tool()
def listar_bancos() -> str:
    """Lista todos os bancos de dados disponíveis no servidor."""
    try:
        conn = get_connection(database_override="master")
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sys.databases WHERE database_id > 4 ORDER BY name")
        rows = cursor.fetchall()
        conn.close()
        if not rows: return "Nenhum banco encontrado."
        return "Bancos encontrados:\n" + "\n".join([f"- {r[0]}" for r in rows])
    except Exception as e:
        return f"Erro: {str(e)}"

@mcp.tool()
def listar_tabelas() -> str:
    """Lista todas as tabelas do banco de dados."""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT TABLE_SCHEMA, TABLE_NAME 
            FROM INFORMATION_SCHEMA.TABLES 
            WHERE TABLE_TYPE = 'BASE TABLE'
            ORDER BY TABLE_SCHEMA, TABLE_NAME
        """)
        rows = cursor.fetchall()
        conn.close()
        if not rows: return "Nenhuma tabela encontrada."
        return "Tabelas:\n" + "\n".join([f"- {r[0]}.{r[1]}" for r in rows])
    except Exception as e:
        return f"Erro: {str(e)}"

@mcp.tool()
def executar_consulta(sql: str) -> str:
    """Executa uma consulta SELECT e retorna os resultados."""
    if not sql.strip().upper().startswith("SELECT"):
        return "Erro: Apenas consultas SELECT são permitidas."
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(sql)
        colunas = [column[0] for column in cursor.description]
        rows = cursor.fetchall()
        conn.close()
        
        if not rows: return "A consulta não retornou resultados."
        
        res = " | ".join(colunas) + "\n" + "-" * 50 + "\n"
        for r in rows:
            res += " | ".join(str(v) for v in r) + "\n"
        return res
    except Exception as e:
        return f"Erro: {str(e)}"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    mcp.run(
        transport="streamable-http", host="0.0.0.0", port=port,
        path="/mcp", stateless_http=True
    )