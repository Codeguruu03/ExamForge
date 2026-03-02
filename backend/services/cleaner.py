"""
Text Cleaning Pipeline.
Strips noise from raw extracted text before normalization:
  - Page numbers
  - Headers / footers
  - Repeated whitespace
  - Watermarks / boilerplate lines
"""
import re


# Lines that are very likely noise (page numbers, section headers, etc.)
_NOISE_PATTERNS = [
    r"^\s*page\s+\d+\s*$",                  # "Page 1", "page 12"
    r"^\s*\d+\s*$",                          # standalone numbers (page numbers)
    r"^\s*-+\s*$",                           # divider lines
    r"^\s*={3,}\s*$",                        # === dividers
    r"^\s*(section|part|unit)\s+[ivxlcdm\d]+\s*$",  # "Section I", "Part 2"
    r"^\s*(answer\s+key|answer\s+sheet)\s*$",        # "Answer Key"
    r"^\s*\(?\s*continued\s*\)?\s*$",               # "(continued)"
    r"^\s*www\.\S+\s*$",                     # website URLs
    r"^\s*©.*$",                             # copyright lines
    r"^\s*P-\d+\s*$",                        # "P-10" page numbers
    r"^\s*DPP.*$",                           # DPP headers "DPP / CP03"
    r"^\s*Chapter-wise Sheets\s*$",
    r"^\s*PHYSICS\s*$",
    r"^\s*Start Time\s*:.*$",
    r"^\s*End Time\s*:.*$",
]

_NOISE_RE = [re.compile(p, re.IGNORECASE) for p in _NOISE_PATTERNS]


def clean_text(raw: str) -> str:
    """
    Main entry point. Accepts raw extracted text and returns cleaned text.
    """
    lines = raw.splitlines()
    cleaned_lines = []

    for line in lines:
        if _is_noise(line):
            continue
        # Normalise whitespace within the line
        line = re.sub(r"[ \t]+", " ", line).strip()
        if line:
            cleaned_lines.append(line)

    # Combine lines to apply block-level cleaning
    text = "\n".join(cleaned_lines)
    
    # Custom rule for DPP Response Grids which interrupt questions
    text = re.sub(r"RESPONSE[\s\n]*GRID[\s\d\.\n]*Space for Rough Work(?:.*?(?:\n|$))?", "", text, flags=re.IGNORECASE | re.DOTALL)
    # Remove rough work brackets that might have bypassed line rules due to wrapped lines
    text = re.sub(r"\[.*?\]", "", text, flags=re.DOTALL)
    
    # Collapse more than two consecutive blank lines into one
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def _is_noise(line: str) -> bool:
    for pattern in _NOISE_RE:
        if pattern.match(line.strip()):
            return True
    return False
