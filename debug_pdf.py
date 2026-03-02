import asyncio
import sys
import os

# Ensure the backend directory is in the path
sys.path.insert(0, ".")

from backend.services.ingestion import IngestionService

async def main():
    pdf_path = r"c:\Users\naman\Desktop\Text Formatter\6943d03962174_3. Motion In A Plane.pdf.pdf"
    print(f"Reading: {pdf_path}")
    
    with open(pdf_path, "rb") as f:
        file_bytes = f.read()

    from backend.services.normalizer import normalize
    
    # We just want the raw text to see what the normalizer sees
    try:
        result = IngestionService.process_file(pdf_path, ".pdf")
        text = result["raw_text"]
        
        norm_result = normalize(text)
        exam = norm_result.exam
        
        print(f"Total Questions detected: {exam.total_questions}")
        print(f"Total Warnings: {len(norm_result.warnings)}")
        
        for q in exam.questions[:5]:
            print(f"\n--- Q{q.id} ---")
            print(q.text)
            for opt in q.options:
                print(f"  [{opt.label}] {opt.text}")
                
        print("\nWarnings sample:")
        for w in norm_result.warnings[:5]:
            print(f"  {w}")

    except Exception as e:
        print(f"Error during extraction: {e}")

if __name__ == "__main__":
    asyncio.run(main())
