# PDF to JSON Converter

A professional-grade Python script that converts PDF documents into structured JSON format using the Unstructured library. This tool extracts text, tables, images (treated as charts), and organizes them by pages with section detection.

## Features

- **Advanced PDF Processing**: Leverages Unstructured library for robust extraction of unstructured documents
- **Structured Output**: Converts PDFs into well-organized JSON with pages, content types, and metadata
- **Section Detection**: Automatically detects and tags sections and subsections using regex heuristics
- **Table Extraction**: Parses markdown tables into 2D arrays
- **Image Handling**: Identifies and describes charts/images with page coordinates
- **Progress Tracking**: Uses tqdm for visual progress during processing
- **Error Handling**: Includes fallback strategies for processing failures
- **Configurable Strategies**: Supports different partitioning strategies (hi_res, fast, ocr_only)

## Schema

The output JSON follows this structure:

```json
{
  "pages": [
    {
      "page_number": 1,
      "content": [
        {
          "type": "paragraph|table|chart",
          "section": "1.1",
          "sub_section": "Introduction",
          "description": "Section header",
          "text": "Extracted text content",
          "table_data": [["row1", "col1"], ["row2", "col2"]]
        }
      ]
    }
  ]
}
```

## Installation

1. **Clone or download the repository**

2. **Set up Python environment** (recommended Python 3.8+)

3. **Install dependencies**:
   ```bash
   pip install "unstructured[all-docs]"
   pip install PyMuPDF tqdm pandas
   ```

   For optimal performance with 'hi_res' strategy, additional dependencies may be required (detectron2, etc.).

4. **Install Poppler** (for PDF image extraction):
   - Download from: https://blog.alivate.com.au/poppler-windows/
   - Extract to a folder (e.g., `poppler-24.02.0/`)
   - Ensure the `bin` folder is in your PATH or specify the path in code

## Usage

### Basic Usage

```bash
python conversion.py "path/to/your/document.pdf" -o "output.json"
```

### Advanced Usage

```bash
python conversion.py "path/to/your/document.pdf" -o "output.json" -s "fast"
```

### Command Line Arguments

- `pdf_path`: Path to the input PDF file (required)
- `-o, --output`: Path to the output JSON file (default: `output.json`)
- `-s, --strategy`: Partitioning strategy (`hi_res`, `fast`, `ocr_only`) (default: `hi_res`)

## Processing Pipeline

1. **Input Validation**: Checks if PDF file exists and is accessible
2. **Page Count**: Uses PyMuPDF to get total pages for progress tracking
3. **PDF Partitioning**: Applies Unstructured's partition_pdf with specified strategy
   - Extracts elements: text, tables, images, titles
   - Handles multi-language content (default: English)
   - Infers table structures for better extraction
4. **Element Processing**:
   - Groups elements by page number
   - Detects sections and subsections using regex patterns
   - Maps element categories to content types (paragraph/table/chart)
   - Parses markdown tables into structured data
   - Extracts metadata (coordinates, descriptions)
5. **Fallback Handling**: If primary strategy fails, automatically retries with fallback strategy
6. **JSON Generation**: Structures all extracted data into the defined schema
7. **Output**: Writes formatted JSON to specified file

## Dependencies

- **unstructured[all-docs]**: Core library for document processing
- **PyMuPDF (fitz)**: For PDF page counting and metadata
- **tqdm**: Progress bar for processing feedback
- **pandas**: Table parsing and data manipulation
- **poppler**: PDF rendering for image extraction (external binary)

## Configuration

The script includes configurable parameters:

- `DEFAULT_STRATEGY`: Default partitioning strategy (`hi_res`)
- `FALLBACK_STRATEGY`: Backup strategy if primary fails (`fast`)
- Logging level and format can be adjusted in the code

## Error Handling

- File not found errors
- Processing strategy failures with automatic fallback
- Table parsing warnings
- Comprehensive logging for debugging

## Examples

### Processing a Financial Report

```bash
python conversion.py "Fund Factsheet.pdf" -o "factsheet.json" -s "hi_res"
```

### Batch Processing (using shell script)

```bash
for pdf in *.pdf; do
    python conversion.py "$pdf" -o "${pdf%.pdf}.json"
done
```

## Troubleshooting

- **Strategy fails**: The script automatically falls back to 'fast' strategy
- **Missing dependencies**: Ensure all pip packages are installed
- **Poppler not found**: Add poppler bin to PATH or install system-wide
- **Large PDFs**: Use 'fast' strategy for quicker processing
- **OCR needed**: Use 'ocr_only' strategy for image-heavy PDFs

## Publishing to GitHub

Follow these steps to publish your PDF to JSON converter project to GitHub:

### 1. Initialize Git Repository

```bash
git init
```

### 2. Add Files to Git

```bash
git add .
```

### 3. Create Initial Commit

```bash
git commit -m "Initial commit: PDF to JSON converter"
```

### 4. Create GitHub Repository

1. Go to [GitHub.com](https://github.com) and sign in
2. Click the "+" icon in the top right corner
3. Select "New repository"
4. Name your repository (e.g., `pdf-to-json-converter`)
5. Add a description: "Convert PDF documents to structured JSON using Unstructured library"
6. Choose public or private
7. **Do not** initialize with README, .gitignore, or license (we already have these)
8. Click "Create repository"

### 5. Connect Local Repository to GitHub

Copy the repository URL from GitHub (it will look like `https://github.com/yourusername/pdf-to-json-converter.git`)

```bash
git remote add origin https://github.com/yourusername/pdf-to-json-converter.git
```

### 6. Push to GitHub

```bash
git push -u origin main
```

### 7. Verify

Visit your GitHub repository URL to confirm all files have been uploaded successfully.

### Additional Git Commands

- **Check status**: `git status`
- **View commit history**: `git log`
- **Create a new branch**: `git checkout -b feature-branch-name`
- **Switch branches**: `git checkout branch-name`
- **Merge branches**: `git merge branch-name`

### Notes

- The `.gitignore` file is already configured to exclude temporary files, virtual environments, and output files
- Make sure to commit changes regularly with descriptive commit messages
- Consider adding a `requirements.txt` file for easy dependency installation:

```bash
pip freeze > requirements.txt
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is open-source. Please check the license file for details.

## Support

For issues or questions, please create an issue in the repository.