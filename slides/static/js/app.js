const app = {
    state: {
        step: 'config',
        templates: [],
        selectedTemplate: null,
        config: {},
        outline: [],
        slidesContent: []
    },

    init: async () => {
        console.log('App initialized');
        await app.loadTemplates();

        document.getElementById('config-form').addEventListener('submit', (e) => {
            e.preventDefault();
            app.generateOutline();
        });
    },

    loadTemplates: async () => {
        const container = document.getElementById('template-list');
        try {
            const res = await fetch('/api/templates/');
            const data = await res.json();
            app.state.templates = data.templates;

            container.innerHTML = '';
            data.templates.forEach((t, idx) => {
                const el = document.createElement('div');
                el.className = 'template-item';
                el.innerHTML = `<strong>${t.filename}</strong><br><small>${t.layouts.length} layouts</small>`;
                el.onclick = () => app.selectTemplate(t, el);
                container.appendChild(el);

                // Select first by default
                if (idx === 0) app.selectTemplate(t, el);
            });
        } catch (err) {
            container.innerHTML = '<div class="error">Failed to load templates. Is backend running?</div>';
        }
    },

    selectTemplate: (template, el) => {
        app.state.selectedTemplate = template;
        document.querySelectorAll('.template-item').forEach(e => e.classList.remove('selected'));
        el.classList.add('selected');
    },

    generateOutline: async () => {
        const topic = document.getElementById('input-topic').value;
        const grade = document.getElementById('input-grade').value;
        const duration = document.getElementById('input-duration').value || '45 minutes';

        if (!topic) return alert('Please enter a topic');
        if (!app.state.selectedTemplate) return alert('Please select a template');

        const btn = document.querySelector('button[type="submit"]');
        const origText = btn.innerText;
        btn.innerText = 'Generating Presentation...';
        btn.disabled = true;

        app.state.config = { topic, grade, duration };

        try {
            const res = await fetch('/api/generate/oneshot/', {
                method: 'POST',
                body: JSON.stringify({
                    topic, grade,
                    template_filename: app.state.selectedTemplate.filename
                })
            });
            const data = await res.json();

            if (data.error) throw new Error(data.error);

            // Set both outline and full content from the single response
            app.state.outline = data.slides;
            app.state.slidesContent = data.slides.map(s => ({
                layout_id: s.layout_id,
                content: s.content
            }));

            // Transition to generation view and start building immediately
            app.goToStep('generation');
            const progressBar = document.getElementById('gen-progress-bar');
            const statusText = document.getElementById('gen-status-details');

            progressBar.style.width = '100%';
            statusText.innerText = 'Content generated! Building PowerPoint...';

            await app.buildPresentation();
        } catch (err) {
            alert('Error generating presentation: ' + err.message);
        } finally {
            btn.innerText = origText;
            btn.disabled = false;
        }
    },

    renderOutline: () => {
        const container = document.getElementById('outline-container');
        container.innerHTML = '';

        app.state.outline.forEach((slide, idx) => {
            const el = document.createElement('div');
            el.className = 'outline-item';
            el.innerHTML = `
                <div class="outline-header">
                    <span>Slide ${slide.slide_number}: ${slide.title}</span>
                    <span class="badge">Layout ID: ${slide.layout_id}</span>
                </div>
                <div class="outline-purpose">${slide.purpose}</div>
            `;
            container.appendChild(el);
        });
    },

    startGeneration: async () => {
        app.goToStep('generation');
        const progressBar = document.getElementById('gen-progress-bar');
        const statusText = document.getElementById('gen-status-details');

        app.state.slidesContent = [];
        const total = app.state.outline.length;

        // Generate slides sequentially (could be parallel, but rate limits...)
        for (let i = 0; i < total; i++) {
            const slidePlan = app.state.outline[i];
            statusText.innerText = `Generating Slide ${i + 1}/${total}: ${slidePlan.title}...`;

            try {
                const res = await fetch('/api/generate/slide/', {
                    method: 'POST',
                    body: JSON.stringify({
                        title: slidePlan.title,
                        purpose: slidePlan.purpose,
                        grade: app.state.config.grade,
                        layout_id: slidePlan.layout_id,
                        template_filename: app.state.selectedTemplate.filename
                    })
                });
                const data = await res.json();

                app.state.slidesContent.push({
                    layout_id: slidePlan.layout_id,
                    content: data.content
                });

            } catch (err) {
                console.error('Slide gen failed', err);
            }

            // Update progress
            const percent = ((i + 1) / total) * 100;
            progressBar.style.width = `${percent}%`;
        }

        statusText.innerText = 'Assembling Presentation...';
        await app.buildPresentation();
    },

    buildPresentation: async () => {
        try {
            const res = await fetch('/api/build/', {
                method: 'POST',
                body: JSON.stringify({
                    template_filename: app.state.selectedTemplate.filename,
                    slides: app.state.slidesContent
                })
            });
            const data = await res.json();

            document.getElementById('gen-status-text').innerText = 'Done!';
            document.getElementById('gen-status-details').innerText = 'Your lesson is ready.';

            document.getElementById('final-actions').classList.remove('hidden');
            const dwBtn = document.getElementById('btn-download');
            dwBtn.onclick = () => window.location.href = data.download_url;

        } catch (err) {
            alert('Build failed: ' + err.message);
        }
    },

    goToStep: (stepName) => {
        app.state.step = stepName;
        document.querySelectorAll('.step-section').forEach(el => el.classList.add('hidden'));
        document.getElementById(`step-${stepName}`).classList.remove('hidden');
    },

    restart: () => {
        app.state.outline = [];
        app.state.slidesContent = [];
        app.goToStep('config');
    }
};

document.addEventListener('DOMContentLoaded', app.init);
