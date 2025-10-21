# ==============================================================================
#                      MEMÓRIA VIVA - BACKEND (EUNOIA)
# ==============================================================================
# Versão: Fase C (Áudio) - Passo 4
#
# Funcionalidades:
# - Recebe memórias via texto ou áudio com geolocalização.
# - Faz upload do arquivo de áudio para o Cloudinary para armazenamento.
# - Transcreve o áudio para texto usando OpenAI Whisper.
# - Analisa o sentimento do texto (tradução + polaridade).
# - Converte a polaridade em uma cor de "Aura".
# - Salva a memória completa (incluindo a URL do áudio) no MongoDB.
# - Fornece todas as memórias para o mapa do front-end.
# ==============================================================================

# --- 1. IMPORTAÇÕES ---
from fastapi import FastAPI, UploadFile, File, Form, BackgroundTasks
from typing import Optional
from fastapi.middleware.cors import CORSMiddleware
import whisper
from textblob import TextBlob
import translators as ts
from pymongo import MongoClient
import shutil
import os
import uuid # Para criar nomes de arquivo únicos
import cloudinary
import cloudinary.uploader

# --- 2. CONFIGURAÇÃO INICIAL (Executa uma vez quando o servidor liga) ---

print("🚀 Iniciando Eunoia...")

# Carregando o modelo de IA Whisper
print("🧠 Carregando o modelo de IA Whisper (modelo 'tiny')...")
model = whisper.load_model("tiny")
print("✅ Modelo Whisper carregado com sucesso.")

# Conexão com o Banco de Dados MongoDB Atlas
# 
# !!! IMPORTANTE !!! COLE A SUA CONNECTION STRING ABAIXO.
MONGO_URI = "mongodb+srv://eunoia_user:Mus3euBarbosa_0212!@memoriavivacluster.15ck8oc.mongodb.net/?retryWrites=true&w=majority&appName=MemoriaVivaCluster" 
print("🛰️  Conectando ao banco de dados na nuvem...")
client = MongoClient(MONGO_URI)
db = client.memoria_viva_db
collection = db.memorias
print("✅ Conexão com o MongoDB Atlas estabelecida.")

# Configuração do Cloudinary (O Cofre de Vozes)
# 
# !!! IMPORTANTE !!! PREENCHA COM SUAS CREDENCIAIS DO CLOUDINARY.
print("☁️ Configurando o cofre de mídias Cloudinary...")
cloudinary.config( 
  cloud_name = "djibxb8vi", 
  api_key = "511969228892169", 
  api_secret = "F0D0msohlwyrUyzr9qp7dUzSABM" 
)
print("✅ Conexão com o Cloudinary estabelecida.")

# --- 3. APLICAÇÃO FASTAPI E CORS ---

app = FastAPI()

origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- 4. FUNÇÕES AUXILIARES ---

def polaridade_para_cor(polaridade: float) -> str:
    """Converte a polaridade de sentimento (-1 a +1) em uma cor hexadecimal."""
    if polaridade < 0:
        p = abs(polaridade)
        r, g, b = int(255 - (255 - 74) * p), int(255 - (255 - 144) * p), int(255 - (255 - 226) * p)
    else:
        p = polaridade
        r, g, b = int(255 - (255 - 245) * p), int(255 - (255 - 166) * p), int(255 - (255 - 35) * p)
    return f"#{r:02x}{g:02x}{b:02x}"

def processar_e_salvar_memoria(caminho_arquivo: str, lat: Optional[float], lon: Optional[float]):
    """Esta função faz todo o trabalho pesado em segundo plano."""
    print(f"---  Tarefa em Background iniciada para: {caminho_arquivo} ---")
    try:
        # 1. UPLOAD PARA O CLOUDINARY
        print("☁️ Fazendo upload do áudio para o Cloudinary...")
        # Usamos resource_type "video" pois o Cloudinary trata áudios como tal
        upload_result = cloudinary.uploader.upload(caminho_arquivo, resource_type = "video")
        audio_url = upload_result['secure_url']
        print(f"✅ Upload concluído. URL: {audio_url}")

        # 2. TRANSCRIÇÃO COM WHISPER
        print("🎤 Iniciando transcrição com Whisper...")
        result = model.transcribe(caminho_arquivo, language="pt", fp16=False)
        texto_processado = result["text"]
        print(f"🗣️ Texto Transcrito (BG): '{texto_processado}'")

        if not texto_processado.strip():
            print("🔇 A transcrição resultou em silêncio. Tarefa encerrada.")
            return

        # 3. ANÁLISE DE SENTIMENTO
        texto_en = ts.translate_text(texto_processado, translator='bing', to_language='en')
        blob_en = TextBlob(texto_en)
        polaridade = blob_en.sentiment.polarity
        cor_aura = polaridade_para_cor(polaridade)
        print(f"🎨 Análise (BG): Polaridade={polaridade:.2f}, Cor={cor_aura}")
        
        # 4. SALVAMENTO NO MONGODB
        memoria_para_salvar = { 
            "tipo": "audio", 
            "texto_original": texto_processado, 
            "cor_aura": cor_aura,
            "audio_url": audio_url  # A nova informação!
        }
        if lat is not None and lon is not None:
            memoria_para_salvar["localizacao"] = {"lat": lat, "lon": lon}
        collection.insert_one(memoria_para_salvar)
        print("💾 Memória de áudio (com URL) salva no MongoDB (BG)!")

    except Exception as e:
        print(f"🚨 ERRO na tarefa de background: {e}")
    finally:
        # 5. LIMPEZA DO ARQUIVO TEMPORÁRIO
        if os.path.exists(caminho_arquivo):
            os.remove(caminho_arquivo)
            print(f"🗑️ Arquivo temporário {caminho_arquivo} deletado.")

# --- 5. ROTAS DA API ---

@app.post("/doar")
async def receber_memoria(
    background_tasks: BackgroundTasks,
    texto: Optional[str] = Form(None), 
    lat: Optional[float] = Form(None), 
    lon: Optional[float] = Form(None), 
    audio_file: Optional[UploadFile] = File(None)
):
    """Rota que recebe a doação e dispara o processamento em background."""
    if audio_file:
        nome_arquivo_unico = f"temp_{uuid.uuid4()}.webm"
        with open(nome_arquivo_unico, "wb") as buffer:
            shutil.copyfileobj(audio_file.file, buffer)
        
        background_tasks.add_task(processar_e_salvar_memoria, nome_arquivo_unico, lat, lon)
        
        print("✅ Pedido de áudio recebido. Processamento em background iniciado.")
        return {"status": "sucesso", "mensagem": "Sua memória de áudio foi recebida e está sendo processada por Eunoia. Obrigado!"}

    elif texto:
        # A lógica para texto continua a mesma (é rápida, não precisa de background task)
        texto_en = ts.translate_text(texto, translator='bing', to_language='en')
        polaridade = TextBlob(texto_en).sentiment.polarity
        cor_aura = polaridade_para_cor(polaridade)
        memoria_para_salvar = {"tipo": "texto", "texto_original": texto, "cor_aura": cor_aura}
        if lat is not None and lon is not None:
            memoria_para_salvar["localizacao"] = {"lat": lat, "lon": lon}
        collection.insert_one(memoria_para_salvar)
        print("💾 Memória de texto salva no MongoDB!")
        return {"status": "sucesso", "mensagem": "Memória de texto recebida."}
    
    return {"status": "erro", "mensagem": "Nenhum dado recebido."}


@app.get("/memorias")
def get_memorias():
    """Rota que envia todas as memórias com localização para o mapa."""
    memorias_salvas = []
    for memoria in collection.find({}):
        if "localizacao" in memoria:
            memoria["_id"] = str(memoria["_id"])
            memoria["lat"] = memoria["localizacao"]["lat"]
            memoria["lon"] = memoria["localizacao"]["lon"]
            memorias_salvas.append(memoria)
    return memorias_salvas

@app.get("/")
def read_root():
    return {"message": "Eunoia está online e ouvindo a alma do mundo."}

print("✅ Eunoia está pronta e esperando por memórias.")


# Forçando o redeploy no Railway