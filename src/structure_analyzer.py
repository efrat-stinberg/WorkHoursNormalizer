# import logging
# from dataclasses import dataclass, asdict
# from typing import List, Dict, Any, Tuple
#
# import fitz  # PyMuPDF
#
#
# @dataclass
# class FontSpec:
#     name: str
#     size: float
#     flags: Dict[str, bool]
#
#
# @dataclass
# class ColumnSpec:
#     name: str
#     x: float
#     width: float
#     alignment: str
#
#
# @dataclass
# class Margins:
#     top: float
#     bottom: float
#     left: float
#     right: float
#
#
# def _infer_orientation(width: float, height: float) -> str:
#     return "landscape" if width > height else "portrait"
#
#
# def _guess_page_size(width: float, height: float) -> str:
#     # Points: A4 ~ 595x842, Letter ~ 612x792
#     candidates = {
#         "A4": (595, 842),
#         "Letter": (612, 792),
#         "Legal": (612, 1008),
#     }
#     def dist(a: Tuple[float, float], b: Tuple[float, float]) -> float:
#         return abs(a[0]-b[0]) + abs(a[1]-b[1])
#     w, h = (width, height) if height >= width else (height, width)
#     best = min(candidates.items(), key=lambda kv: dist((w, h), kv[1]))[0]
#     return best
#
#
# def _flags_to_styles(flags: int) -> Dict[str, bool]:
#     # PyMuPDF flags: 1=bold, 2=italic, 4=serif, 8=monospace, 16=smallcaps
#     return {
#         "bold": bool(flags & 1),
#         "italic": bool(flags & 2),
#         "serif": bool(flags & 4),
#         "monospace": bool(flags & 8),
#         "smallcaps": bool(flags & 16),
#     }
#
#
# def _cluster_x_positions(spans: List[Dict[str, Any]], tolerance: float = 8.0) -> List[float]:
#     xs = sorted({round(s["bbox"][0], 1) for s in spans})
#     if not xs:
#         return []
#     clusters = [[xs[0]]]
#     for x in xs[1:]:
#         if abs(x - clusters[-1][-1]) <= tolerance:
#             clusters[-1].append(x)
#         else:
#             clusters.append([x])
#     return [sum(c)/len(c) for c in clusters]
#
#
# def _infer_alignment(column_x: float, cell_left: float, cell_right: float, tolerance: float = 3.0) -> str:
#     if abs(column_x - cell_left) <= tolerance:
#         return "left"
#     if abs(column_x - (cell_left + cell_right) / 2.0) <= tolerance:
#         return "center"
#     return "right"
#
#
# def extract_layout_json(pdf_path: str, sample_pages: List[int] | None = None) -> Dict[str, Any]:
#     """Extract layout/formatting details for pages and return structured JSON-like dict.
#
#     Includes: page size/orientation, margins (heuristic), header columns with positions,
#     fonts, row spacing, table structure, totals/summary blocks.
#     """
#     doc = fitz.open(pdf_path)
#     pages_to_scan = sample_pages or list(range(len(doc)))
#     result_pages: List[Dict[str, Any]] = []
#     detected_report_type: str | None = None
#
#     for page_index in pages_to_scan:
#         page = doc[page_index]
#         width, height = page.rect.width, page.rect.height
#         orientation = _infer_orientation(width, height)
#         guessed_size = _guess_page_size(width, height)
#
#         # Extract text with positioning
#         page_dict = page.get_text("dict")  # blocks -> lines -> spans
#         spans: List[Dict[str, Any]] = []
#         line_tops: List[float] = []
#         fonts_collected: Dict[Tuple[str, float, int], int] = {}
#         for block in page_dict.get("blocks", []):
#             if block.get("type") != 0:  # text only
#                 continue
#             for line in block.get("lines", []):
#                 bbox = line.get("bbox")
#                 if bbox:
#                     line_tops.append(bbox[1])
#                 for span in line.get("spans", []):
#                     spans.append(span)
#                     key = (span.get("font", ""), float(span.get("size", 0)), int(span.get("flags", 0)))
#                     fonts_collected[key] = fonts_collected.get(key, 0) + 1
#
#         # Heuristic margins: nearest text from each edge
#         lefts = [s["bbox"][0] for s in spans]
#         rights = [s["bbox"][2] for s in spans]
#         tops = [s["bbox"][1] for s in spans]
#         bottoms = [s["bbox"][3] for s in spans]
#         margins = Margins(
#             top=max(0.0, min(tops) if tops else 36.0),
#             bottom=max(0.0, height - (max(bottoms) if bottoms else height - 36.0)),
#             left=max(0.0, min(lefts) if lefts else 36.0),
#             right=max(0.0, width - (max(rights) if rights else width - 36.0)),
#         )
#
#         # Column detection using header row: find the highest-density line near top
#         header_candidates = [s for s in spans if s.get("text", "").strip()]
#         header_candidates.sort(key=lambda s: s["bbox"][1])
#         header_band_y = margins.top + 0.05 * height
#         header_spans = [s for s in header_candidates if s["bbox"][1] <= header_band_y]
#         if not header_spans:
#             # fallback: take top N spans
#             header_spans = header_candidates[:12]
#
#         column_xs = _cluster_x_positions(header_spans)
#         columns: List[ColumnSpec] = []
#         header_positions: List[Dict[str, Any]] = []
#         for hs in header_spans:
#             l, t, r, b = hs["bbox"]
#             header_positions.append({
#                 "text": hs.get("text", "").strip(),
#                 "x": l,
#                 "y": t,
#                 "width": r - l,
#                 "height": b - t,
#             })
#         if column_xs:
#             # Estimate widths by gap to next column or to right margin
#             sorted_xs = sorted(column_xs)
#             for i, x in enumerate(sorted_xs):
#                 next_x = (sorted_xs[i+1] if i+1 < len(sorted_xs) else (width - margins.right))
#                 col_width = max(20.0, next_x - x - 4.0)
#                 # Column name from closest header span
#                 nearest_span = min(header_spans, key=lambda s: abs(s["bbox"][0] - x)) if header_spans else {"text": f"col_{i+1}"}
#                 name = nearest_span.get("text", f"col_{i+1}").strip()
#                 columns.append(ColumnSpec(name=name, x=x, width=col_width, alignment="left"))
#
#         # Row spacing: analyze distances between line tops
#         line_tops_sorted = sorted(line_tops)
#         gaps = [round(line_tops_sorted[i+1] - line_tops_sorted[i], 1) for i in range(len(line_tops_sorted)-1)]
#         dominant_gap = max(set(gaps), key=gaps.count) if gaps else 14.0
#         row_positions = line_tops_sorted
#
#         # Approximate table bbox from headers to last text line
#         table_left = min([c.x for c in columns], default=margins.left)
#         table_right = max([c.x + c.width for c in columns], default=width - margins.right)
#         table_top = min([h["y"] for h in header_positions], default=margins.top)
#         table_bottom = max(bottoms) if bottoms else (height - margins.bottom)
#         table_bbox = {"x": table_left, "y": table_top, "width": table_right - table_left, "height": table_bottom - table_top}
#
#         # Infer alignment per column using a few body rows under headers
#         body_spans = [s for s in spans if s not in header_spans]
#         for col in columns:
#             # find spans within column band
#             col_spans = [s for s in body_spans if abs(s["bbox"][0] - col.x) <= max(6.0, 0.5*col.width)]
#             if not col_spans:
#                 continue
#             # use a representative cell
#             sample = min(col_spans, key=lambda s: s["bbox"][1])
#             l, t, r, b = sample["bbox"]
#             col.alignment = _infer_alignment(col.x, l, r)
#
#         # Fonts summary
#         fonts_summary = []
#         for (fname, fsize, fflags), count in sorted(fonts_collected.items(), key=lambda kv: (-kv[1], -kv[0][1])):
#             fonts_summary.append({
#                 "font": fname,
#                 "size": fsize,
#                 "styles": _flags_to_styles(fflags),
#                 "count": count,
#             })
#
#         # Totals/summary detection: find spans containing common keywords
#         total_keywords = ["Total", "סה\"כ", "סך הכל", "סיכום", "Total Hours", "Grand Total"]
#         totals = []
#         for s in spans:
#             txt = s.get("text", "").strip()
#             if not txt:
#                 continue
#             if any(k in txt for k in total_keywords):
#                 l, t, r, b = s["bbox"]
#                 totals.append({"text": txt, "x": l, "y": t})
#
#         # Simple structure-based report classification based on header names
#         if columns and detected_report_type is None:
#             header_names = {c.name for c in columns}
#             hebrew_keys = {"תאריך", "יום", "כניסה", "יציאה", "סה\"כ"}
#             en_keys = {"Employee", "Date", "Start Time", "End Time", "Total Hours"}
#             if len(hebrew_keys & header_names) >= 3:
#                 detected_report_type = "attendance_timesheet_hebrew"
#             elif len(en_keys & header_names) >= 3:
#                 detected_report_type = "attendance_timesheet_en"
#             else:
#                 detected_report_type = "generic_table_report"
#
#         page_info: Dict[str, Any] = {
#             "page_number": page_index + 1,
#             "page_size": guessed_size,
#             "orientation": orientation,
#             "dimensions_pt": {"width": width, "height": height},
#             "margins": asdict(margins),
#             "padding": {"row": 2.0, "cell": 2.0},
#             "columns": [asdict(c) for c in columns],
#             "num_columns": len(columns),
#             "headers": header_positions,
#             "fonts": fonts_summary,
#             "row_spacing": dominant_gap,
#             "row_positions": row_positions,
#             "table_bbox": table_bbox,
#             "totals": totals,
#         }
#
#         result_pages.append(page_info)
#
#     return {"pages": result_pages, "report_type": detected_report_type or "unknown"}
#
#
# def analyze_structure(pdf_path, sample_pages=[0], ocr_lang="heb+eng"):
#     """Enhanced structure analysis that preserves exact layout and formatting."""
#     layout = extract_layout_json(pdf_path, sample_pages=sample_pages)
#     first_page = layout.get("pages", [{}])[0]
#
#     # Extract comprehensive structure information
#     structure = {
#         "columns": [],
#         "page_info": first_page,
#         "fonts": first_page.get("fonts", []),
#         "margins": first_page.get("margins", {}),
#         "row_spacing": first_page.get("row_spacing", 14.0),
#         "table_bbox": first_page.get("table_bbox", {}),
#         "report_type": layout.get("report_type", "unknown")
#     }
#
#     # Process columns with enhanced information
#     cols = first_page.get("columns", [])
#     for c in cols:
#         structure["columns"].append({
#             "name": c["name"],
#             "x_start": c["x"],
#             "width": c["width"],
#             "align": c.get("alignment", "left"),
#             "font_size": _get_column_font_size(c, first_page),
#             "font_style": _get_column_font_style(c, first_page)
#         })
#
#     # Fallback structure if no columns detected
#     if not structure["columns"]:
#         logging.info(f"Structure analysis fallback for {pdf_path} — no columns found, using default layout.")
#         structure["columns"] = [
#             {"name": "תאריך", "x_start": 50, "width": 80, "align": "left", "font_size": 10, "font_style": "normal"},
#             {"name": "יום", "x_start": 140, "width": 60, "align": "center", "font_size": 10, "font_style": "normal"},
#             {"name": "כניסה", "x_start": 210, "width": 60, "align": "center", "font_size": 10, "font_style": "normal"},
#             {"name": "יציאה", "x_start": 280, "width": 60, "align": "center", "font_size": 10, "font_style": "normal"},
#             {"name": "סה\"כ", "x_start": 350, "width": 60, "align": "right", "font_size": 10, "font_style": "normal"},
#         ]
#
#     logging.info("Enhanced structure analysis completed for %s — detected %d columns", pdf_path, len(structure["columns"]))
#     return structure
#
# def _get_column_font_size(column, page_info):
#     """Extract font size for a column based on page analysis."""
#     fonts = page_info.get("fonts", [])
#     if fonts:
#         # Return the most common font size
#         return fonts[0].get("size", 10)
#     return 10
#
# def _get_column_font_style(column, page_info):
#     """Extract font style for a column based on page analysis."""
#     fonts = page_info.get("fonts", [])
#     if fonts:
#         styles = fonts[0].get("styles", {})
#         if styles.get("bold"):
#             return "bold"
#         elif styles.get("italic"):
#             return "italic"
#     return "normal"
