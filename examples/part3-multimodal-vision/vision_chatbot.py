#!/usr/bin/env python3
"""
Multimodal Vision Chatbot
-------------------------
A complete image analysis system supporting:
- Basic image understanding
- Invoice/receipt OCR with structured extraction
- Batch image processing
- Interactive Streamlit UI

Usage:
    # Basic image analysis
    python vision_chatbot.py analyze photo.jpg "What's in this image?"
    
    # Invoice extraction
    python vision_chatbot.py invoice receipt.png
    
    # Batch processing
    python vision_chatbot.py batch ./photos "Describe what you see"
    
    # Interactive UI
    streamlit run vision_chatbot.py

Prerequisites:
    pip install openai pillow streamlit
    export OPENAI_API_KEY="sk-xxx"
"""

import openai
import base64
import json
import os
import sys
from pathlib import Path
from typing import Optional, List, Dict
from concurrent.futures import ThreadPoolExecutor
import argparse

# Initialize OpenAI client
client = openai.OpenAI()


# =============================================================================
# Core Vision Functions
# =============================================================================

def encode_image(image_path: str) -> tuple[str, str]:
    """
    Encode image to base64 and detect MIME type
    
    Returns:
        (base64_data, mime_type)
    """
    with open(image_path, "rb") as f:
        image_data = base64.b64encode(f.read()).decode()
    
    ext = Path(image_path).suffix.lower().lstrip('.')
    mime_map = {
        "png": "image/png",
        "jpg": "image/jpeg",
        "jpeg": "image/jpeg",
        "gif": "image/gif",
        "webp": "image/webp"
    }
    mime = mime_map.get(ext, "image/png")
    
    return image_data, mime


def analyze_image(
    image_path: str,
    question: str = "Describe this image in detail.",
    model: str = "gpt-4o-mini",
    max_tokens: int = 500
) -> str:
    """
    Analyze a single image with GPT-4o vision
    
    Args:
        image_path: Path to image file
        question: Question to ask about the image
        model: OpenAI vision model (gpt-4o-mini recommended for cost)
        max_tokens: Max response length
        
    Returns:
        AI's response text
        
    Example:
        >>> result = analyze_image("photo.jpg", "How many people are in this photo?")
        >>> print(result)
    """
    image_data, mime = encode_image(image_path)
    
    response = client.chat.completions.create(
        model=model,
        messages=[{
            "role": "user",
            "content": [
                {"type": "text", "text": question},
                {
                    "type": "image_url",
                    "image_url": {"url": f"data:{mime};base64,{image_data}"}
                }
            ]
        }],
        max_tokens=max_tokens
    )
    
    return response.choices[0].message.content


def extract_invoice(
    image_path: str,
    model: str = "gpt-4o-mini"
) -> Dict:
    """
    Extract structured data from invoice/receipt image
    
    Returns JSON with fields:
        - vendor: Store/vendor name
        - date: Transaction date (YYYY-MM-DD)
        - items: List of {name, quantity, price}
        - subtotal, tax, total
        - currency: Currency code (USD, EUR, etc.)
        - payment_method: Payment type
        
    Example:
        >>> data = extract_invoice("receipt.png")
        >>> print(f"Total: {data['currency']} {data['total']}")
    """
    image_data, mime = encode_image(image_path)
    
    prompt = """Extract information from this invoice/receipt and return as JSON:
{
    "vendor": "Store name",
    "date": "YYYY-MM-DD",
    "items": [
        {"name": "Item name", "quantity": 1, "price": 10.50}
    ],
    "subtotal": 100.00,
    "tax": 8.00,
    "total": 108.00,
    "currency": "USD",
    "payment_method": "Credit Card"
}

If any field is not present, use null. Return ONLY valid JSON, no markdown or extra text."""
    
    response = client.chat.completions.create(
        model=model,
        messages=[{
            "role": "user",
            "content": [
                {"type": "text", "text": prompt},
                {
                    "type": "image_url",
                    "image_url": {"url": f"data:{mime};base64,{image_data}"}
                }
            ]
        }],
        max_tokens=1000,
        response_format={"type": "json_object"}
    )
    
    return json.loads(response.choices[0].message.content)


def batch_analyze(
    folder_path: str,
    prompt: str,
    max_workers: int = 5,
    extensions: set = {".png", ".jpg", ".jpeg", ".gif", ".webp"}
) -> List[Dict]:
    """
    Analyze all images in a folder concurrently
    
    Args:
        folder_path: Directory containing images
        prompt: Question to ask for each image
        max_workers: Number of concurrent requests
        extensions: Image file extensions to process
        
    Returns:
        List of {"file": path, "result": answer} dicts
        
    Example:
        >>> results = batch_analyze("./photos", "What objects are visible?")
        >>> for r in results:
        >>>     print(f"{r['file']}: {r['result']}")
    """
    folder = Path(folder_path)
    image_files = [
        str(f) for f in folder.iterdir()
        if f.suffix.lower() in extensions
    ]
    
    if not image_files:
        return []
    
    def process_one(path: str) -> Dict:
        try:
            result = analyze_image(path, prompt, max_tokens=300)
            return {"file": path, "result": result}
        except Exception as e:
            return {"file": path, "error": str(e)}
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        results = list(executor.map(process_one, image_files))
    
    return results


# =============================================================================
# CLI Interface
# =============================================================================

def cli_analyze(args):
    """CLI handler for image analysis"""
    result = analyze_image(args.image, args.question)
    print(result)


def cli_invoice(args):
    """CLI handler for invoice extraction"""
    data = extract_invoice(args.image)
    print(json.dumps(data, indent=2, ensure_ascii=False))


def cli_batch(args):
    """CLI handler for batch processing"""
    results = batch_analyze(args.folder, args.question, max_workers=args.workers)
    
    for item in results:
        print(f"\n{'='*60}")
        print(f"File: {item['file']}")
        print(f"{'='*60}")
        if "error" in item:
            print(f"ERROR: {item['error']}")
        else:
            print(item['result'])


def main_cli():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="Multimodal Vision AI Chatbot",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    subparsers = parser.add_subparsers(dest="command", required=True)
    
    # analyze command
    analyze_parser = subparsers.add_parser("analyze", help="Analyze a single image")
    analyze_parser.add_argument("image", help="Path to image file")
    analyze_parser.add_argument("question", nargs="?", default="Describe this image in detail.")
    analyze_parser.set_defaults(func=cli_analyze)
    
    # invoice command
    invoice_parser = subparsers.add_parser("invoice", help="Extract invoice/receipt data")
    invoice_parser.add_argument("image", help="Path to invoice image")
    invoice_parser.set_defaults(func=cli_invoice)
    
    # batch command
    batch_parser = subparsers.add_parser("batch", help="Batch process folder of images")
    batch_parser.add_argument("folder", help="Folder containing images")
    batch_parser.add_argument("question", nargs="?", default="What do you see in this image?")
    batch_parser.add_argument("--workers", type=int, default=5, help="Concurrent workers")
    batch_parser.set_defaults(func=cli_batch)
    
    args = parser.parse_args()
    
    # Check API key
    if not os.getenv("OPENAI_API_KEY"):
        print("ERROR: OPENAI_API_KEY environment variable not set", file=sys.stderr)
        print("Get your key from: https://platform.openai.com/api-keys", file=sys.stderr)
        sys.exit(1)
    
    args.func(args)


# =============================================================================
# Streamlit UI (optional)
# =============================================================================

def streamlit_ui():
    """
    Interactive Streamlit interface
    
    Run with: streamlit run vision_chatbot.py
    """
    import streamlit as st
    from PIL import Image
    
    st.set_page_config(page_title="Vision AI Chatbot", page_icon="👁️")
    st.title("👁️ Multimodal Vision AI Chatbot")
    
    mode = st.radio("Mode", ["Image Analysis", "Invoice Extraction"])
    
    uploaded_file = st.file_uploader(
        "Upload an image",
        type=["png", "jpg", "jpeg", "gif", "webp"]
    )
    
    if uploaded_file:
        # Display image
        image = Image.open(uploaded_file)
        st.image(image, caption="Uploaded Image", use_container_width=True)
        
        # Save temporarily
        temp_path = f"/tmp/{uploaded_file.name}"
        with open(temp_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        
        if mode == "Image Analysis":
            question = st.text_input(
                "What do you want to know about this image?",
                "Describe this image in detail."
            )
            
            if st.button("Analyze"):
                with st.spinner("Analyzing..."):
                    result = analyze_image(temp_path, question)
                st.success("Analysis Complete!")
                st.write(result)
        
        else:  # Invoice Extraction
            if st.button("Extract Invoice Data"):
                with st.spinner("Extracting..."):
                    data = extract_invoice(temp_path)
                st.success("Extraction Complete!")
                st.json(data)
                
                # Show formatted summary
                if data.get("vendor"):
                    st.markdown(f"**Vendor:** {data['vendor']}")
                if data.get("date"):
                    st.markdown(f"**Date:** {data['date']}")
                if data.get("total") and data.get("currency"):
                    st.markdown(f"**Total:** {data['currency']} {data['total']}")


# =============================================================================
# Entry Point
# =============================================================================

if __name__ == "__main__":
    # Detect if running via Streamlit
    try:
        import streamlit as st
        # If this succeeds, we're in Streamlit runtime
        streamlit_ui()
    except (ImportError, AttributeError):
        # Not Streamlit, use CLI
        main_cli()
