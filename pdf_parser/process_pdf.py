import os
import subprocess
import json
import shutil
import tempfile
from loguru import logger
from openai import OpenAI
import uuid
from dotenv import load_dotenv


from pdf_parser.text_extraction import (
    process_json,
    extract_sections,
    extract_title_from_metadata,
    mapping_sections_with_llm,
)

load_dotenv(override=True)


# clear the content of the log file first
if os.path.exists("PdfParser.log"):
    with open("PdfParser.log", "w") as f:
        f.truncate()


def process_pdf_task(
    client: OpenAI,
    file_path,
    run_section_extraction: bool = True,
    output_path: str = None,
):
    try:
        # Use a secure temporary directory
        with tempfile.TemporaryDirectory() as temp_dir:
            # Copy the file to the temp_dir
            input_filename = os.path.basename(file_path)
            input_path = os.path.join(temp_dir, input_filename)
            shutil.copyfile(file_path, input_path)

            # Define prefixes for output files
            output_metadata_prefix = os.path.join(temp_dir, "data-")
            os.makedirs(output_metadata_prefix, exist_ok=True)

            cmd = [
                "java",
                "-jar",
                "pdf_parser/pdf-parser.jar",
                input_path,
                "-g",
                output_metadata_prefix,
            ]
            # Run pdf-parser
            process = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

            if process.returncode != 0:
                raise Exception(f"pdf-parser processing failed: {process.stderr}")

            # Extract base filename without extension
            base_filename = os.path.splitext(input_filename)[0]

            # Construct the path to the output JSON file
            output_json_path = f"{output_metadata_prefix}{base_filename}.json"

            # Read and parse the metadata JSON file
            with open(output_json_path, "r") as f:
                metadata = json.load(f)
            title = extract_title_from_metadata(input_path)
            full_text = process_json(metadata)
            structured_data = {"title": title}
            section_positions = {"title": 0}
            sections_mapping = {}
            if run_section_extraction:
                structured_data, section_positions = extract_sections(client, full_text)
                sections_mapping = mapping_sections_with_llm(client, structured_data)
                section_positions["title"] = 0
                structured_data["title"] = title
            full_text = title + "\n\n" + full_text
            results = {
                "metadata": metadata,
                "structured_data": structured_data,
                "full_text": full_text,
                "sections_mapping": sections_mapping,
                "section_positions": section_positions,
            }

            # Save results to a local directory
            if output_path:
                filename = input_filename.replace(".pdf", ".json")
                result_path = os.path.join(output_path, filename)
                os.makedirs(output_path, exist_ok=True)
                with open(result_path, "w") as f:
                    json.dump(results, f, indent=4)

            return results

    except Exception as e:
        error_msg = str(e)
        logger.error(f"Error during processing: {error_msg}")
        return {"error": error_msg}


if __name__ == "__main__":
    pdf_path = "example_paper.pdf"
    # Only running PDF parser
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    results = process_pdf_task(client, pdf_path, run_section_extraction=True, output_path="output")
    print(results)
