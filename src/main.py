from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from llama_index.core import StorageContext, load_index_from_storage

from src.settings import init_settings
from src.index import STORAGE_DIR
from src.query import create_hybrid_query_engine 

app = FastAPI(title="DUT JobFair RAG API")

# Cấu hình CORS để Flutter gọi không bị chặn
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    message: str

# Biến global để lưu trữ engine
query_engine = None

@app.on_event("startup")
async def startup_event():
    global query_engine
    print("1. Khởi tạo Settings (Ollama + BGE-M3)...")
    init_settings()
    
    print(f"2. Load dữ liệu từ {STORAGE_DIR}...")
    try:
        storage_context = StorageContext.from_defaults(persist_dir=STORAGE_DIR)
        index = load_index_from_storage(storage_context)
    except Exception as e:
        print(f"Lỗi Load Database. Hãy chạy file pipeline trước! Chi tiết: {e}")
        return
        
    print("3. Khởi tạo Hybrid Engine...")
    query_engine = create_hybrid_query_engine(index)
    print("🚀 API ĐÃ SẴN SÀNG NHẬN REQUEST TỪ FLUTTER!")

@app.post("/api/chat")
async def chat_endpoint(request: ChatRequest):
    if not query_engine:
        raise HTTPException(status_code=500, detail="AI Engine chưa khởi tạo xong.")
    
    try:
        # Gửi query tới LlamaIndex
        response = query_engine.query(request.message)
        
        # Bóc tách metadata để trả về cho Flutter làm UI "Trích dẫn nguồn"
        citations = []
        for node in response.source_nodes:
            meta = node.node.metadata
            citations.append({
                "company": meta.get('company_name', 'N/A'),
                "job": meta.get('job_title', 'N/A'),
                "score": round(node.score, 4)
            })
            
        return {
            "reply": str(response),
            "citations": citations
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))