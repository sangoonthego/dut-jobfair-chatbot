import os
from llama_index.core import Settings
from llama_index.llms.ollama import Ollama
from llama_index.embeddings.huggingface import HuggingFaceEmbedding

def init_settings():
    # Chỉ dùng HF_HOME để nó tự tìm vào thư mục hub
    os.environ["HF_HOME"] = r"D:\huggingface_cache"
    
    Settings.llm = Ollama(
        model="qwen2.5:1.5b", 
        request_timeout=300.0
    )
    
    # Ở đây CHỈ để model_name, KHÔNG để cache_folder nữa để nó dùng HF_HOME
    Settings.embed_model = HuggingFaceEmbedding(
        model_name="BAAI/bge-m3"
    )

    Settings.chunk_size = 512
    Settings.chunk_overlap = 50