# OCR Extraction API
    - A FastAPI-based application that extracts line items, quantities, rates, and amounts from bill/invoice images using Tesseract OCR.
    This project supports remote image URLs, performs OCR, detects table structures, and returns structured JSON output.

1. OCR-Based Text Extraction
   Extracts text from bill images using Tesseract OCR
   Supports colored, scanned, and smartphone photos

2. Automatic Table Line-Item Detection
   Automatically identifies header columns such as:
   Item Description
   Quantity
   Rate
  Gross / Net Amount
  Reconstructs rows based on word positions (x/y coordinates)

3. Clean Structured Output

4. Simple FastAPI Endpoint
   Accepts a URL of the bill image
   Returns structured bill items
   Built-in error handling
   
5. Fully Modular Code
   OCR pipeline separated into bill_extractor.py
   API in app.py
    