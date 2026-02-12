from nicegui import ui, app
import glob
import frontmatter
from datetime import datetime, date
import os
import re

# Get absolute path to the images directory
base_dir = os.path.dirname(os.path.abspath(__file__))
images_dir = os.path.join(base_dir, 'posts', 'images')
# Ensure directory exists
if not os.path.exists(images_dir):
    os.makedirs(images_dir, exist_ok=True)

app.add_static_files('/post/images', images_dir)

# --- INIT ---
try:
    if not hasattr(frontmatter, 'load'): raise ImportError
except:
    raise SystemExit("Install 'python-frontmatter', not 'frontmatter'")

# --- CONFIG ---
HERO_TITLE = "Montano.uk"
HERO_SUBTITLE = "Home Lab & Developer Blog"
LINKS = [
    {"name": "GitHub", "url": "https://github.com/yourusername", "icon": "code"},
    {"name": "Blog", "url": "/blog", "icon": "article"},
    {"name": "Email", "url": "mailto:you@example.com", "icon": "email"},
]

# --- LOGIC ---
def strip_markdown(text):
    """Removes markdown syntax from text."""
    # Remove headers (e.g. # Header)
    text = re.sub(r'^#+\s+', '', text, flags=re.MULTILINE)
    # Remove bold/italic (e.g. **bold**, *italic*)
    text = re.sub(r'(\*\*|__)(.*?)\1', r'\2', text)
    text = re.sub(r'(\*|_)(.*?)\1', r'\2', text)
    # Remove images (e.g. ![alt](url))
    text = re.sub(r'!\[(.*?)\]\(.*?\)', r'\1', text)
    # Remove links (e.g. [text](url))
    text = re.sub(r'\[(.*?)\]\(.*?\)', r'\1', text)
    # Remove code blocks (e.g. ```code```)
    text = re.sub(r'`{3}.*?`{3}', '', text, flags=re.DOTALL)
    # Remove inline code (e.g. `code`)
    text = re.sub(r'`(.*?)`', r'\1', text)
    # Remove blockquotes (e.g. > quote)
    text = re.sub(r'^>\s+', '', text, flags=re.MULTILINE)
    
    return text.strip()

def parse_date(date_str):
    """Parses date string into a datetime.date object."""
    if isinstance(date_str, datetime): return date_str.date()
    if isinstance(date_str, date): return date_str
    if not isinstance(date_str, str): return datetime.now().date()
    
    for fmt in ['%Y-%m-%d', '%d-%m-%Y', '%b %d, %Y', '%B %d, %Y']:
        try: return datetime.strptime(date_str, fmt).date()
        except: continue
    return datetime.now().date()

def get_posts():
    """Retrieves and processes all markdown blog posts."""
    if not os.path.exists("posts"): os.makedirs("posts", exist_ok=True)
    posts = []
    for file in glob.glob("posts/*.md"):
        try:
            post = frontmatter.load(file)
            clean_content = strip_markdown(post.content)
            posts.append({
                "title": post.get('title', 'Untitled'),
                "date": parse_date(post.get('date')),
                "content": post.content.strip(),
                "summary": clean_content[:126] + "...",
                "filename": os.path.basename(file)
            })
        except: continue
    return sorted(posts, key=lambda x: x['date'], reverse=True)

# --- UI HELPERS ---
def common_style():
    """Applies global styles and dark mode."""
    # Initialize Persistent Dark Mode logic early
    if 'dark_mode' not in app.storage.user:
        app.storage.user['dark_mode'] = False
        
    # Prevent FOUC: Conditionally inject CSS to force background color immediately
    # This runs in HEAD, before body exists, guaranteeing no white flash.
    if app.storage.user['dark_mode']:
        ui.add_head_html('''
            <style>
                html.dark body { background-color: #121212 !important; color: white !important; }
            </style>
            <script>
                document.documentElement.classList.add("dark");
            </script>
        ''')
    else:
        ui.add_head_html('''
            <script>
                document.documentElement.classList.remove("dark");
            </script>
        ''')

    ui.add_head_html('<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap" rel="stylesheet">')
    ui.add_head_html('''
        <style>
            body { font-family: 'Inter', sans-serif; background-color: white; color: #121212; transition: background-color 0.3s, color 0.3s; }
            /* Tailwind/NiceGUI often target body, but we support html.dark too for early loading */
            html.dark body, body.dark { background-color: #121212 !important; color: white !important; }
            
            .nicegui-content { padding: 0 !important; max-width: 100% !important; }
            a { text-decoration: none; color: inherit; }
        </style>
    ''')
    
    # Initialize UI Dark Mode Component
    dark = ui.dark_mode()
    dark.bind_value(app.storage.user, 'dark_mode')

    # Sync proper classes via JS for runtime toggles
    def sync_classes(e):
        if e.value:
            ui.run_javascript('document.documentElement.classList.add("dark"); document.body.classList.add("dark");')
        else:
            ui.run_javascript('document.documentElement.classList.remove("dark"); document.body.classList.remove("dark");')
    
    # Fix the toggle button state
    if dark.value:
        # Ensure consistency on python side load
        ui.run_javascript('document.body.classList.add("dark");')

    # Listener for changes
    dark.on_value_change(sync_classes)

def nav_header():
    """Renders the navigation header."""
    with ui.row().classes('w-full max-w-3xl justify-between items-center py-4 mb-6 border-b border-gray-200 dark:border-[#222]'):
        with ui.link(target='/').classes('headline-link'):
            ui.label(HERO_TITLE).classes('text-lg font-bold text-gray-900 dark:text-white tracking-tight hover:text-blue-600 dark:hover:text-blue-400 transition')
        
        with ui.row().classes('gap-6 items-center'):
            with ui.link(target='/').classes('text-sm text-gray-600 dark:text-white/60 hover:text-black dark:hover:text-white transition'):
                ui.label('Home')
            with ui.link(target='/blog').classes('text-sm text-gray-600 dark:text-white/60 hover:text-black dark:hover:text-white transition'):
                ui.label('Blog')
            
            # Dark Mode Toggle
            # Toggle storage directly; the binding in common_style handles the rest
            def toggle_dark():
                app.storage.user['dark_mode'] = not app.storage.user.get('dark_mode', False)
                
            with ui.button(icon='dark_mode', on_click=toggle_dark).props('flat round dense').classes('text-gray-600 dark:text-white/60 hover:text-black dark:hover:text-white'):
                pass

# --- PAGES ---

@ui.page('/')
def home():
    """Renders the landing page."""
    common_style()
    
    # Dark Mode Toggle (Absolute Position)
    def toggle_dark():
        app.storage.user['dark_mode'] = not app.storage.user.get('dark_mode', False)

    with ui.element('div').classes('absolute top-4 right-4 z-50'):
         with ui.button(icon='dark_mode', on_click=toggle_dark).props('flat round dense').classes('text-gray-600 dark:text-white/60 hover:text-black dark:hover:text-white'):
            pass

    with ui.column().classes('w-full h-screen items-center justify-center transition-colors duration-300'):
        ui.label(HERO_TITLE).classes('text-6xl md:text-8xl font-black tracking-tighter text-gray-900 dark:text-white/90 mb-4')
        ui.label(HERO_SUBTITLE).classes('text-xl md:text-2xl text-gray-500 dark:text-white/60 font-medium')
        
        with ui.row().classes('mt-12 gap-6'):
            for link in LINKS:
                with ui.link(target=link['url']):
                    with ui.row().classes('items-center gap-3 px-6 py-3 rounded-lg bg-gray-100 dark:bg-[#1e1e1e] hover:bg-gray-200 dark:hover:bg-[#252525] transition border border-gray-200 dark:border-[#333]'):
                        ui.icon(link['icon']).classes('text-xl text-gray-600 dark:text-white/80')
                        ui.label(link['name']).classes('text-sm font-semibold text-gray-700 dark:text-white/80')

@ui.page('/blog')
def blog():
    """Renders the blog index page."""
    common_style()
    with ui.column().classes('w-full min-h-screen items-center pt-4 px-4 transition-colors duration-300'):
        nav_header()
        
        with ui.column().classes('w-full max-w-3xl gap-6'):
            ui.label('Latest Writing').classes('text-xs font-bold text-gray-400 dark:text-white/40 uppercase tracking-widest mb-2')
            
            posts = get_posts()
            if not posts: ui.label('No posts found.').classes('text-gray-400 dark:text-white/40 italic')

            for post in posts:
                with ui.link(target=f"/post/{post['filename']}").classes('group w-full'):
                    with ui.column().classes('gap-1'): 
                        ui.label(post['title']).classes('text-xl font-bold text-gray-900 dark:text-white/90 group-hover:text-blue-600 dark:group-hover:text-blue-400 transition-colors')
                        ui.label(post['date'].strftime('%B %d, %Y')).classes('text-xs text-gray-400 dark:text-white/40 font-mono uppercase tracking-widest')
                        ui.label(post['summary']).classes('text-sm text-gray-600 dark:text-white/60 leading-relaxed max-w-2xl mt-1')

@ui.page('/post/{filename}')
def post_page(filename: str):
    """Renders an individual blog post page."""
    common_style()
    filepath = os.path.join("posts", filename)
    
    if not os.path.exists(filepath):
        ui.label('404').classes('text-red-500 m-10')
        return

    post = frontmatter.load(filepath)
    title = post.get('title', 'Untitled')
    date_obj = parse_date(post.get('date'))
    
    # Main Container
    with ui.column().classes(
        'w-full min-h-screen items-center '
        'pt-4 px-4 transition-colors duration-300'
    ):
        nav_header()
        
        # Content Column
        with ui.column().classes('w-full max-w-3xl gap-0'):
            
            # Back Button
            with ui.link(target='/blog').classes(
                'mb-4 flex items-center gap-2 text-gray-500 dark:text-white/50 '
                'hover:text-black dark:hover:text-white transition group'
            ):
                ui.icon('arrow_back').classes(
                    'text-sm group-hover:-translate-x-1 transition-transform'
                )
                ui.label('Back to Blog').classes('text-sm font-medium')

            # Title
            ui.label(title).classes(
                'text-4xl md:text-5xl font-black tracking-tight '
                'text-gray-900 dark:text-white mb-0 leading-tight'
            )
            
            # Date & Divider
            ui.label(date_obj.strftime('%B %d, %Y')).classes(
                'text-sm text-gray-400 dark:text-white/40 font-mono '
                'border-b border-gray-200 dark:border-[#222] w-full pt-2 pb-2 mb-4'
            )
            
            # Markdown Content
            ui.markdown(post.content).classes(
                'prose dark:prose-invert prose-lg max-w-none '
                'prose-headings:font-bold prose-headings:text-gray-900 dark:prose-headings:text-white/90 '
                'prose-p:text-gray-700 dark:prose-p:text-white/80 prose-a:text-blue-600 dark:prose-a:text-blue-400 '
                'prose-img:rounded-xl '
                'prose-h1:mt-0 prose-h2:mt-1 prose-p:mt-0'
            )

if __name__ in {"__main__", "__mp_main__"}:
    ui.run(host='0.0.0.0', port=8080, title='Montano.uk', storage_secret='montano_secret_key')