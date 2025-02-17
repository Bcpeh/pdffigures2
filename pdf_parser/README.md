# PDF Parser

This project contains a PDF parsing tool that extracts text and metadata from PDF files.

## Prerequisites

- Python 3.10+
- Install dependencies through pip
- Java Runtime Environment (JRE) openjdk@11 or openjdk@17
- If local debug mode, add below into `.vscode/settings.json` (create such file if don't have):
```json
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Python: Current File",
            "type": "debugpy",
            "request": "launch",
            "program": "${file}",
            "console": "integratedTerminal",
            "cwd": "${workspaceFolder}",
            "env": {
                "PYTHONPATH": "${workspaceFolder}"
            },
            "justMyCode": true
        }
    ]
}
```
## Usage

To process a PDF file, use the `process_pdf_task` function in the `process_pdf.py` file. Here's how to use it:

1. Place your PDF file in the `pdfs` directory.
2. Set PYTHONPATH to the root directory of the project:
   ``` bash
   export PYTHONPATH=$(pwd)
   # OR
   export PYTHONPATH=/`pwd`
   ```
3. Note that if you would like to have section with respective results, you need to set the `run_section_extraction` to `True`, this might take a while and also requires OPENAI_API_KEY to be set.
   Update the section mapping file in `pdf_parser/section_mapping.json` if you would like to change the section names.
   ```
   OPENAI_API_KEY=example_openai_api_key
   ```
   Then, you can call the function as follows:
   ```python
   from pdf_parser.process_pdf import process_pdf_task
   client = OpenAI()
   results = process_pdf_task(client, 'path/to/your/pdf.pdf', run_section_extraction=True, output_path="output")
   ```


## How it works

1. The `process_pdf_task` function copies the input PDF to a temporary directory for processing.

2. It then runs the Java-based PDF parser using the `pdf-parser.jar` file.

3. The parser extracts metadata and text information from the PDF and saves it as a JSON file.

4. The `process_json` function in `text_extraction.py` processes this JSON data to create a full text representation of the PDF content.

5. The results, including metadata and full text, are saved in the `results/pdf_parser` directory as a JSON file.

## Customization

You can customize the text extraction process by modifying the `create_full_text` function in `text_extraction.py`. This function determines how the extracted text is formatted and structured.

## Troubleshooting

If you encounter any issues:

1. Ensure that Java `openjdk@17` is installed and accessible from the command line.
2. Install the required packages with `pip install -r requirements.txt`.
3. Check that the `pdf-parser.jar` file is present in the `pdf_parser` directory.
4. Verify that the input PDF file exists in the specified location.

For any errors during processing, check the logs printed to the console for more information.
