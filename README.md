# AI Lesson Planner - Quick Start

## ✅ What's Been Implemented

### Backend (Django + Python-PPTX + Gemini):
- ✅ Template analysis and management
- ✅ AI-powered lesson outline generation
- ✅ AI-powered slide content generation
- ✅ **NEW**: Image search integration (Google Custom Search API)
- ✅ PowerPoint file generation with images
- ✅ RESTful API endpoints

### Frontend (HTML/CSS/JS):
- ✅ Interactive step-by-step UI
- ✅ Template selection
- ✅ Lesson configuration form
- ✅ Outline review and editing
- ✅ Progress tracking during generation
- ✅ Download functionality

## 🔧 Setup Instructions

### 1. Install Dependencies (Already Done)
```bash
pip install django python-pptx google-generativeai python-dotenv
```

### 2. Add Your API Keys

Create a `.env` file in the project root:

```env
# REQUIRED - Get from: https://makersuite.google.com/app/apikey
GEMINI_API_KEY=your_gemini_api_key_here

# OPTIONAL - For real images instead of placeholders
# Get from: https://console.cloud.google.com/apis/credentials
GOOGLE_SEARCH_API_KEY=your_google_search_api_key_here
GOOGLE_SEARCH_ENGINE_ID=your_search_engine_id_here
```

**See `API_SETUP_GUIDE.md` for detailed instructions on getting these keys.**

### 3. Start the Server
```bash
python manage.py runserver
```

### 4. Open in Browser
Navigate to: **http://127.0.0.1:8000/**

## 📋 How to Use

1. **Select Template**: Choose "simple.pptx" (or add your own templates to `templates_source/`)
2. **Enter Topic**: e.g., "Volcanoes", "Photosynthesis", "Ancient Egypt"
3. **Set Grade Level**: e.g., "5th Grade", "High School"
4. **Choose Duration**: 30, 45, or 60 minutes
5. **Generate Outline**: AI creates a pedagogically sound slide structure
6. **Review & Edit**: Check the proposed slides
7. **Generate Content**: AI fills in all the text and image queries
8. **Download**: Get your PowerPoint file!

## 🖼️ Image Integration

### How It Works:
1. **AI generates image queries** like:
   - "photosynthesis diagram for 5th graders"
   - "volcano cross-section illustration"
   
2. **Backend searches Google Images** (if API configured)
   - Finds relevant, safe-for-school images
   - Inserts actual image URLs into the presentation
   
3. **Fallback**: If no API key, uses placeholder images

### To Enable Real Images:
- Follow `API_SETUP_GUIDE.md` to set up Google Custom Search
- Add keys to `.env` file
- Restart server

## 📁 Project Structure

```
Workspace for experiments/
├── .env                          # Your API keys (create this!)
├── .env.example                  # Template for .env
├── API_SETUP_GUIDE.md           # Detailed API setup instructions
├── manage.py                     # Django management
├── lesson_planner/              # Django project settings
│   ├── settings.py
│   └── urls.py
├── slides/                       # Main app
│   ├── services/
│   │   ├── template_engine.py   # PowerPoint handling
│   │   ├── gemini_service.py    # AI content generation
│   │   └── image_search.py      # NEW: Image search
│   ├── static/
│   │   ├── css/style.css        # Styling
│   │   └── js/app.js            # Frontend logic
│   ├── templates/
│   │   └── index.html           # Main UI
│   ├── views.py                 # API endpoints
│   └── urls.py
├── templates_source/            # Your .pptx templates
│   └── simple.pptx
└── media/                       # Generated presentations
```

## 🔌 API Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/templates/` | GET | List available templates |
| `/api/generate/outline/` | POST | Generate lesson outline |
| `/api/generate/slide/` | POST | Generate single slide content |
| `/api/search/images/` | POST | **NEW**: Search for images |
| `/api/build/` | POST | Build final PowerPoint |

## 🎨 Customization

### Add Your Own Templates:
1. Create a PowerPoint file with your desired layouts
2. Save it to `templates_source/`
3. Refresh the page - it will appear in the template selector

### Modify AI Prompts:
Edit `slides/services/gemini_service.py`:
- `generate_lesson_outline()` - Controls slide structure
- `generate_slide_content()` - Controls text content

### Customize UI:
- **Styling**: Edit `slides/static/css/style.css`
- **Layout**: Edit `slides/templates/index.html`
- **Logic**: Edit `slides/static/js/app.js`

## 🐛 Troubleshooting

### Server won't start:
```bash
python manage.py migrate
python manage.py runserver
```

### "GEMINI_API_KEY not set":
- Create `.env` file in project root
- Add your API key
- Restart server

### Images not working:
- Check if Google Search API keys are in `.env`
- System will use placeholders if keys are missing (this is OK!)

### Template not loading:
- Make sure `.pptx` file is in `templates_source/`
- Check file isn't corrupted
- Restart server

## 📚 Next Steps

1. **Get API Keys**: Follow `API_SETUP_GUIDE.md`
2. **Test the System**: Create a sample lesson
3. **Add Templates**: Create custom PowerPoint templates
4. **Customize Prompts**: Adjust AI behavior for your needs
5. **Share with UX Designer**: The frontend is ready for design improvements!

## 💡 Tips

- **Start Simple**: Test with basic topics first
- **Review Outlines**: Always check the AI-generated structure before generating content
- **Iterate**: Regenerate individual slides if needed (feature coming soon!)
- **Save Templates**: Keep successful presentations as templates

---

**Ready to create amazing lesson plans? Start the server and visit http://127.0.0.1:8000/**
