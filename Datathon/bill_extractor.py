import requests
from io import BytesIO
from PIL import Image
from pytesseract import Output
import pytesseract

# Path to installed OCR executable
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"


# ---------------------------------------------------------
# Download image from URL
# ---------------------------------------------------------
def fetch_image(url: str) -> Image.Image:
    """
    Retrieves an image from the given HTTP URL.
    Returns a PIL Image instance.
    """
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    }

    response = requests.get(url, headers=headers, timeout=20)
    response.raise_for_status()

    return Image.open(BytesIO(response.content)).convert("RGB")


# ---------------------------------------------------------
# OCR wrappers
# ---------------------------------------------------------
def ocr_plain(img: Image.Image) -> str:
    """Perform basic OCR and return the recognized text."""
    return pytesseract.image_to_string(img)


def ocr_with_positions(img: Image.Image):
    """Return word-level OCR including bounding box coordinates."""
    return pytesseract.image_to_data(img, output_type=Output.DICT)


# ---------------------------------------------------------
# Convert OCR words into visually aligned rows
# ---------------------------------------------------------
def assemble_rows(ocr, y_gap=12):
    """
    Groups OCR tokens into horizontal text lines based on proximity of Y-coords.
    Returns: List[List[(x, text)]]
    """
    buffer = []
    current = []
    last_top = None

    for x, y, text in zip(ocr["left"], ocr["top"], ocr["text"]):
        token = text.strip()
        if not token:
            continue

        if last_top is None or abs(y - last_top) <= y_gap:
            current.append((x, token))
        else:
            buffer.append(sorted(current, key=lambda v: v[0]))
            current = [(x, token)]
        last_top = y

    if current:
        buffer.append(sorted(current, key=lambda v: v[0]))

    return buffer


# ---------------------------------------------------------
# Locate header row + determine column boundaries
# ---------------------------------------------------------
def detect_header_and_boundaries(rows):
    """
    Identifies the row containing the table header 
    and infers rough column split points using token x-positions.
    """
    header_idx = None
    header = None

    for idx, row in enumerate(rows):
        line = " ".join(t[1] for t in row).lower()
        if ("description" in line and "qty" in line and "rate" in line) or \
           ("qty" in line and "gross" in line):
            header_idx = idx
            header = row
            break

    if header is None:
        return None, None

    # determine approximate column x-locations
    x_desc = x_qty = x_rate = x_amount = None

    for x, word in header:
        w = word.lower()
        if "desc" in w:
            x_desc = x
        elif "qty" in w:
            x_qty = x
        elif "rate" in w:
            x_rate = x
        elif "gross" in w or "amount" in w or "net" in w:
            x_amount = x

    valid = [v for v in (x_desc, x_qty, x_rate, x_amount) if v is not None]
    valid.sort()

    borders = {}
    if len(valid) > 1:
        borders["desc_end"] = (valid[0] + valid[1]) / 2
    if len(valid) > 2:
        borders["qty_end"] = (valid[1] + valid[2]) / 2
    if len(valid) > 3:
        borders["rate_end"] = (valid[2] + valid[3]) / 2

    return header_idx, borders


# ---------------------------------------------------------
# Helpers
# ---------------------------------------------------------
def to_float(text):
    try:
        return float(text.replace(",", ""))
    except:
        return None


def remove_slno(desc: str):
    """Strip serial numbers at the start of the description field."""
    parts = desc.split()
    if parts and parts[0].isdigit():
        return " ".join(parts[1:])
    return desc


# ---------------------------------------------------------
# Parse table rows into structured line-tems 
# ---------------------------------------------------------
def extract_items(rows, header_idx, borders):
    """
    Converts each table row into JSON friendly objects.
    Returns: list of line-items
    """
    if header_idx is None or borders is None:
        return []

    items = []

    for row in rows[header_idx + 1:]:
        combined = " ".join(text for _, text in row).lower()

        # Skip totals or footer
        if "category total" in combined:
            continue
        if "printed" in combined:
            break

        desc_bucket = []
        qty_bucket = []
        rate_bucket = []
        amount_bucket = []

        for x, token in row:
            if borders.get("desc_end") and x < borders["desc_end"]:
                desc_bucket.append(token)
            elif borders.get("qty_end") and x < borders["qty_end"]:
                qty_bucket.append(token)
            elif borders.get("rate_end") and x < borders["rate_end"]:
                rate_bucket.append(token)
            else:
                amount_bucket.append(token)

        desc = remove_slno(" ".join(desc_bucket).strip())
        qty = to_float("".join(qty_bucket).strip())
        rate = to_float("".join(rate_bucket).strip())

        # amount: pick first numeric


        amount = None
        for t in amount_bucket:
            v = to_float(t)
            if v is not None:
                amount = v
                break

        if not desc or amount is None:
            continue

        items.append({
            "item_name": desc,
            "item_quantity": qty if qty is not None else 1.0,
            "item_rate": rate if rate is not None else amount,
            "item_amount": amount
        })

    return items


# ---------------------------------------------------------
# Main callable for FastAPI
# ---------------------------------------------------------
def extract_bill_info_from_url(url: str) -> dict:
    """
    Download image → OCR → parse rows → extract structured line-items.
    Returns final JSON response.
    """
    img = fetch_image(url)
    ocr = ocr_with_positions(img)

    rows = assemble_rows(ocr)

    header_idx, borders = detect_header_and_boundaries(rows)
    items = extract_items(rows, header_idx, borders)


    return {
        "is_success": True,
        "data": {
            "pagewise_line_items": [
                {
                    "page_no": "1",
                    "bill_items": items
                }
            ],
            "total_item_count": len(items),
            "reconciled_amount": sum(x["item_amount"] for x in items)
        }
    }
