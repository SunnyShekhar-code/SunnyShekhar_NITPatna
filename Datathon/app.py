# from fastapi import FastAPI
# from pydantic import BaseModel
# from bill_extractor import extract_bill_info_from_url


# app = FastAPI()

# class RequestBody(BaseModel):
#     document: str   # URL of the bill  image

# # uvicorn app:app --reload
# @app.post("/extract-bill-data")
# def extract_data(body: RequestBody):
#     """
#     Endpoint that accepts a URL to an image and returns the structured
#     bill line-items extracted via OCR.
#     """
#     try:
#         output = extract_bill_info_from_url(body.document)
#         return output
#     except Exception as exc:
#         return {
#             "is_success": False,
#             "data": None,
#             "error": str(exc)
#         }




from fastapi import FastAPI
from pydantic import BaseModel
from bill_extractor import extract_bill_info_from_url

app = FastAPI()


class RequestBody(BaseModel):
    document: str   # URL of the bill image


@app.post("/extract-bill-data")
def extract_data(body: RequestBody):
    """
    Main API — returns structured bill items in EXACT Datathon format.
    """
    try:
        result = extract_bill_info_from_url(body.document)
        return result
    except Exception as exc:
        # Follow Datathon error schema as closely as possible
        return {
            "is_success": False,
            "token_usage": {
                "total_tokens": 0,
                "input_tokens": 0,
                "output_tokens": 0
            },
            "data": None
        }

