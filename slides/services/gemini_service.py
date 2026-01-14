import os
import json
import google.generativeai as genai
from django.conf import settings

class GeminiService:
    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            print("Warning: GEMINI_API_KEY not set.")
            self.model = None
        else:
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel('gemini-3-flash-preview')

    def generate_lesson_outline(self, topic, grade_level, duration, available_layouts):
        """
        Generates a sequence of slides with selected layouts.
        """
        prompt = f"""
        Act as an expert curriculum planner. Create a {duration}-minute lesson plan on "{topic}" for Grade {grade_level}.
        
        Available Slide Layouts (ID: Name - Description):
        {self._format_layouts_for_prompt(available_layouts)}
        
        Output a JSON array of objects. Each object represents a slide and must have:
        - "slide_number": int
        - "layout_id": int (Must be one of the available IDs)
        - "title": str (The main topic of this slide)
        - "purpose": str (Brief explanation of why this slide is here)
        - "content_plan": str (Brief notes on what content goes here)
        
        Ensure the lesson has a logical flow: Introduction -> Core Concepts -> Activity/Interaction -> Summary/Assessment.
        Strictly limit the output to exactly 5 slides.
        Output purely JSON, no markdown formatting.
        """
        
        return self._call_gemini_json(prompt)

    def generate_slide_content(self, slide_title, slide_purpose, layout_schema, grade_level):
        """
        Generates specific text content for a slide's placeholders.
        """
        prompt = f"""
        Write the content for a presentation slide.
        Topic: {slide_title}
        Purpose: {slide_purpose}
        Target Audience: Grade {grade_level}
        
        The slide uses a layout with specific placeholders. You must provide content for each relevant placeholder.
        
        Placeholders Schema:
        {json.dumps(layout_schema, indent=2)}
        
        Instructions:
        1. Return a JSON object where keys are the Placeholder Indices (as strings) and values are the text content.
        2. Content must be educational, engaging, and appropriate for the grade level.
        3. Do NOT include markdown in the values (no **bold**, etc will render as literal stars in PPT).
        4. For 'image' placeholders OR generic 'content' placeholders where a visual aids understanding, generate a "search_query" object: {{"type": "image", "query": "KEYWORD SEARCH TERMS"}}.
           - The query MUST be simple, effective keywords for Google Images (2-4 words max).
           - Good: "photosynthesis diagram", "Abraham Lincoln portrait", "DNA double helix"
           - Bad: "a diagram showing how photosynthesis works for 5th grade students" (Too specific, will fail)
        5. Prioritize including at least one image per slide if the layout permits.
        6. **IMPORTANT**: Do NOT use bullet points (* or -) in the text. PowerPoint adds bullets automatically. Just separate distinct points with newlines.
        
        Output purely JSON.
        """
        
        return self._call_gemini_json(prompt)

    def _format_layouts_for_prompt(self, layouts):
        lines = []
        for l in layouts:
            # layout is dict from TemplateManager.analyze_template
            # l['name'], l['placeholders'], l['id']
            ph_names = [p['name'] for p in l['placeholders']]
            lines.append(f"ID {l['id']}: {l['name']} (Slots: {', '.join(ph_names)})")
        return "\n".join(lines)

    def _call_gemini_json(self, prompt):
        if self.model is None:
            print("Gemini Error: API key not configured")
            return None
            
        try:
            # We enforce JSON mode via prompt instructions + parsing
            # Depending on gemini version, we might use generation_config={'response_mime_type': 'application/json'}
            response = self.model.generate_content(
                prompt,
                generation_config={'response_mime_type': 'application/json'}
            )
            print('--------------')
            print(response)
            return json.loads(response.text)
        except Exception as e:
            print(f"Gemini Error: {e}")
            # Mock fallback for dev/testing if API fails
            return None
