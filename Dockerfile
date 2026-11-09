FROM python:3.11-slim

# Instala dependências do sistema e o driver ODBC para SQL Server
RUN apt-get update && apt-get install -y \
    curl \
    gnupg2 \
    unixodbc-dev \
    && rm -rf /var/lib/apt/lists/*

# Adiciona a chave da Microsoft (método moderno com gpg)
RUN curl -fsSL https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor -o /usr/share/keyrings/microsoft-archive-keyring.gpg

# Adiciona o repositório da Microsoft para Debian 12 (Bookworm)
RUN echo "deb [arch=amd64,arm64,armhf signed-by=/usr/share/keyrings/microsoft-archive-keyring.gpg] https://packages.microsoft.com/debian/12/prod bookworm main" > /etc/apt/sources.list.d/mssql-release.list

# Instala o driver ODBC 18
RUN apt-get update && ACCEPT_EULA=Y apt-get install -y msodbcsql18 && apt-get clean && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# O Render usa a variável PORT automaticamente
CMD ["python", "app.py"]
