import os
import logging
from huggingface_hub import HfApi, create_repo

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def setup_hf_repo():
    """Configura el repositorio en Hugging Face"""
    try:
        HF_TOKEN = os.getenv("HF_TOKEN")
        REPO_NAME = "daniel-ai-assistant"  # Cambia por tu usuario
        
        # Crear repositorio
        create_repo(
            REPO_NAME,
            token=HF_TOKEN,
            repo_type="model",
            exist_ok=True
        )
        
        logger.info(f"✅ Repositorio {REPO_NAME} configurado en Hugging Face")
        
    except Exception as e:
        logger.error(f"❌ Error configurando HF repo: {str(e)}")

if __name__ == "__main__":
    setup_hf_repo()
