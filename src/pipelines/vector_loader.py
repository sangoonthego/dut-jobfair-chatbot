from src.pipelines.semantic_chunker import JobDescriptionChunker

chunker = JobDescriptionChunker(target_size=400, overlap=0.15)

raw_jd_text = "..." 
meta = {
    "company_name": "FPT Software",
    "job_title": "AI Engineer"
}

chunks = chunker.chunk_job_description(raw_jd_text, meta)