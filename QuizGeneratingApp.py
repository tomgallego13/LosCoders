import os
import tkinter as tk
from tkinter import ttk, scrolledtext, filedialog, messagebox
import anthropic
import threading
import PyPDF2
import csv
import io


class SpanishQuizGenerator:
    def __init__(self, root):
        self.root = root
        self.root.title("Spanish Lesson Quiz Generator")
        self.root.geometry("800x700")
       
        # Hardcoded API key - replace with your actual API key
        self.api_key = "YOUR_API_KEY_HERE"
       
        # Available languages for the quiz
        self.languages = ["Spanish", "English"]
       
        self.setup_ui()
   
    def setup_ui(self):
        # Create a scrollable canvas
        canvas = tk.Canvas(self.root)
        scrollbar = ttk.Scrollbar(self.root, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
   
        # Configure the canvas and scrollbar
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
       
        # Pack the canvas and scrollbar
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
   
        # Main container inside the scrollable frame
        main_container = ttk.Frame(scrollable_frame)
        main_container.pack(fill="both", expand=True, padx=10, pady=10)
   
        # PDF Selection
        pdf_frame = ttk.LabelFrame(main_container, text="PDF Selection")
        pdf_frame.pack(fill="x", padx=10, pady=10)
   
        self.pdf_path = tk.StringVar()
        ttk.Label(pdf_frame, text="Selected PDF:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        ttk.Entry(pdf_frame, textvariable=self.pdf_path, width=60, state="readonly").grid(row=0, column=1, padx=5, pady=5)
        ttk.Button(pdf_frame, text="Browse...", command=self.select_pdf).grid(row=0, column=2, padx=5, pady=5)
   
        # PDF Preview
        preview_frame = ttk.LabelFrame(main_container, text="PDF Preview (First 500 characters)")
        preview_frame.pack(fill="both", expand=True, padx=10, pady=10)
   
        self.preview_text = scrolledtext.ScrolledText(preview_frame, height=10, wrap=tk.WORD)
        self.preview_text.pack(fill="both", expand=True, padx=5, pady=5)
   
        # Output Settings
        output_frame = ttk.LabelFrame(main_container, text="Output Settings")
        output_frame.pack(fill="x", padx=10, pady=10)
   
        ttk.Label(output_frame, text="Output filename:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.filename = tk.StringVar(value="spanish_quiz.csv")
        ttk.Entry(output_frame, textvariable=self.filename, width=30).grid(row=0, column=1, padx=5, pady=5)
   
        # Language selection
        ttk.Label(output_frame, text="Quiz Language:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.selected_language = tk.StringVar(value="Spanish")
        language_dropdown = ttk.Combobox(output_frame, textvariable=self.selected_language, values=self.languages, width=28, state="readonly")
        language_dropdown.grid(row=1, column=1, padx=5, pady=5)
   
        # Question count configuration
        question_frame = ttk.LabelFrame(main_container, text="Multiple Choice Questions")
        question_frame.pack(fill="x", padx=10, pady=10)
   
        # Multiple Choice count
        ttk.Label(question_frame, text="Number of questions:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.mc_count = tk.IntVar(value=10)
        ttk.Spinbox(question_frame, from_=1, to=20, textvariable=self.mc_count, width=5).grid(row=0, column=1, padx=5, pady=5)
   
        # Controls
        controls_frame = ttk.Frame(main_container)
        controls_frame.pack(fill="x", padx=10, pady=10)
   
        self.status_var = tk.StringVar(value="Ready")
        ttk.Label(controls_frame, textvariable=self.status_var).pack(side="left", padx=5)
   
        # Progress bar
        self.progress_var = tk.DoubleVar(value=0)
        self.progress_bar = ttk.Progressbar(controls_frame, variable=self.progress_var, length=200, mode="indeterminate")
       
        ttk.Button(controls_frame, text="Generate Quiz", command=self.generate_quiz).pack(side="right", padx=5)
        ttk.Button(controls_frame, text="Save Location", command=self.select_save_location).pack(side="right", padx=5)
   
    def select_pdf(self):
        filepath = filedialog.askopenfilename(
            filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")]
        )
        if filepath:
            self.pdf_path.set(filepath)
            self.display_pdf_preview(filepath)
   
    def display_pdf_preview(self, filepath):
        try:
            with open(filepath, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                text = ""
                for page_num in range(min(2, len(pdf_reader.pages))):
                    page = pdf_reader.pages[page_num]
                    text += page.extract_text()
               
                # Display first 500 characters as preview
                preview = text[:500] + "..." if len(text) > 500 else text
                self.preview_text.delete("1.0", tk.END)
                self.preview_text.insert(tk.END, preview)
        except Exception as e:
            self.preview_text.delete("1.0", tk.END)
            self.preview_text.insert(tk.END, f"Error previewing PDF: {e}")
   
    def select_save_location(self):
        filepath = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            initialfile=self.filename.get()
        )
        if filepath:
            self.filename.set(os.path.basename(filepath))
            self.save_directory = os.path.dirname(filepath)
   
    def extract_pdf_text(self, filepath):
        try:
            with open(filepath, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                text = ""
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
                return text
        except Exception as e:
            raise Exception(f"Error extracting PDF text: {e}")
   
    def update_progress(self, state):
        if state:
            self.progress_bar.pack(side="left", padx=10)
            self.progress_bar.start(10)
        else:
            self.progress_bar.stop()
            self.progress_bar.pack_forget()
   
    def generate_quiz(self):
        if not hasattr(self, 'save_directory'):
            self.save_directory = os.getcwd()
       
        pdf_path = self.pdf_path.get()
        if not pdf_path or not os.path.exists(pdf_path):
            self.status_var.set("Error: Please select a valid PDF file")
            return
       
        # Get the number of multiple choice questions and selected language
        mc_count = self.mc_count.get()
        language = self.selected_language.get()
       
        # Instructions for multiple choice questions only, with language specification
        instructions = f"""
        Create a quiz based on the Spanish lesson PDF I've uploaded.
        Generate {mc_count} multiple choice questions with 4 options each.
       
        IMPORTANT: Write only the question text in {language}. Keep all the answers in Spanish.
       
        Return the quiz in this JSON format:
        [
            {{
                "type": "MC",
                "question": "Question text in {language}",
                "answers": ["Spanish answer 1", "Spanish answer 2", "Spanish answer 3", "Spanish answer 4"],
                "correctAnswer": 1,
                "points": 1
            }},
            // more questions...
        ]
       
        Make sure each question tests understanding of the material from the PDF.
        Number correctAnswer from 1 to 4, indicating which answer is correct.
        """
       
        self.status_var.set("Extracting PDF text...")
        self.update_progress(True)
       
        # Start in a thread to keep UI responsive
        threading.Thread(target=self._generate_quiz_thread, args=(pdf_path, instructions, language)).start()
   
    def _generate_quiz_thread(self, pdf_path, instructions, language):
        try:
            # Extract PDF text
            self.root.after(0, lambda: self.status_var.set("Extracting PDF text..."))
            pdf_text = self.extract_pdf_text(pdf_path)
           
            # Initialize API client
            client = anthropic.Client(api_key=self.api_key)
           
            self.root.after(0, lambda: self.status_var.set(f"Generating quiz questions in {language}..."))
           
            # Send request to Claude
            message = client.messages.create(
                model="claude-3-7-sonnet-20250219",
                max_tokens=4000,
                system=f"You are an assistant specialized in creating educational materials for Spanish language teachers. Your task is to generate multiple choice quiz questions where the questions are in {language} but all answer options remain in Spanish. Return the quiz data in JSON format.",
                messages=[
                    {
                        "role": "user",
                        "content": f"{instructions}\n\nHere is the Spanish lesson content:\n\n{pdf_text}"
                    }
                ]
            )
           
            # Extract JSON content
            response_text = message.content[0].text.strip()
           
            # Extract JSON from response if needed
            import json
            import re
           
            # Find JSON array in the response
            json_match = re.search(r'\[\s*\{.*\}\s*\]', response_text, re.DOTALL)
            if json_match:
                json_data = json_match.group(0)
            else:
                # If JSON array not found, try to clean up the text
                # Remove any markdown code block formatting
                if response_text.startswith("```") and response_text.endswith("```"):
                    lines = response_text.split("\n")
                    if len(lines) > 2:
                        response_text = "\n".join(lines[1:-1])
                json_data = response_text
           
            # Parse JSON data
            try:
                quiz_data = json.loads(json_data)
            except json.JSONDecodeError as e:
                raise Exception(f"Failed to parse quiz data: {str(e)}")
           
            # Convert JSON to CSV using CSV module for proper escaping
            filepath = os.path.join(self.save_directory, self.filename.get())
           
            with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
                # Create CSV writer
                csv_writer = csv.writer(csvfile, quoting=csv.QUOTE_ALL)
               
                # Write header
                csv_writer.writerow(["Type", "Question", "Answer1", "Answer2", "Answer3", "Answer4", "Correct Answer", "Points"])
               
                # Write quiz questions
                for question in quiz_data:
                    row = [
                        question["type"],
                        question["question"],
                        question["answers"][0],
                        question["answers"][1],
                        question["answers"][2],
                        question["answers"][3],
                        question["correctAnswer"],
                        question["points"]
                    ]
                    csv_writer.writerow(row)
           
            self.root.after(0, lambda: self.status_var.set(f"Quiz in {language} saved to {filepath}"))
       
        except Exception as e:
            print(f"Error details: {e}")  # Log the error details to the console
            self.root.after(0, lambda: self.status_var.set(f"Error: {str(e)}"))
            messagebox.showerror("Error", str(e))
        finally:
            self.root.after(0, lambda: self.update_progress(False))




if __name__ == "__main__":
    root = tk.Tk()
    app = SpanishQuizGenerator(root)
    root.mainloop()

