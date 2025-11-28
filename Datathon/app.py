from fastapi import FastAPI
from pydantic import BaseModel
from bill_extractor import extract_bill_info_from_url


app = FastAPI()

class RequestBody(BaseModel):
    document: str   # URL of the bill  image

# uvicorn app:app --reload
@app.post("/extract-bill-data")
def extract_data(body: RequestBody):
    """
    Endpoint that accepts a URL to an image and returns the structured
    bill line-items extracted via OCR.
    """
    try:
        output = extract_bill_info_from_url(body.document)
        return output
    except Exception as exc:
        return {
            "is_success": False,
            "data": None,
            "error": str(exc)
        }
