import json
import os

MEMORY_FILE = r"E:\my_japan_blog\auto\written_products.json"

def load_written_products():
    if not os.path.exists(MEMORY_FILE):
        return []
    with open(MEMORY_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
        return data.get("written", [])

def save_written_products(new_products):
    """追加写入新商品"""
    written = load_written_products()
    for p in new_products:
        if p not in written:
            written.append(p)
    with open(MEMORY_FILE, "w", encoding="utf-8") as f:
        json.dump({"written": written}, f, ensure_ascii=False, indent=2)
