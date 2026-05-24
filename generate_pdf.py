"""Generate a PDF user guide from the screenshot manifest."""

import json
import os
from datetime import datetime
from fpdf import FPDF


class UserGuidePDF(FPDF):
    """Custom PDF class for the user guide."""

    def __init__(self):
        super().__init__()
        self.set_auto_page_break(auto=True, margin=20)
        self.toc_entries = []

    def header(self):
        """Add header to each page (except cover and TOC)."""
        if self.page_no() > 2:
            self.set_font("Helvetica", "I", 9)
            self.set_text_color(128, 128, 128)
            self.cell(0, 10, "Todo App - User Guide", align="L")
            self.cell(0, 10, f"Page {self.page_no()}", align="R")
            self.ln(15)
            self.set_text_color(0, 0, 0)

    def footer(self):
        """Add footer with page number."""
        pass

    def add_cover_page(self, app_name, subtitle, date_str):
        """Add a cover page."""
        self.add_page()
        self.ln(60)

        # App name
        self.set_font("Helvetica", "B", 36)
        self.set_text_color(37, 99, 235)  # Primary blue
        self.cell(0, 20, app_name, ln=True, align="C")

        # Subtitle
        self.ln(5)
        self.set_font("Helvetica", "", 24)
        self.set_text_color(55, 65, 81)
        self.cell(0, 15, subtitle, ln=True, align="C")

        # Date
        self.ln(10)
        self.set_font("Helvetica", "", 14)
        self.set_text_color(107, 114, 128)
        self.cell(0, 10, f"Generated: {date_str}", ln=True, align="C")

        # Decorative line
        self.ln(20)
        self.set_draw_color(37, 99, 235)
        self.set_line_width(0.5)
        self.line(60, self.get_y(), 150, self.get_y())

        # Description
        self.ln(15)
        self.set_font("Helvetica", "", 12)
        self.set_text_color(75, 85, 99)
        self.multi_cell(
            0,
            7,
            "This document provides a comprehensive guide to using the Todo App. "
            "It covers all pages, features, and interactive elements with screenshots "
            "and step-by-step instructions.",
            align="C",
        )

        self.set_text_color(0, 0, 0)

    def add_toc(self):
        """Add table of contents page."""
        self.add_page()
        self.set_font("Helvetica", "B", 22)
        self.set_text_color(31, 41, 55)
        self.cell(0, 15, "Table of Contents", ln=True)
        self.ln(10)

        self.set_font("Helvetica", "", 12)
        self.set_text_color(55, 65, 81)

        for i, entry in enumerate(self.toc_entries, 1):
            label = entry["label"]
            page_num = entry["page"]
            # Draw dotted line between label and page number
            self.set_font("Helvetica", "", 12)
            label_text = f"{i}. {label}"
            self.cell(0, 8, label_text, ln=False)
            self.set_x(-30)
            self.cell(20, 8, str(page_num), ln=True, align="R")

        self.set_text_color(0, 0, 0)

    def add_section(self, label, route, screenshots, usage_steps):
        """Add a section for a route."""
        self.add_page()
        page_num = self.page_no()
        self.toc_entries.append({"label": label, "page": page_num})

        # Section heading
        self.set_font("Helvetica", "B", 20)
        self.set_text_color(31, 41, 55)
        self.cell(0, 12, label, ln=True)

        # Route path
        self.set_font("Helvetica", "I", 11)
        self.set_text_color(107, 114, 128)
        self.cell(0, 8, f"Route: {route}", ln=True)
        self.ln(5)

        # Screenshots
        for screenshot_path in screenshots:
            if os.path.exists(screenshot_path):
                file_size = os.path.getsize(screenshot_path)
                if file_size > 0:
                    # Check if we need a new page for the image
                    if self.get_y() > 180:
                        self.add_page()

                    try:
                        self.image(screenshot_path, x=10, w=190)
                        self.ln(3)

                        # Caption
                        filename = os.path.basename(screenshot_path)
                        caption = filename.replace("page-", "").replace(".png", "").replace("-", " ").title()
                        self.set_font("Helvetica", "I", 9)
                        self.set_text_color(107, 114, 128)
                        self.cell(0, 6, f"Figure: {caption}", ln=True, align="C")
                        self.ln(5)
                    except Exception as e:
                        print(f"WARNING: Could not embed image {screenshot_path}: {e}")
                        self.set_font("Helvetica", "I", 10)
                        self.cell(0, 8, f"[Image could not be embedded: {os.path.basename(screenshot_path)}]", ln=True)
                else:
                    print(f"WARNING: Screenshot is empty: {screenshot_path}")
            else:
                print(f"WARNING: Screenshot missing: {screenshot_path}")
                self.set_font("Helvetica", "I", 10)
                self.set_text_color(220, 38, 38)
                self.cell(0, 8, f"[Screenshot missing: {os.path.basename(screenshot_path)}]", ln=True)
                self.set_text_color(0, 0, 0)

        # Usage steps
        if self.get_y() > 220:
            self.add_page()

        self.ln(5)
        self.set_font("Helvetica", "B", 14)
        self.set_text_color(31, 41, 55)
        self.cell(0, 10, "How to Use", ln=True)
        self.ln(2)

        self.set_font("Helvetica", "", 11)
        self.set_text_color(55, 65, 81)

        for i, step in enumerate(usage_steps, 1):
            if self.get_y() > 270:
                self.add_page()
            self.multi_cell(0, 6, f"{i}. {step}")
            self.ln(2)

        self.set_text_color(0, 0, 0)


def main():
    """Generate the PDF user guide."""
    # Resolve paths relative to this script's directory for portability
    base_dir = os.path.dirname(os.path.abspath(__file__))
    manifest_path = os.path.join(base_dir, "manifest.json")

    with open(manifest_path, "r") as f:
        manifest = json.load(f)

    # Convert any relative screenshot paths in the manifest to absolute paths
    for entry in manifest:
        entry["screenshots"] = [
            p if os.path.isabs(p) else os.path.join(base_dir, p)
            for p in entry["screenshots"]
        ]

    print(f"Loaded manifest with {len(manifest)} sections")

    # Verify all screenshots exist
    total_screenshots = 0
    missing_screenshots = 0
    for entry in manifest:
        for screenshot in entry["screenshots"]:
            total_screenshots += 1
            if not os.path.exists(screenshot):
                print(f"WARNING: Missing screenshot: {screenshot}")
                missing_screenshots += 1

    print(f"Total screenshots: {total_screenshots}, Missing: {missing_screenshots}")

    # Create PDF
    pdf = UserGuidePDF()

    # Cover page
    date_str = datetime.now().strftime("%B %d, %Y")
    pdf.add_cover_page("Todo App", "User Guide", date_str)

    # Add sections (we'll fill TOC after)
    for entry in manifest:
        pdf.add_section(
            label=entry["label"],
            route=entry["route"],
            screenshots=entry["screenshots"],
            usage_steps=entry["usage_steps"],
        )

    # Now rebuild with TOC
    # Since fpdf2 doesn't support inserting pages, we rebuild
    pdf2 = UserGuidePDF()
    pdf2.toc_entries = pdf.toc_entries

    # Cover page
    pdf2.add_cover_page("Todo App", "User Guide", date_str)

    # TOC
    pdf2.add_toc()

    # Sections
    for entry in manifest:
        pdf2.add_section(
            label=entry["label"],
            route=entry["route"],
            screenshots=entry["screenshots"],
            usage_steps=entry["usage_steps"],
        )

    # Save PDF
    output_path = os.path.join(base_dir, "user-guide.pdf")
    pdf2.output(output_path)

    # Verify
    if os.path.exists(output_path) and os.path.getsize(output_path) > 0:
        size_kb = os.path.getsize(output_path) / 1024
        print(f"\n✅ SUCCESS: PDF generated at: {output_path}")
        print(f"   File size: {size_kb:.1f} KB")
        print(f"   Sections: {len(manifest)}")
        print(f"   Screenshots embedded: {total_screenshots - missing_screenshots}")
    else:
        print("\n❌ ERROR: PDF is missing or empty!")
        exit(1)


if __name__ == "__main__":
    main()
