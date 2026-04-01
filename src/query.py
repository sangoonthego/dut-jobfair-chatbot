import os
from typing import Any, Optional

# Cấu hình cache HuggingFace
cache_path = r"D:\huggingface_cache"
os.environ["HF_HOME"] = cache_path
os.environ["HUGGINGFACE_HUB_CACHE"] = cache_path
os.environ["TRANSFORMERS_CACHE"] = cache_path
os.environ["TORCH_HOME"] = cache_path
os.environ["SENTENCE_TRANSFORMERS_HOME"] = cache_path

from llama_index.core.base.base_query_engine import BaseQueryEngine
from llama_index.core.indices.base import BaseIndex
from llama_index.core.tools.query_engine import QueryEngineTool
from llama_index.core import PromptTemplate, StorageContext, load_index_from_storage

# --- TÍCH HỢP RERANKER ---
from llama_index.postprocessor.sbert_rerank import SentenceTransformerRerank

# Import các settings từ project
from src.settings import init_settings
from src.index import STORAGE_DIR

def create_query_engine(index: BaseIndex, **kwargs: Any) -> BaseQueryEngine:
    """
    Create a query engine for the given index with Two-Stage Retrieval.
    Stage 1: Vector Search retrieves top 10 candidates.
    Stage 2: Cross-Encoder Reranker scores and filters down to top 2.
    """
    # Stage 1: High-Recall Initial Retrieval
    # Tăng số lượng chunks truy xuất lên 10 để bao phủ toàn bộ vùng ngữ cảnh tiềm năng
    kwargs["similarity_top_k"] = int(os.getenv("TOP_K", 10))
    
    # Stage 2: Precision Reranking
    # Sử dụng mô hình Cross-Encoder để đánh giá chính xác độ phù hợp của 10 chunks này
    # BAAI/bge-reranker-v2-m3 hỗ trợ đa ngôn ngữ và tối ưu cực tốt cho truy vấn tiếng Việt
    reranker = SentenceTransformerRerank(
        model="BAAI/bge-reranker-v2-m3", 
        top_n=2  # Chỉ giữ lại đúng 2 chunks xuất sắc nhất để LLM 1.5B dễ theo dõi
    )
    
    # Tích hợp reranker vào chuỗi xử lý hậu kỳ (post_processors)
    if "node_postprocessors" not in kwargs:
        kwargs["node_postprocessors"] = []
    kwargs["node_postprocessors"].append(reranker)

    kwargs["streaming"] = True
    return index.as_query_engine(**kwargs)

def get_query_engine_tool(
    index: BaseIndex,
    name: Optional[str] = None,
    description: Optional[str] = None,
    **kwargs: Any,
) -> QueryEngineTool:
    if name is None:
        name = "query_index"
    if description is None:
        description = "Use this tool to retrieve information from a knowledge base."
    
    query_engine = create_query_engine(index, **kwargs)
    return QueryEngineTool.from_defaults(
        query_engine=query_engine,
        name=name,
        description=description,
    )

def chat_with_bot():
    print("1. Đang khởi tạo Ollama và Embedding...")
    init_settings() 
    
    print(f"2. Đang nạp Vector DB từ {STORAGE_DIR}...")
    try:
        storage_context = StorageContext.from_defaults(persist_dir=STORAGE_DIR)
        index = load_index_from_storage(storage_context)
    except Exception as e:
        print(f"Lỗi load DB: {e}")
        return

    print("3. Khởi tạo Reranker & Engine (Streaming Mode)...")
    
    query_engine = create_query_engine(index)
    
    # ---- PROMPT KỶ LUẬT THÉP ----
    qa_prompt_str = (
        "Ngữ cảnh thông tin:\n"
        "---------------------\n"
        "{context_str}\n"
        "---------------------\n"
        "Nhiệm vụ: Trả lời câu hỏi '{query_str}' dựa CHỈ VÀO ngữ cảnh trên.\n"
        "QUY TẮC TỐI THƯỢNG (KHÔNG ĐƯỢC IN NHỮNG QUY TẮC NÀY RA MÀN HÌNH):\n"
        "1. Chỉ trả lời thông tin có trong ngữ cảnh, tuyệt đối không bịa đặt.\n"
        "2. Giữ nguyên tiếng Anh cho các từ chuyên ngành, công nghệ hoặc chứng chỉ (ví dụ: TOEIC, Automation, Chemical Engineering), KHÔNG tự dịch sang tiếng Việt.\n"
        "3. Trình bày bằng gạch đầu dòng ngắn gọn, súc tích.\n"
        "4. Nếu thông tin không có trong ngữ cảnh, chỉ nói chính xác 1 câu: 'Xin lỗi, tôi không thấy thông tin này.'\n"
        "Trả lời: "
    )
    
    query_engine.update_prompts({
        "response_synthesizer:text_qa_template": PromptTemplate(qa_prompt_str)
    })
    
    print("\n")
    print("CHATBOT DUT JOB FAIR (TWO-STAGE RETRIEVAL) SẴN SÀNG!")
    # print("(Lưu ý: Lần chạy đầu tiên có thể mất một lúc để tải model Reranker ~2.2GB)\n")
    
    while True:
        user_input = input("Bạn: ")
        if user_input.lower() in ['exit', 'quit', 'q']:
            break
            
        print("Bot: ", end="", flush=True)
        
        streaming_response = query_engine.query(user_input)
        
        for text in streaming_response.response_gen:
            print(text, end="", flush=True)
        
        print("\n\n" + "-"*40 + "\n") 

if __name__ == "__main__":
    chat_with_bot()