import os
import pyodbc
from fastapi import FastAPI
from pydantic import BaseModel

# Inicializa a API REST para o ChatGPT
app = FastAPI(
    title="Estrela DB API",
    description="API para consultar o banco de dados SQL Server",
    version="1.0.0"
)

class ConsultaInput(BaseModel):
    sql: str

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

@app.get("/testar_conexao", summary="Testa a conexão com o banco")
def testar_conexao():
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT @@VERSION")
        versao = cursor.fetchone()[0]
        conn.close()
        return {"status": "Conexão OK", "versao": versao}
    except Exception as e:
        return {"status": "Falha na conexão", "erro": str(e)}

@app.get("/listar_tabelas", summary="Lista todas as tabelas")
def listar_tabelas():
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT TABLE_SCHEMA, TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_TYPE = 'BASE TABLE'")
        rows = cursor.fetchall()
        conn.close()
        tabelas = [f"{r[0]}.{r[1]}" for r in rows]
        return {"tabelas": tabelas}
    except Exception as e:
        return {"erro": str(e)}

@app.post("/executar_consulta", summary="Executa uma consulta SELECT")
def executar_consulta(dados: ConsultaInput):
    sql = dados.sql
    if not sql.strip().upper().startswith("SELECT"):
        return {"erro": "Apenas consultas SELECT são permitidas."}
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(sql)
        colunas = [column[0] for column in cursor.description]
        rows = cursor.fetchall()
        conn.close()
        
        if not rows: 
            return {"resultado": "A consulta não retornou resultados."}
        
        # Formata o resultado
        res = " | ".join(colunas) + "\n" + "-" * 50 + "\n"
        for r in rows:
            res += " | ".join(str(v) for v in r) + "\n"
        return {"resultado": res}
    except Exception as e:
        return {"erro": str(e)}

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
