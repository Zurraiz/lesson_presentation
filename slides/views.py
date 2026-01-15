import os
import json
from django.conf import settings
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from .services.template_engine import TemplateManager
from .services.gemini_service import GeminiService
from .services.image_search import ImageSearchService

from django.shortcuts import render

TEMPLATES_DIR = os.path.join(settings.BASE_DIR, 'templates_source')

def home(request):
    """
    Serve the single page app (SPA).
    """
    return render(request, 'index.html')

@csrf_exempt
@require_http_methods(["GET"])
def list_templates(request):
    """
    List all available .pptx templates in the templates directory.
    """
    if not os.path.exists(TEMPLATES_DIR):
        os.makedirs(TEMPLATES_DIR)
        
    templates = []
    for f in os.listdir(TEMPLATES_DIR):
        if f.endswith(".pptx") and not f.startswith("~$"):
            path = os.path.join(TEMPLATES_DIR, f)
            try:
                tm = TemplateManager(path)
                layout_info = tm.analyze_template()
                templates.append({
                    "filename": f,
                    "layouts": layout_info["layouts"]
                })
            except Exception as e:
                print(f"Error loading {f}: {e}")
                
    return JsonResponse({"templates": templates})

@csrf_exempt
@require_http_methods(["POST"])
def generate_one_shot(request):
    """
    Generates entire presentation (Outline + Content) in one go.
    """
    try:
        data = json.loads(request.body)
        topic = data.get("topic")
        grade = data.get("grade")
        
        # Get defaults
        template_filename = data.get("template_filename", "modern_template.pptx")
        template_path = os.path.join(TEMPLATES_DIR, template_filename)
        
        tm = TemplateManager(template_path)
        layouts = tm.analyze_template().get("layouts", [])
        
        gemini = GeminiService()
        result = gemini.generate_full_presentation(topic, grade, "45 minutes", layouts)
        
        if not result or "slides" not in result:
             return JsonResponse({"error": "Failed to generate presentation"}, status=500)
             
        return JsonResponse({"slides": result["slides"], "outline": result["slides"]})
        
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def generate_outline(request):
    """
    Step 1: Generate a lesson outline (list of slides) based on topic.
    """
    try:
        data = json.loads(request.body)
        topic = data.get("topic")
        grade = data.get("grade")
        duration = data.get("duration", "45")
        template_filename = data.get("template_filename")
        
        template_path = os.path.join(TEMPLATES_DIR, template_filename)
        tm = TemplateManager(template_path)
        layouts = tm.analyze_template().get("layouts", [])
        
        gemini = GeminiService()
        outline = gemini.generate_lesson_outline(topic, grade, duration, layouts)
        
        if not outline:
            return JsonResponse({"error": "Failed to generate outline"}, status=500)
            
        return JsonResponse({"outline": outline})
        
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def generate_slide_content(request):
    """
    Step 2: Generate content for a single slide.
    """
    try:
        data = json.loads(request.body)
        slide_title = data.get("title")
        slide_purpose = data.get("purpose")
        grade_level = data.get("grade")
        layout_id = data.get("layout_id")
        template_filename = data.get("template_filename")
        
        # We need the layout schema to tell Gemini what buckets to fill
        template_path = os.path.join(TEMPLATES_DIR, template_filename)
        tm = TemplateManager(template_path)
        layouts = tm.analyze_template().get("layouts", [])
        
        target_layout = next((l for l in layouts if l['id'] == layout_id), None)
        if not target_layout:
             return JsonResponse({"error": "Invalid layout_id"}, status=400)
             
        gemini = GeminiService()
        content = gemini.generate_slide_content(slide_title, slide_purpose, target_layout['placeholders'], grade_level)
        
        return JsonResponse({"content": content})
        
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def search_images(request):
    """
    Search for images using Google Custom Search API
    """
    try:
        data = json.loads(request.body)
        query = data.get("query")
        num_results = data.get("num_results", 3)
        
        if not query:
            return JsonResponse({"error": "Query is required"}, status=400)
        
        image_service = ImageSearchService()
        results = image_service.search_images(query, num_results)
        
        return JsonResponse({"images": results})
        
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def build_presentation(request):
    """
    Step 3: Assemble the final PPTX file from the client's state.
    Automatically resolves image queries to actual URLs.
    """
    try:
        data = json.loads(request.body)
        template_filename = data.get("template_filename")
        slides_data = data.get("slides", []) # List of {layout_id, content}
        
        # Process slides to convert image queries to actual URLs
        image_service = ImageSearchService()
        
        for slide in slides_data:
            content = slide.get("content", {})
            for key, value in list(content.items()):
                # Check if this is an image query object
                if isinstance(value, dict) and value.get("type") == "image":
                    query = value.get("query")
                    if query:
                        # Get the best image URL for this query
                        image_url = image_service.get_best_image(query)
                        if image_url:
                            # Replace the query object with actual image data
                            content[key] = {
                                "type": "image",
                                "url": image_url
                            }
        
        template_path = os.path.join(TEMPLATES_DIR, template_filename)
        tm = TemplateManager(template_path)
        
        output_path = tm.create_presentation(slides_data)
        
        # Return the download URL (in dev, direct file path relative to media)
        filename = os.path.basename(output_path)
        return JsonResponse({"download_url": f"/media/{filename}"})
        
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
