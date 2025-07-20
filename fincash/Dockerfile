FROM python:3.11-slim

WORKDIR /app

# Installer les dépendances système
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copier les fichiers de dépendances
COPY requirements.txt .

# Installer les dépendances Python
RUN pip install --no-cache-dir -r requirements.txt

# Copier le code source
COPY src/ ./src/

# Créer le dossier pour la base de données
RUN mkdir -p src/database

# Exposer le port
EXPOSE 5000

# Variable d'environnement pour Flask
ENV FLASK_APP=src/main.py
ENV FLASK_ENV=production

# Commande pour démarrer l'application
CMD ["python", "src/main.py"] 