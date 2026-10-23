"""Run explicitly whenever the PDF or embedding model changes."""
import hashlib
import json
import shutil
import time
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from common import ROOT, embeddings

def ingest():
    pdf = ROOT / "hr_manual.pdf"
    if not pdf.exists():
        raise ValueError("Place the supplied Enso HR manual at hr_manual.pdf first.")
    pages = PyPDFLoader(str(pdf)).load()
    empty = [i + 1 for i, page in enumerate(pages) if not page.page_content.strip()]
    if empty:
        raise ValueError(f"Pages {empty} have no text. Obtain a readable/OCR copy before ingesting.")
    if not pages:
        raise ValueError("The PDF has no readable pages.")
    chunks = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=150).split_documents(pages)
    model = embeddings()
    staging = ROOT / "chroma_db_build"
    if staging.exists():
        shutil.rmtree(staging)
    store = Chroma(collection_name="hr_policy", embedding_function=model, persist_directory=str(staging))
    # Keep below Gemini's free-tier request limit; retry transient quota limits.
    for start in range(0, len(chunks), 40):
        batch = chunks[start:start + 40]
        for attempt in range(4):
            try:
                store.add_documents(batch, ids=[f"chunk-{i}" for i in range(start, start + len(batch))])
                break
            except Exception as exc:
                if "429" not in str(exc) or attempt == 3:
                    raise
                print("Gemini rate limit: waiting 55 seconds before retrying.", flush=True)
                time.sleep(55)
        print(f"Stored {min(start + 40, len(chunks))}/{len(chunks)} chunks", flush=True)
        if start + 40 < len(chunks):
            time.sleep(30)
    manifest = {"embedding_model": model.model, "sha256": hashlib.sha256(pdf.read_bytes()).hexdigest(), "pages": len(pages), "chunks": len(chunks)}
    (staging / "manifest.json").write_text(json.dumps(manifest))
    # Chroma may hold open file handles; POSIX permits this directory rename.
    target = ROOT / "chroma_db"
    if target.exists():
        shutil.rmtree(target)
    staging.rename(target)
    print(f"Ingested {len(pages)} pages and {len(chunks)} chunks. Citations use PDF viewer pages.")

if __name__ == "__main__":
    try:
        ingest()
    except Exception as exc:
        raise SystemExit(f"Ingestion failed: {exc}")
