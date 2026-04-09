import logging
import os

from llama_index.core.indices import load_index_from_storage
from llama_index.core.storage import StorageContext

logger = logging.getLogger("uvicorn")

STORAGE_DIR = "src/storage"


def get_index():
    # check if storage already exists
    if not os.path.exists(STORAGE_DIR):
        return None
    # load the existing index
    logger.info(f"Loading index from {STORAGE_DIR}...")
    storage_context = StorageContext.from_defaults(persist_dir=STORAGE_DIR)
    index = load_index_from_storage(storage_context)
    logger.info(f"Finished loading index from {STORAGE_DIR}")
    return index

def get_query_engine():
    index = get_index()
    if index is None:
        logger.error("Index không tồn tại! Hãy chạy pipeline để tạo data trước.")
        return None
    # Ở đây ông có thể cấu hình thêm similarity_top_k để lấy bao nhiêu kết quả liên quan
    return index.as_query_engine(similarity_top_k=3)