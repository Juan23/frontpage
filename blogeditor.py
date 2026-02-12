from nicegui import ui, app
import os
import frontmatter
from datetime import datetime

# Configuration
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
POSTS_DIR = os.path.join(BASE_DIR, 'posts')

# Ensure posts directory exists
if not os.path.exists(POSTS_DIR):
    os.makedirs(POSTS_DIR)

class BlogEditor:
    def __init__(self):
        self.current_file = None
        self.editor = None
        self.preview = None
        self.file_list = None
        
        # UI State
        self.content = ""

    def load_file(self, filename):
        """Loads a file into the editor"""
        filepath = os.path.join(POSTS_DIR, filename)
        if os.path.exists(filepath):
            with open(filepath, 'r', encoding='utf-8') as f:
                self.content = f.read()
            self.current_file = filename
            if self.editor:
                self.editor.value = self.content
            if self.preview:
                self.preview.content = self.content
            ui.notify(f'Loaded {filename}')
            self.refresh_title()
            self.refresh_file_list()

    def save_file(self):
        """Saves current content to file"""
        if not self.current_file:
            ui.notify('No file selected!', color='warning')
            return
            
        filepath = os.path.join(POSTS_DIR, self.current_file)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(self.editor.value)
        ui.notify('Saved successfully!', color='positive')

    def create_new_post(self):
        """Creates a new post template"""
        # Dialog to get filename
        with ui.dialog() as dialog, ui.card():
            ui.label('Create New Post')
            filename_input = ui.input('Filename (e.g., my-post.md)')
            
            def create():
                name = filename_input.value
                if not name:
                    return
                if not name.endswith('.md'):
                    name += '.md'
                
                # Basic frontmatter template
                template = f"""---
title: "New Post"
date: {datetime.now().strftime('%Y-%m-%d')}
author: Author
---

# New Post

Start writing here...
"""
                filepath = os.path.join(POSTS_DIR, name)
                if os.path.exists(filepath):
                    ui.notify('File already exists!', color='negative')
                    return
                
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(template)
                
                self.refresh_file_list()
                self.load_file(name)
                dialog.close()

            ui.button('Create', on_click=create)
            ui.button('Cancel', on_click=dialog.close, color='warning')

        dialog.open()

    def refresh_file_list(self):
        """Refreshes the file list in the sidebar"""
        self.file_list.clear()
        files = [f for f in os.listdir(POSTS_DIR) if f.endswith('.md')]
        with self.file_list:
            for file in files:
                active = file == self.current_file
                ui.button(file, on_click=lambda f=file: self.load_file(f)) \
                    .props(f'flat align=left {"color=primary" if active else ""}') \
                    .classes('w-full text-left rounded-md tracking-tight') \
                    .classes('bg-gray-100 dark:bg-zinc-800' if active else 'hover:bg-gray-100 dark:hover:bg-zinc-800 text-gray-700 dark:text-gray-400')

    def refresh_title(self):
        title = "MarkText Clone"
        if self.current_file:
            title += f" - {self.current_file}"
        ui.page_title(title)

    def handle_input(self, e):
        """Updates preview on input"""
        self.content = e.value
        self.preview.content = self.content # Direct binding might be slow for large docs, but OK for now

    def set_view_mode(self, mode):
        self.view_mode = mode
        if mode == 'Editor':
            self.editor_col.classes(remove='hidden w-1/2', add='w-full')
            self.preview_col.classes(remove='w-1/2', add='hidden')
        elif mode == 'Preview':
            self.editor_col.classes(remove='w-1/2', add='hidden')
            self.preview_col.classes(remove='hidden w-1/2', add='w-full')
        else: # Split
            self.editor_col.classes(remove='hidden w-full', add='w-1/2')
            self.preview_col.classes(remove='hidden w-full', add='w-1/2')

    def setup_ui(self):
        # Header
        with ui.header().classes('items-center justify-between border-b h-14') \
                .classes('bg-white text-slate-800 border-slate-200') \
                .classes('dark:bg-zinc-900 dark:text-slate-200 dark:border-zinc-800'):
            ui.label('MarkText Clone').classes('text-lg font-bold tracking-tight')
            with ui.row().classes('items-center gap-1'):
                with ui.button_group().props('flat'):
                    ui.button(icon='edit', on_click=lambda: self.set_view_mode('Editor')).tooltip('Editor Only')
                    ui.button(icon='vertical_split', on_click=lambda: self.set_view_mode('Split')).tooltip('Split View')
                    ui.button(icon='preview', on_click=lambda: self.set_view_mode('Preview')).tooltip('Preview Only')
                
                ui.separator().props('vertical spaced')
                ui.button(on_click=self.create_new_post, icon='add').props('flat round dense').tooltip('New Post')
                ui.button(on_click=self.save_file, icon='save').props('flat round dense').tooltip('Save')
                ui.switch(on_change=lambda e: ui.dark_mode(e.value)).props('color=grey-8 unchecked-icon=light_mode checked-icon=dark_mode transform').tooltip('Toggle Dark Mode')

        # Drawer (Sidebar)
        with ui.left_drawer(value=True).classes('border-r') \
                .classes('bg-gray-50 border-gray-200') \
                .classes('dark:bg-zinc-900 dark:border-zinc-800'):
            with ui.row().classes('w-full p-4 items-center justify-between border-b') \
                    .classes('border-gray-200 dark:border-zinc-800'):
                ui.label('EXPLORER').classes('text-xs font-bold tracking-widest') \
                    .classes('text-gray-400 dark:text-gray-500')
                ui.button(icon='refresh', on_click=self.refresh_file_list).props('flat round size=xs color=grey')
            
            self.file_list = ui.column().classes('w-full p-2 gap-1')
            self.refresh_file_list()

        # Main Content
        with ui.row().classes('w-full h-[calc(100vh-56px)] no-wrap gap-0') \
                .classes('bg-white dark:bg-zinc-950'):
            # Editor Pane (Left)
            self.editor_col = ui.column().classes('w-1/2 h-full border-r p-0') \
                .classes('border-gray-200 dark:border-zinc-800')
            with self.editor_col:
                self.editor = ui.codemirror(language='markdown', theme='dracula') \
                    .classes('w-full h-full text-base') \
                    .on('change', self.handle_input)
            
            # Preview Pane (Right)
            self.preview_col = ui.column().classes('w-1/2 h-full p-8 overflow-y-auto') \
                .classes('bg-white dark:bg-zinc-950 text-slate-900 dark:text-slate-300')
            with self.preview_col:
                self.preview = ui.markdown(self.content).classes('w-full prose max-w-none') \
                    .classes('dark:prose-invert')

        # Load first file if exists
        files = [f for f in os.listdir(POSTS_DIR) if f.endswith('.md')]
        if files:
            self.load_file(files[0])
        self.set_view_mode('Split')


@ui.page('/')
def main():
    app = BlogEditor()
    app.setup_ui()

ui.run(title="MarkText Clone", port=8080, reload=True)
