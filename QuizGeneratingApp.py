import os
import tkinter as tk
from tkinter import ttk, scrolledtext, filedialog, messagebox
import anthropic
import threading
import PyPDF2

#edit
class SpanishQuizGenerator:
    def __init__(self, root):
        self.root = root
        self.root.title("Spanish Lesson Quiz Generator")
        self.root.geometry("800x700")
       
        # Hardcoded API key - replace with your actual API key
        self.api_key = "YOUR_API_KEY_HERE"
       
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
   
    def generate_quiz(self):
        if not hasattr(self, 'save_directory'):
            self.save_directory = os.getcwd()
       
        pdf_path = self.pdf_path.get()
        if not pdf_path or not os.path.exists(pdf_path):
            self.status_var.set("Error: Please select a valid PDF file")
            return
       
        # Get the number of multiple choice questions
        mc_count = self.mc_count.get()
       
        # Instructions for multiple choice questions only
        instructions = f"""
        Create a quiz based on the Spanish lesson PDF I've uploaded.
        Generate {mc_count} multiple choice questions with 4 options each.
       
        IMPORTANT FORMATTING INSTRUCTIONS:
        Return ONLY raw CSV data with these column headers:
        Type,Question,Answer1,Answer2,Answer3,Answer4,Correct Answer,Points
       
        For each question:
           - Type: "MC" (for Multiple Choice)
           - Question: The full question text
           - Answer1-4: Four possible answers
           - Correct Answer: The number (1, 2, 3, or 4) of the correct option
           - Points: Always "1"
       
        Do not include any markdown formatting, explanations, or additional text - ONLY the CSV data.
        """
       
        self.status_var.set("Extracting PDF text...")
       
        # Start in a thread to keep UI responsive
        threading.Thread(target=self._generate_quiz_thread, args=(pdf_path, instructions)).start()
   
    def _generate_quiz_thread(self, pdf_path, instructions):
        try:
            # Extract PDF text
            self.root.after(0, lambda: self.status_var.set("Extracting PDF text..."))
            pdf_text = self.extract_pdf_text(pdf_path)
           
            # Initialize API client
            client = anthropic.Client(api_key=self.api_key)
           
            self.root.after(0, lambda: self.status_var.set("Generating quiz questions..."))
           
            # Send request to Claude
            message = client.messages.create(
                model="claude-3-7-sonnet-20250219",
                max_tokens=4000,
                system="You are an assistant specialized in creating educational materials for Spanish language teachers. Your task is to generate multiple choice quiz questions in CSV format based on Spanish lesson content.",
                messages=[
                    {
                        "role": "user",
                        "content": f"{instructions}\n\nHere is the Spanish lesson content:\n\n{pdf_text}"
                    }
                ]
            )
           
            # Extract CSV content
            csv_content = message.content[0].text.strip()
           
            # Clean up any potential markdown formatting if Claude adds it
            if csv_content.startswith("```") and csv_content.endswith("```"):
                csv_content = csv_content[csv_content.find("\n")+1:csv_content.rfind("\n")]
            elif csv_content.startswith("```csv") and csv_content.endswith("```"):
                csv_content = csv_content[csv_content.find("\n")+1:csv_content.rfind("\n")]
           
            # Make sure the first line is the header
            if not csv_content.startswith("Type,Question"):
                csv_content = "Type,Question,Answer1,Answer2,Answer3,Answer4,Correct Answer,Points\n" + csv_content
           
            # Save to file
            filepath = os.path.join(self.save_directory, self.filename.get())
            with open(filepath, 'w', newline='', encoding='utf-8') as file:
                file.write(csv_content)
           
            self.root.after(0, lambda: self.status_var.set(f"Quiz saved to {filepath}"))
       
        except Exception as e:
            print(f"Error details: {e}")  # Log the error details to the console
            self.root.after(0, lambda: self.status_var.set(f"Error: {str(e)}"))
            messagebox.showerror("Error", str(e))


if __name__ == "__main__":
    root = tk.Tk()
    app = SpanishQuizGenerator(root)
    root.mainloop()