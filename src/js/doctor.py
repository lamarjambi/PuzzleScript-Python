import json
import os
import re
import tkinter as tk
from tkinter import messagebox, filedialog
import requests

class PuzzleScriptEditor:
    def __init__(self, root):
        self.root = root
        self.root.title("PuzzleScript-like Editor")
        
        # editor state tracking
        self._editor_dirty = False
        self._editor_clean_state = ""
        
        # text widget to simulate CodeMirror
        self.text_area = tk.Text(root, wrap=tk.WORD, undo=True)
        self.text_area.pack(expand=True, fill='both')
        
        # bind events
        self.text_area.bind('<KeyRelease>', self.on_text_change)
        
        # menu setup
        self.setup_menu()
    
    def setup_menu(self):
        menubar = tk.Menu(self.root)
        
        # file menu
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Open", command=self.try_load_file)
        file_menu.add_command(label="Save", command=self.save_file)
        file_menu.add_command(label="Load Gist", command=self.try_load_gist)
        menubar.add_cascade(label="File", menu=file_menu)
        
        self.root.config(menu=menubar)
    
    def try_load_file(self):
        # check if current content is saaved
        if not self.can_exit():
            return
        
        filename = filedialog.askopenfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt")]
        )
        if filename:
            with open(filename, 'r') as file:
                content = file.read()
                self.text_area.delete('1.0', tk.END)
                self.text_area.insert('1.0', content)
                self.set_editor_clean()
    
    def try_load_gist(self):
        gist_id = tk.simpledialog.askstring("Load Gist", "Enter GitHub Gist ID:")
        if not gist_id:
            return
        
        try:
            gist_url = f'https://api.github.com/gists/{gist_id}'
            response = requests.get(gist_url)
            response.raise_for_status()
            
            gist_data = response.json()
            script_content = next(iter(gist_data['files'].values()))['content']
            
            self.text_area.delete('1.0', tk.END)
            self.text_area.insert('1.0', script_content)
            self.set_editor_clean()
        
        except requests.RequestException as e:
            messagebox.showerror("Error", f"Could not load Gist: {e}")
    
    def on_text_change(self, event=None):
        self.check_editor_dirty()
    
    def check_editor_dirty(self):
        current_content = self.text_area.get('1.0', tk.END)
        if current_content != self._editor_clean_state:
            self._editor_dirty = True
            self.root.title("PuzzleScript Editor *")
        else:
            self._editor_dirty = False
            self.root.title("PuzzleScript Editor")
    
    def set_editor_clean(self):
        self._editor_clean_state = self.text_area.get('1.0', tk.END)
        self._editor_dirty = False
        self.root.title("PuzzleScript Editor")
    
    def can_exit(self):
        # check if there are unsaved changes
        if not self._editor_dirty:
            return True
        
        response = messagebox.askyesno(
            "Unsaved Changes", 
            "You have unsaved changes. Are you sure you want to continue?"
        )
        return response
    
    def save_file(self):
        filename = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt")]
        )
        if filename:
            with open(filename, 'w') as file:
                file.write(self.text_area.get('1.0', tk.END))
            self.set_editor_clean()

def main():
    root = tk.Tk()
    editor = PuzzleScriptEditor(root)
    root.mainloop()

if __name__ == "__main__":
    main()