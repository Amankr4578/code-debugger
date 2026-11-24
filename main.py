import google.generativeai as genai
import tkinter as tk
from tkinter import scrolledtext, ttk
import tkinter.font as tkfont
import os
from dotenv import load_dotenv

load_dotenv()
GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY")
if GOOGLE_API_KEY:
    genai.configure(api_key=GOOGLE_API_KEY)

# Add more programming languages with icons
LANGUAGES = ["Python", "Java", "C++", "JavaScript", "C#", "Go", "Rust", "PHP", "Swift", "TypeScript", "Kotlin", "Ruby"]

# Add language-specific syntax highlighting hints (optional)
LANGUAGE_HINTS = {
    "Python": ["def", "class", "import", "for", "while", "if", "elif", "else", "try", "except"],
    "Java": ["public", "class", "static", "void", "int", "String", "boolean", "try", "catch"],
    "JavaScript": ["function", "const", "let", "var", "if", "for", "while", "try", "catch", "async", "await"]
    # Add more as needed
}

# Add debugging modes
DEBUG_MODES = ["Standard Debugging", "Performance Analysis", "Security Review", "Code Explanation"]

# Light mode color scheme with more vibrant colors
BG_COLOR = "#f0f4f8"  # Light blue-gray background
TEXT_COLOR = "#2d3748"  
BUTTON_COLOR = "#4361ee" 
INPUT_BG = "#ffffff"  
INPUT_TEXT = "#212529"
ACCENT_COLOR = "#4f46e5"  # Indigo
DIVIDER_COLOR = "#cbd5e0"
USER_MSG_COLOR = "#047857"  # Teal
BOT_MSG_COLOR = "#b45309"  # Amber
HIGHLIGHT_COLOR = "#06b6d4"  # Cyan
BUTTON_BG = "#3b82f6"  # Blue
BUTTON_HOVER = "#2563eb"  # Darker blue
SECONDARY_BG = "#e2e8f0"  # Light slate
TITLE_BG = "#dbeafe"  # Very light blue

BOT_CODE_COLOR = "#1e40af"  # Dark blue for code
BOT_HEADING_COLOR = "#b45309"  # Amber for headings
BOT_EXPLANATION_COLOR = "#374151"  # Dark gray for explanations
BOT_SUCCESS_COLOR = "#065f46"  # Dark green for success messages
BOT_ERROR_COLOR = "#991b1b"  # Dark red for errors
BOT_HIGHLIGHT_COLOR = "#4f46e5"  # Purple for important points

def format_bot_response(response, language):
    """Format the bot's response to highlight code blocks and explanations"""
    formatted_text = ""
    lines = response.split('\n')
    in_code_block = False
    code_block = []
    
    for line in lines:
        # Check for code block markers ```
        if line.strip().startswith('```') or line.strip() == '```':
            if in_code_block:
                # End of code block
                formatted_text += "\n⟪CODE⟫\n"
                code_text = "\n".join(code_block)
                formatted_text += code_text + "\n"
                formatted_text += "⟪/CODE⟫\n\n"
                code_block = []
                in_code_block = False
            else:
                # Start of code block
                in_code_block = True
            continue
        
        if in_code_block:
            # Collect code block lines
            code_block.append(line)
        else:
            # Regular text - check for special formatting
            if line.strip().startswith('#') or line.strip().startswith('##'):
                # Heading
                formatted_text += "⟪HEADING⟫" + line + "⟪/HEADING⟫\n"
            elif line.strip().startswith('- ') or line.strip().startswith('* '):
                # List item
                formatted_text += "⟪LIST⟫" + line + "⟪/LIST⟫\n"
            elif "ERROR" in line.upper() or "ISSUE" in line.upper():
                # Error or issue description
                formatted_text += "⟪ERROR⟫" + line + "⟪/ERROR⟫\n"
            elif "FIXED" in line.upper() or "SOLUTION" in line.upper():
                # Solution or fix
                formatted_text += "⟪SUCCESS⟫" + line + "⟪/SUCCESS⟫\n"
            else:
                # Regular explanation text
                formatted_text += line + "\n"
    
    # Handle any remaining code block
    if code_block:
        formatted_text += "\n⟪CODE⟫\n"
        code_text = "\n".join(code_block)
        formatted_text += code_text + "\n"
        formatted_text += "⟪/CODE⟫\n\n"
    
    return formatted_text

def get_debugging_response(user_input, language, mode="Standard Debugging"):
    """Send the user's input code & language to Gemini AI for debugging."""
    try:
        model = genai.GenerativeModel("gemini-1.5-pro-latest") 
        
        # Different prompts based on mode
        if mode == "Standard Debugging":
            prompt = f"""Debug this {language} code:
```{language}
{user_input}
```

Please provide:
1. A clear explanation of any issues found
2. The corrected code blocks using markdown triple backticks
3. Explanations of why the fixes work
"""
        elif mode == "Performance Analysis":
            prompt = f"""Analyze this {language} code for performance issues:
```{language}
{user_input}
```

Please provide:
1. Performance bottlenecks identified
2. Optimized code blocks using markdown triple backticks
3. Explanation of how the optimizations improve performance
"""
        elif mode == "Security Review":
            prompt = f"""Review this {language} code for security vulnerabilities:
```{language}
{user_input}
```

Please provide:
1. Security issues identified
2. Secure code alternatives using markdown triple backticks
3. Explanation of the security risks and how the fixes address them
"""
        elif mode == "Code Explanation":
            prompt = f"""Explain this {language} code in simple terms:
```{language}
{user_input}
```

Please provide:
1. A high-level overview of what this code does
2. A step-by-step breakdown of key sections (with code snippets in triple backticks)
3. Explanations of any complex or important concepts
"""
        else:
            # Fallback to standard debugging
            prompt = f"Debug this {language} code:\n{user_input}\nProvide fixes and explanations."
            
        response = model.generate_content(prompt)
        raw_text = response.text if response.text else "No response from AI."
        formatted_text = format_bot_response(raw_text, language)
        return formatted_text
    except Exception as e:
        return f"Error: {str(e)}"

def basic_syntax_highlight(text, language):
    """Applies very simple syntax highlighting for code display"""
    if language in LANGUAGE_HINTS:
        for keyword in LANGUAGE_HINTS[language]:
            # This is a simplified approach - a real syntax highlighter would be more complex
            text = text.replace(f" {keyword} ", f" <keyword>{keyword}</keyword> ")
    return text

def send_message():
    """Handles user input, sends it to Gemini AI, and displays the response."""
    user_input = user_entry.get("1.0", tk.END).strip()
    selected_language = language_var.get()
    selected_mode = mode_var.get()  # Get mode directly from the variable

    if user_input and user_input != placeholder_text:
        # Show request in history with the selected mode
        chat_history.config(state=tk.NORMAL)
        chat_history.insert(tk.END, f"\n🧑‍💻 You ({selected_language}) - {selected_mode}:\n", "user_heading")
        chat_history.insert(tk.END, f"{user_input}\n\n", "user")
        chat_history.insert(tk.END, "─" * 80 + "\n", "divider")
        
        # Update status with the mode
        status_bar.config(text=f"Processing your code with {selected_mode}... Please wait")
        root.update()

        # Show loading message with the mode
        chat_history.insert(tk.END, f"🤖 Bot: Analyzing your code ({selected_mode})...\n", "bot_heading")
        chat_history.config(state=tk.DISABLED)
        chat_history.yview(tk.END)
        root.update()

        # Get AI response with the selected mode
        response = get_debugging_response(user_input, selected_language, selected_mode)
        
        # Update status
        status_bar.config(text="Ready to debug more code")
        
        # Update with actual response
        chat_history.config(state=tk.NORMAL)
        chat_history.delete("end-2l", "end-1c")  # Remove loading message
        chat_history.insert(tk.END, "🤖 Bot:\n", "bot_heading")
        
        # Insert formatted response with appropriate tags
        current_pos = chat_history.index(tk.END)
        chat_history.insert(tk.END, response, "bot")
        
        # Apply formatting tags
        find_and_tag(chat_history, "⟪CODE⟫", "⟪/CODE⟫", "code")
        find_and_tag(chat_history, "⟪HEADING⟫", "⟪/HEADING⟫", "heading")
        find_and_tag(chat_history, "⟪LIST⟫", "⟪/LIST⟫", "list")
        find_and_tag(chat_history, "⟪ERROR⟫", "⟪/ERROR⟫", "error")
        find_and_tag(chat_history, "⟪SUCCESS⟫", "⟪/SUCCESS⟫", "success")
        
        # Remove the marker tags
        remove_markers(chat_history)
        
        chat_history.insert(tk.END, "\n\n", "bot")
        chat_history.insert(tk.END, "═" * 80 + "\n", "separator")
        chat_history.config(state=tk.DISABLED)
        
        chat_history.yview(tk.END)
        user_entry.delete("1.0", tk.END)
        add_placeholder(None)

def find_and_tag(text_widget, start_marker, end_marker, tag_name):
    """Find text between markers and apply the specified tag"""
    text = text_widget.get("1.0", tk.END)
    current_index = "1.0"
    
    while True:
        start_index = text_widget.search(start_marker, current_index, tk.END)
        if not start_index:
            break
            
        end_index = text_widget.search(end_marker, start_index, tk.END)
        if not end_index:
            break
            
        # Apply tag to the text between markers (excluding markers)
        marker_length = len(start_marker)
        start_text_index = f"{start_index}+{marker_length}c"
        text_widget.tag_add(tag_name, start_text_index, end_index)
        
        # Move to search after this occurrence
        current_index = f"{end_index}+{len(end_marker)}c"

def remove_markers(text_widget):
    """Remove all marker tags from the text"""
    markers = ["⟪CODE⟫", "⟪/CODE⟫", "⟪HEADING⟫", "⟪/HEADING⟫", 
              "⟪LIST⟫", "⟪/LIST⟫", "⟪ERROR⟫", "⟪/ERROR⟫", 
              "⟪SUCCESS⟫", "⟪/SUCCESS⟫"]
    
    for marker in markers:
        current_index = "1.0"
        while True:
            marker_index = text_widget.search(marker, current_index, tk.END)
            if not marker_index:
                break
                
            end_index = f"{marker_index}+{len(marker)}c"
            text_widget.delete(marker_index, end_index)
            current_index = marker_index  # Continue from this position

def clear_placeholder(event):
    if user_entry.get("1.0", "end-1c") == placeholder_text:
        user_entry.delete("1.0", "end")
        user_entry.config(fg=INPUT_TEXT)

def add_placeholder(event):
    if not event or user_entry.get("1.0", "end-1c").strip() == "":
        user_entry.delete("1.0", "end")
        user_entry.insert("1.0", placeholder_text)
        user_entry.config(fg="gray")

def configure_styles():
    """Configure ttk styles for widgets"""
    style = ttk.Style()
    
    # Configure the combobox style
    style.configure("TCombobox", 
                    fieldbackground=INPUT_BG,
                    background=INPUT_BG,
                    foreground=TEXT_COLOR,
                    arrowcolor=ACCENT_COLOR,
                    borderwidth=0)
                    
    style.map('TCombobox', 
              fieldbackground=[('readonly', INPUT_BG)],
              selectbackground=[('readonly', HIGHLIGHT_COLOR)],
              selectforeground=[('readonly', "white")])

def create_custom_scrollbar(widget):
    """Create custom scrollbars for the widget"""
    # Create a custom scrollbar style
    style = ttk.Style()
    style.configure("Custom.Vertical.TScrollbar",
                    gripcount=0,
                    background=ACCENT_COLOR,
                    troughcolor=SECONDARY_BG,
                    borderwidth=0,
                    arrowsize=14)
    
    # Create and attach scrollbar
    scrollbar = ttk.Scrollbar(widget.master, orient="vertical", 
                            command=widget.yview, 
                            style="Custom.Vertical.TScrollbar")
    scrollbar.place(relx=1, rely=0, relheight=1, anchor='ne')
    widget.configure(yscrollcommand=scrollbar.set)
    return scrollbar

# Set up the main window
root = tk.Tk()
root.title("🌟 Code Guardian - AI Debugging Assistant")
root.geometry("1100x900")
root.configure(bg=BG_COLOR)
root.minsize(900, 700)

# Configure ttk styles
configure_styles()

# Create a main container frame for better layout control
main_container = tk.Frame(root, bg=BG_COLOR)
main_container.pack(fill=tk.BOTH, expand=True)

# App title with gradient effect - reduce padding to save space
title_frame = tk.Frame(main_container, bg=TITLE_BG, pady=10, relief=tk.GROOVE, borderwidth=1)
title_frame.pack(fill=tk.X)

title_font = tkfont.Font(family="Arial", size=22, weight="bold")
title_label = tk.Label(title_frame, text="Code Guardian", 
                     font=title_font, bg=TITLE_BG, fg=ACCENT_COLOR)
title_label.pack()

subtitle_font = tkfont.Font(family="Arial", size=12)
subtitle_label = tk.Label(title_frame, text="AI-Powered Debugging Assistant", 
                        font=subtitle_font, bg=TITLE_BG, fg=TEXT_COLOR)
subtitle_label.pack()

# Center content frame with slight pattern
content_frame = tk.Frame(main_container, bg=BG_COLOR, relief=tk.RIDGE, borderwidth=1)
content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=5)  # Reduced padding

# Create decorative header - reduce height
header_canvas = tk.Canvas(content_frame, height=5, bg=BG_COLOR, highlightthickness=0)
header_canvas.pack(fill=tk.X)
for i in range(20):
    x = i * 55
    header_canvas.create_rectangle(x, 0, x+50, 5, fill=ACCENT_COLOR, outline="")

# Chat history section - limit height more precisely
history_frame = tk.Frame(content_frame, bg=BG_COLOR, padx=5, pady=3)  # Reduced padding
history_frame.pack(fill=tk.BOTH, expand=True, side=tk.TOP)

history_label = tk.Label(history_frame, text="Debugging Conversation", 
                       font=("Arial", 12, "bold"), bg=BG_COLOR, fg=ACCENT_COLOR, anchor='w')
history_label.pack(fill=tk.X, pady=(0, 5))

chat_history = scrolledtext.ScrolledText(history_frame, wrap=tk.WORD, 
                                       height=12,  # Reduced height
                                       font=("Consolas", 11),
                                       bg=INPUT_BG, fg=TEXT_COLOR, 
                                       insertbackground=TEXT_COLOR, 
                                       borderwidth=1, relief=tk.GROOVE,
                                       padx=10, pady=10,
                                       selectbackground=HIGHLIGHT_COLOR)
chat_history.pack(fill=tk.BOTH, expand=True)
chat_history.config(state=tk.DISABLED)

# Configure text tags for different message types
chat_history.tag_configure("user", foreground=USER_MSG_COLOR)
chat_history.tag_configure("user_heading", foreground=USER_MSG_COLOR, font=("Consolas", 11, "bold"))
chat_history.tag_configure("bot", foreground=BOT_MSG_COLOR)
chat_history.tag_configure("bot_heading", foreground=BOT_MSG_COLOR, font=("Consolas", 11, "bold"))
chat_history.tag_configure("divider", foreground=DIVIDER_COLOR)
chat_history.tag_configure("separator", foreground=DIVIDER_COLOR)

# Add specialized formatting tags for bot responses
chat_history.tag_configure("code", foreground=BOT_CODE_COLOR, background="#f8fafc", 
                         font=("Consolas", 11), spacing1=5, spacing3=5, relief=tk.GROOVE, 
                         borderwidth=1, lmargin1=20, lmargin2=20, rmargin=10)
chat_history.tag_configure("heading", foreground=BOT_HEADING_COLOR, 
                         font=("Arial", 11, "bold"), spacing1=10, spacing3=5)
chat_history.tag_configure("list", foreground=BOT_EXPLANATION_COLOR, lmargin1=20)
chat_history.tag_configure("error", foreground=BOT_ERROR_COLOR, font=("Consolas", 11))
chat_history.tag_configure("success", foreground=BOT_SUCCESS_COLOR, font=("Consolas", 11))

# Create custom scrollbar for chat history
create_custom_scrollbar(chat_history)

# Language selection frame - reduce padding
lang_frame = tk.Frame(content_frame, bg=SECONDARY_BG, pady=5, padx=5, relief=tk.FLAT)
lang_frame.pack(fill=tk.X)

tk.Label(lang_frame, text="Programming Language:", 
       font=("Arial", 11, "bold"), fg=TEXT_COLOR, bg=SECONDARY_BG).pack(side=tk.LEFT, padx=5)

language_var = tk.StringVar()
language_var.set("Python")  # Default language
language_menu = ttk.Combobox(lang_frame, textvariable=language_var, 
                           values=LANGUAGES, state="readonly", 
                           font=("Arial", 11), width=15)
language_menu.pack(side=tk.LEFT, padx=5)

# Add a file load button next to the language selection
file_button = tk.Button(lang_frame, text="📂 Load File", 
                     font=("Arial", 11),
                     bg=BUTTON_BG, fg="white",
                     activebackground=BUTTON_HOVER,
                     activeforeground="white",
                     padx=10, pady=5,
                     relief=tk.RAISED,
                     borderwidth=1,
                     cursor="hand2",
                     command=lambda: load_file())
file_button.pack(side=tk.RIGHT, padx=10)

def load_file():
    """Load code from a file"""
    from tkinter import filedialog
    
    file_path = filedialog.askopenfilename(
        title="Select Code File",
        filetypes=(
            ("Python files", "*.py"),
            ("Java files", "*.java"),
            ("C++ files", "*.cpp *.h"),
            ("JavaScript files", "*.js"),
            ("C# files", "*.cs"),
            ("All files", "*.*")
        )
    )
    
    if file_path:
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                code = file.read()
                user_entry.delete("1.0", tk.END)
                user_entry.insert("1.0", code)
                user_entry.config(fg=INPUT_TEXT)
                
                # Try to detect language from file extension
                ext = file_path.split('.')[-1].lower()
                lang_map = {
                    'py': 'Python',
                    'java': 'Java', 
                    'cpp': 'C++', 'h': 'C++',
                    'js': 'JavaScript',
                    'cs': 'C#',
                    'go': 'Go',
                    'rs': 'Rust'
                }
                
                if ext in lang_map and lang_map[ext] in LANGUAGES:
                    language_var.set(lang_map[ext])
                    
                # Update status
                status_bar.config(text=f"Loaded file: {file_path.split('/')[-1]}")
        except Exception as e:
            status_bar.config(text=f"Error loading file: {str(e)}")

# After the language selection frame, add a debugging mode selection with a callback
mode_frame = tk.Frame(content_frame, bg=SECONDARY_BG, pady=5, padx=5, relief=tk.FLAT)
mode_frame.pack(fill=tk.X, pady=(0, 3))  # Reduced padding

tk.Label(mode_frame, text="Debug Mode:", 
       font=("Arial", 11, "bold"), fg=TEXT_COLOR, bg=SECONDARY_BG).pack(side=tk.LEFT, padx=5)

mode_var = tk.StringVar()
mode_var.set("Standard Debugging")  # Default mode

# Add a callback when mode is changed
def mode_changed(event=None):
    # Update button appearance based on mode
    mode = mode_var.get()
    if mode == "Standard Debugging":
        send_button.config(text="DEBUG CODE", bg="#059669")
    elif mode == "Performance Analysis":
        send_button.config(text="ANALYZE PERFORMANCE", bg="#0369a1")  # Blue shade
    elif mode == "Security Review":
        send_button.config(text="CHECK SECURITY", bg="#b91c1c")  # Red shade
    elif mode == "Code Explanation":
        send_button.config(text="EXPLAIN CODE", bg="#9333ea")  # Purple shade
    
    # Reset pulsing to the new color
    on_leave(None)

mode_menu = ttk.Combobox(mode_frame, textvariable=mode_var, 
                       values=DEBUG_MODES, state="readonly", 
                       font=("Arial", 11), width=20)
mode_menu.pack(side=tk.LEFT, padx=5)
mode_menu.bind("<<ComboboxSelected>>", mode_changed)

# Input area with label - with subtle shadow effect
input_frame = tk.Frame(content_frame, bg=BG_COLOR, padx=5, pady=3)  # Reduced padding
input_frame.pack(fill=tk.BOTH, expand=True, side=tk.TOP, pady=(3, 8))

input_label = tk.Label(input_frame, text="Your Code:", 
                     font=("Arial", 12, "bold"), bg=BG_COLOR, fg=ACCENT_COLOR, anchor='w')
input_label.pack(fill=tk.X, pady=(0, 5))

# Create a frame for the text entry with a subtle shadow effect
entry_container = tk.Frame(input_frame, bg=TEXT_COLOR, bd=0)
entry_container.pack(fill=tk.BOTH, expand=True, padx=1, pady=1)

user_entry = tk.Text(entry_container, height=6,  # Reduced height
                   font=("Consolas", 11), bg=INPUT_BG, fg=INPUT_TEXT, 
                   insertbackground=TEXT_COLOR, padx=10, pady=10,
                   borderwidth=0, 
                   selectbackground=HIGHLIGHT_COLOR)
user_entry.pack(fill=tk.BOTH, expand=True)

# Create custom scrollbar for user input
create_custom_scrollbar(user_entry)

placeholder_text = "Enter your code here..."
user_entry.insert("1.0", placeholder_text)
user_entry.config(fg="gray")

user_entry.bind("<FocusIn>", clear_placeholder)
user_entry.bind("<FocusOut>", add_placeholder)

# IMPORTANT: Create a dedicated frame for buttons with gradient effect
button_frame = tk.Frame(main_container, bg=SECONDARY_BG, height=100, pady=10)  # Increased height
button_frame.pack(side=tk.BOTTOM, fill=tk.X)
button_frame.pack_propagate(False)  # Ensure the frame stays at fixed height

# Add decorative footer
footer_canvas = tk.Canvas(button_frame, height=5, bg=SECONDARY_BG, highlightthickness=0)
footer_canvas.pack(fill=tk.X, side=tk.TOP)
for i in range(40):
    x = i * 30
    color = BUTTON_BG if i % 2 == 0 else ACCENT_COLOR
    footer_canvas.create_rectangle(x, 0, x+25, 5, fill=color, outline="")

# Button container centered in the button frame
button_container = tk.Frame(button_frame, bg=SECONDARY_BG, pady=20)  # Increased padding
button_container.pack(fill=tk.NONE, expand=True)

# Clear button
clear_button = tk.Button(button_container, text="Clear", 
                      font=("Arial", 12), 
                      bg="#6c757d", fg="white", 
                      activebackground="#5a6268",
                      activeforeground="white",
                      padx=20, pady=8,
                      relief=tk.RAISED,
                      borderwidth=1,
                      cursor="hand2",
                      command=lambda: (user_entry.delete("1.0", tk.END), add_placeholder(None)))
clear_button.pack(side=tk.LEFT, padx=10)

# Debug button with enhanced styling
debug_button_frame = tk.Frame(button_container, bg="#134e4a", padx=2, pady=2, borderwidth=2, relief=tk.RAISED)
debug_button_frame.pack(side=tk.LEFT, padx=15)

send_button = tk.Button(debug_button_frame, text="DEBUG CODE", command=send_message, 
                      font=("Arial", 14, "bold"), 
                      bg="#059669", fg="white",  # Bright green for visibility
                      activebackground="#047857",
                      activeforeground="white",
                      padx=30, pady=10,
                      relief=tk.RAISED,
                      borderwidth=0,
                      cursor="hand2")
send_button.pack()

# Add a pulsing effect to make it more noticeable
def pulse_button():
    current_mode = mode_var.get()
    current_bg = send_button.cget("background")
    
    # Base and pulse colors for different modes
    colors = {
        "Standard Debugging": ("#059669", "#047857"),
        "Performance Analysis": ("#0369a1", "#075985"),
        "Security Review": ("#b91c1c", "#991b1b"),
        "Code Explanation": ("#9333ea", "#7e22ce")
    }
    
    base_color, pulse_color = colors.get(current_mode, ("#059669", "#047857"))
    
    if current_bg == base_color:
        send_button.config(background=pulse_color)
    else:
        send_button.config(background=base_color)
        
    root.after(1500, pulse_button)  # Pulse every 1.5 seconds

# Start the pulsing effect after a short delay
root.after(3000, pulse_button)

# Add a hover effect to the send button with mode awareness
def on_enter(e):
    current_mode = mode_var.get()
    
    # Hover colors for different modes
    hover_colors = {
        "Standard Debugging": "#10b981",  # Lighter green
        "Performance Analysis": "#0ea5e9",  # Lighter blue
        "Security Review": "#dc2626",  # Lighter red
        "Code Explanation": "#a855f7"  # Lighter purple
    }
    
    hover_color = hover_colors.get(current_mode, "#10b981")
    send_button['background'] = hover_color
    
def on_leave(e):
    current_mode = mode_var.get()
    
    # Base colors for different modes
    base_colors = {
        "Standard Debugging": "#059669",  # Green
        "Performance Analysis": "#0369a1",  # Blue
        "Security Review": "#b91c1c",  # Red
        "Code Explanation": "#9333ea"  # Purple
    }
    
    base_color = base_colors.get(current_mode, "#059669")
    send_button['background'] = base_color

send_button.bind("<Enter>", on_enter)
send_button.bind("<Leave>", on_leave)

# Add a save response button 
save_button = tk.Button(button_container, text="💾 Save", 
                     font=("Arial", 12),
                     bg="#6c757d", fg="white", 
                     activebackground="#5a6268",
                     activeforeground="white",
                     padx=15, pady=8,
                     relief=tk.RAISED,
                     borderwidth=1,
                     cursor="hand2",
                     command=lambda: save_response())
save_button.pack(side=tk.LEFT, padx=10)

def save_response():
    """Save the current conversation to a file"""
    from tkinter import filedialog
    import datetime
    
    file_path = filedialog.asksaveasfilename(
        title="Save Debugging Session",
        defaultextension=".txt",
        filetypes=(
            ("Text files", "*.txt"),
            ("All files", "*.*")
        ),
        initialfile=f"debug_session_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    )
    
    if file_path:
        try:
            content = chat_history.get("1.0", tk.END)
            # Strip out the styling tags for plain text
            with open(file_path, 'w', encoding='utf-8') as file:
                file.write(content)
            status_bar.config(text=f"Session saved to: {file_path.split('/')[-1]}")
        except Exception as e:
            status_bar.config(text=f"Error saving file: {str(e)}")

# Status bar at the bottom with less height
status_frame = tk.Frame(root, height=20, bg=SECONDARY_BG)  # Reduced height
status_frame.pack(side=tk.BOTTOM, fill=tk.X)

status_bar = tk.Label(status_frame, text="Ready to debug your code", 
                    font=("Arial", 9), bg=SECONDARY_BG, fg=TEXT_COLOR, 
                    anchor='e', padx=10, pady=3)
status_bar.pack(fill=tk.X)

# Welcome message
chat_history.config(state=tk.NORMAL)
chat_history.insert(tk.END, "🤖 Code Guardian:\n", "bot_heading")
chat_history.insert(tk.END, "Welcome to Code Guardian! I'm here to help debug and improve your code. Here's how to use me:\n\n", "bot")
chat_history.insert(tk.END, "1. Select your programming language from the dropdown\n", "bot")
chat_history.insert(tk.END, "2. Choose a debugging mode based on your needs\n", "bot")
chat_history.insert(tk.END, "3. Paste your code in the box below or use the 'Load File' button\n", "bot")
chat_history.insert(tk.END, "4. Click 'DEBUG CODE' or press Ctrl+Enter to analyze\n\n", "bot")
chat_history.insert(tk.END, "Ready to make your code better!\n\n", "bot")
chat_history.insert(tk.END, "═" * 80 + "\n", "separator")
chat_history.config(state=tk.DISABLED)

# Add keyboard shortcuts
root.bind('<Control-Return>', lambda event: send_message())
root.bind('<Control-l>', lambda event: load_file())
root.bind('<Control-s>', lambda event: save_response())

# Call mode_changed once at startup to set the correct button appearance
mode_changed()

root.mainloop()
