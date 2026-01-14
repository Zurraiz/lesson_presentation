import os
import requests
from io import BytesIO
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.enum.shapes import PP_PLACEHOLDER
from django.conf import settings

class TemplateManager:
    """
    Manages PowerPoint template operations: inspection and generation.
    """
    
    def __init__(self, template_path):
        if not os.path.exists(template_path):
            raise FileNotFoundError(f"Template not found: {template_path}")
        self.template_path = template_path
        self.prs = Presentation(template_path)

    def analyze_template(self):
        """
        Returns a JSON-serializable structure defining available layouts and their placeholders.
        """
        layouts_info = []
        
        for idx, layout in enumerate(self.prs.slide_layouts):
            placeholders = []
            for ph in layout.placeholders:
                ph_type = ph.placeholder_format.type
                ph_name = ph.name
                ph_idx = ph.placeholder_format.idx
                
                placeholders.append({
                    "index": ph_idx,
                    "name": ph_name,
                    "type": str(ph_type), # enum value, helpful for debugging
                    "is_title": "title" in ph_name.lower() or ph_type == PP_PLACEHOLDER.TITLE,
                    "is_image": "picture" in ph_name.lower() or ph_type == PP_PLACEHOLDER.PICTURE
                })
            
            layouts_info.append({
                "id": idx,
                "name": layout.name,
                "placeholders": placeholders
            })
            
        return {"layouts": layouts_info}

    def create_presentation(self, slides_data, output_filename=None):
        """
        Creates a new presentation based on the template and provided data.
        
        slides_data: List of dictionaries. Each dict should have:
            - layout_id: int (index of the layout to use)
            - content: dict mapping placeholder_index (str/int) to value
            
        Returns: Path to the saved file.
        """
        # Create a fresh presentation instance from the template
        new_prs = Presentation(self.template_path)
        
        # Remove any existing slides (templates sometimes have dummy slides)
        # Note: python-pptx doesn't support deleting common slides easily without low-level XML, 
        # but usually we just append. If the template file comes with slides, they remain.
        # Ideally, the template file should be empty of slides, just masters/layouts.
        
        for slide_data in slides_data:
            layout_id = slide_data.get("layout_id")
            content = slide_data.get("content", {})
            
            if layout_id is None:
                continue
                
            try:
                slide_layout = new_prs.slide_layouts[layout_id]
            except IndexError:
                # Fallback or skip
                continue
                
            slide = new_prs.slides.add_slide(slide_layout)
            self._fill_slide(slide, content)
            
        if not output_filename:
            output_filename = "generated_lesson.pptx"
            
        output_path = os.path.join(settings.MEDIA_ROOT, output_filename)
        new_prs.save(output_path)
        
        return output_path

    def _fill_slide(self, slide, content_map):
        """
        Fills a single slide's placeholders with content.
        content_map: Key is placeholder_idx, Value is text string or dict for images.
        """
        for ph_idx, value in content_map.items():
            # Convert key to int if it came from JSON as string
            try:
                ph_idx = int(ph_idx)
            except ValueError:
                continue
                
            # Find the placeholder on the slide
            try:
                shape = slide.placeholders[ph_idx]
            except KeyError:
                # Placeholder not found on this slide layout
                continue
                
            if isinstance(value, str):
                # Simple text fill
                if not shape.has_text_frame:
                    continue
                shape.text = value
                
                # Manual Dynamic Font Scaling
                # Heuristic: The more text, the smaller the font.
                try:
                     text_len = len(value)
                     # Get the first paragraph/run to set font
                     if shape.text_frame.paragraphs:
                         p = shape.text_frame.paragraphs[0]
                         if not p.runs:
                             p.add_run()
                         
                         # Base sizing logic (adjust thresholds as needed)
                         if text_len > 300:
                             font_size = Pt(12)
                         elif text_len > 200:
                             font_size = Pt(14)
                         elif text_len > 100:
                             font_size = Pt(18)
                         else:
                             # Keep template default or set a standard size
                             font_size = Pt(24)
                             
                         # Apply to ALL runs in ALL paragraphs
                         for paragraph in shape.text_frame.paragraphs:
                             for run in paragraph.runs:
                                 run.font.size = font_size
                                 
                     shape.text_frame.word_wrap = True
                except Exception as e:
                    print(f"Error sizing text: {e}")
                
            elif isinstance(value, dict) and value.get("type") == "image":
                # Image fill
                image_url = value.get("url")
                if image_url:
                    self._insert_image(shape, image_url)

    def _insert_image(self, shape, image_url):
        """
        Inserts an image into a picture placeholder, preserving aspect ratio if possible.
        """
        # Download image to memory
        try:
            # Add User-Agent to avoid 403 Forbidden from sites like Wikimedia
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            response = requests.get(image_url, headers=headers, timeout=10)
            response.raise_for_status()
            image_stream = BytesIO(response.content)
            
            # If it's a proper placeholder, insert_picture creates a NEW shape and replaces the placeholder
            # python-pptx's placeholder.insert_picture is the way.
            if hasattr(shape, 'insert_picture'):
                shape.insert_picture(image_stream)
            else:
                # Fallback if it's not a picture placeholder but we want to force it? 
                # For now stick to strict placeholder behavior.
                pass
                
        except Exception as e:
            print(f"Failed to load image: {e}")
            # Optionally set text to error message
            if shape.has_text_frame:
                shape.text = f"[Error loading image]"
