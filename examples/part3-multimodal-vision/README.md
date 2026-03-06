# Part 3: Multimodal Vision AI

Complete implementation of image understanding with GPT-4o vision capabilities.

## Features

✅ **Single Image Analysis** — Ask questions about any image  
✅ **Invoice/Receipt OCR** — Extract structured data from receipts  
✅ **Batch Processing** — Analyze folders of images concurrently  
✅ **Interactive UI** — Streamlit web interface  
✅ **Cost-Optimized** — Uses `gpt-4o-mini` (~$0.001 per image)

## Installation

```bash
cd examples/part3-multimodal-vision
pip install -r requirements.txt

# Set your OpenAI API key
export OPENAI_API_KEY="sk-xxx"
```

Get your API key from: https://platform.openai.com/api-keys

## Usage

### 1. Command-Line Interface

**Analyze a single image:**
```bash
python vision_chatbot.py analyze photo.jpg "What's in this image?"
```

**Extract invoice data:**
```bash
python vision_chatbot.py invoice receipt.png
```

**Batch process a folder:**
```bash
python vision_chatbot.py batch ./photos "Describe what you see"
```

### 2. Interactive Web UI

```bash
streamlit run vision_chatbot.py
```

Opens browser at http://localhost:8501 with:
- Drag-and-drop image upload
- Real-time image analysis
- Invoice extraction with JSON output

### 3. Python API

```python
from vision_chatbot import analyze_image, extract_invoice, batch_analyze

# Single image
result = analyze_image("photo.jpg", "How many people are in this photo?")
print(result)

# Invoice extraction
invoice_data = extract_invoice("receipt.png")
print(f"Total: {invoice_data['currency']} {invoice_data['total']}")

# Batch processing
results = batch_analyze("./photos", "What objects are visible?")
for r in results:
    print(f"{r['file']}: {r['result']}")
```

## Architecture

```
vision_chatbot.py
├── encode_image()         # Base64 encoding + MIME type detection
├── analyze_image()        # General image Q&A
├── extract_invoice()      # Structured invoice extraction
├── batch_analyze()        # Concurrent batch processing
├── CLI interface          # argparse commands
└── Streamlit UI           # Interactive web interface
```

## Cost Analysis

Using `gpt-4o-mini` (recommended):

| Operation | Input Tokens | Cost per Image |
|-----------|--------------|----------------|
| Simple analysis | ~1,000 | $0.0001 |
| Invoice extraction | ~1,500 | $0.00015 |
| Detailed description | ~2,000 | $0.0002 |

**Example:** 1,000 invoice extractions = ~$0.15 total cost.

Compare to dedicated OCR services:
- AWS Textract: $1.50 per 1,000 pages
- Google Cloud Vision: $1.50 per 1,000 images
- GPT-4o-mini: $0.15 per 1,000 images ✅

## Example Output

### Image Analysis
```bash
$ python vision_chatbot.py analyze sunset.jpg "Describe the mood"

This image captures a serene sunset over a calm ocean. 
The sky transitions from deep orange to purple, creating 
a peaceful and contemplative atmosphere. A silhouette of 
a person stands on the beach, suggesting solitude and 
reflection.
```

### Invoice Extraction
```bash
$ python vision_chatbot.py invoice grocery_receipt.png

{
  "vendor": "Whole Foods Market",
  "date": "2024-03-15",
  "items": [
    {"name": "Organic Bananas", "quantity": 2, "price": 3.99},
    {"name": "Almond Milk", "quantity": 1, "price": 4.49}
  ],
  "subtotal": 8.48,
  "tax": 0.68,
  "total": 9.16,
  "currency": "USD",
  "payment_method": "Credit Card"
}
```

## Supported Image Formats

- PNG
- JPEG/JPG
- GIF
- WebP

Maximum file size: 20MB (OpenAI limit)

## Error Handling

The script includes:
- Automatic retry for transient API errors
- Graceful degradation for unsupported formats
- Clear error messages for missing API keys

## Performance Tips

1. **Batch processing:** Use `--workers` flag to control concurrency
   ```bash
   python vision_chatbot.py batch ./photos "What's this?" --workers 10
   ```

2. **Cost optimization:** Use `gpt-4o-mini` instead of `gpt-4o` (10x cheaper, minimal quality loss)

3. **Rate limits:** OpenAI free tier = 3 RPM; paid tier = 500+ RPM

## Troubleshooting

**API key error:**
```bash
export OPENAI_API_KEY="sk-xxx"
```

**Image format error:**
Convert to PNG/JPG:
```bash
convert input.tiff output.png
```

**Rate limit exceeded:**
Reduce `--workers` or upgrade OpenAI plan.

## Next Steps

- Add support for Claude 3.5 Sonnet (better for complex visuals)
- Implement caching for repeated images
- Add PDF page extraction → image analysis pipeline
- Build invoice → accounting software integration

## Related Tutorials

- [Part 1: Basic Chatbot](../part1-basic-chatbot/)
- [Part 2: RAG Document Q&A](../part2-rag-chatbot/)
- [Part 4: AI Agents](../part4-ai-agents/) (coming soon)

## License

MIT — Use freely in your projects!

---

**Questions?** Open an issue on GitHub or reach out on X [@bitale14](https://x.com/bitale14)
