import os
from dotenv import load_dotenv
from llama_index.core import Settings
from llama_index.llms.ollama import Ollama
from llama_index.embeddings.huggingface import HuggingFaceEmbedding

def init_settings():
    load_dotenv()
    
    cache_path = os.getenv("HF_HOME", r"D:\huggingface_cache")
    os.environ["HF_HOME"] = cache_path

    Settings.llm = Ollama(
        model="qwen2.5:1.5b", 
        request_timeout=300.0
    )
    
    Settings.embed_model = HuggingFaceEmbedding(
        model_name="BAAI/bge-m3"
    )

    Settings.chunk_size = 512
    Settings.chunk_overlap = 50