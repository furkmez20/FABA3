def convert_text_to_json(input_path, output_path="output.json"):
    import json
    import os
    from docx import Document

    def parse_script_lines(lines):
        """Turn raw lines into a list of {id, speaker, text} dicts."""
        parsed = []
        for i, line in enumerate(lines, start=1):
            if ":" in line:
                speaker, text = line.split(":", 1)
                parsed.append({"id": i, "speaker": speaker.strip(), "text": text.strip()})
            else:
                parsed.append({"id": i, "speaker": "Narrator", "text": line.strip()})
        return parsed

    def read_txt(file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            lines = [line.strip() for line in f if line.strip()]
        return lines

    def read_docx(file_path):
        doc = Document(file_path)
        paragraphs = [p.text.strip() for p in doc.paragraphs if p.text.strip()]
        return paragraphs

    ext = os.path.splitext(input_path)[1].lower()
    if ext == ".txt":
        lines = read_txt(input_path)
    elif ext == ".docx":
        lines = read_docx(input_path)
    else:
        raise ValueError("Unsupported file type: use .txt or .docx")

    json_data = parse_script_lines(lines)

    output_dir = os.path.dirname(output_path) or os.getcwd()
    os.makedirs(output_dir, exist_ok=True)

    final_json_path = os.path.join(output_dir, os.path.basename(output_path))
    with open(final_json_path, "w", encoding="utf-8") as f:
        json.dump(json_data, f, ensure_ascii=False, indent=2)

    return final_json_path, lines
