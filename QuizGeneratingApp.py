import os
import tkinter as tk
from tkinter import ttk, scrolledtext, filedialog, messagebox
import anthropic
import threading
import PyPDF2
import csv
import io
import json
import xml.dom.minidom as md
import zipfile
import uuid
import datetime
import random
import string


class SpanishQuizGenerator:
    def __init__(self, root):
        self.root = root
        self.root.title("Spanish Lesson Quiz Generator")
        self.root.geometry("800x700")
       
        # Replace with your actual API key
        self.api_key = "YOUR_API_KEY_HERE"
       
        # Available languages for the quiz
        self.languages = ["English", "Spanish"]
        
        # Available export formats
        self.formats = ["QTI", "CSV"]
       
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
        self.filename = tk.StringVar(value="spanish_quiz")
        ttk.Entry(output_frame, textvariable=self.filename, width=30).grid(row=0, column=1, padx=5, pady=5)
        
        # Export format selection
        ttk.Label(output_frame, text="Export format:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.export_format = tk.StringVar(value="QTI")
        format_dropdown = ttk.Combobox(output_frame, textvariable=self.export_format, values=self.formats, width=28, state="readonly")
        format_dropdown.grid(row=1, column=1, padx=5, pady=5)
   
        # Language selection
        ttk.Label(output_frame, text="Quiz Language:").grid(row=2, column=0, padx=5, pady=5, sticky="w")
        self.selected_language = tk.StringVar(value="English")
        language_dropdown = ttk.Combobox(output_frame, textvariable=self.selected_language, values=self.languages, width=28, state="readonly")
        language_dropdown.grid(row=2, column=1, padx=5, pady=5)
   
        # Question count configuration
        question_frame = ttk.LabelFrame(main_container, text="Multiple Choice Questions")
        question_frame.pack(fill="x", padx=10, pady=10)
   
        # Multiple Choice count
        ttk.Label(question_frame, text="Number of questions:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.mc_count = tk.IntVar(value=10)
        ttk.Spinbox(question_frame, from_=1, to=50, textvariable=self.mc_count, width=5).grid(row=0, column=1, padx=5, pady=5)
        
        # Quiz title
        ttk.Label(question_frame, text="Quiz title:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.quiz_title = tk.StringVar(value="Spanish Vocabulary Quiz")
        ttk.Entry(question_frame, textvariable=self.quiz_title, width=30).grid(row=1, column=1, padx=5, pady=5, columnspan=2)
   
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
        format_extension = ".zip" if self.export_format.get() == "QTI" else ".csv"
        filepath = filedialog.asksaveasfilename(
            defaultextension=format_extension,
            filetypes=[("QTI files", "*.zip"), ("CSV files", "*.csv"), ("All files", "*.*")],
            initialfile=self.filename.get() + format_extension
        )
        if filepath:
            self.filename.set(os.path.splitext(os.path.basename(filepath))[0])
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
        export_format = self.export_format.get()
       
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
        threading.Thread(target=self._generate_quiz_thread, args=(pdf_path, instructions, language, export_format)).start()
   
    def _generate_quiz_thread(self, pdf_path, instructions, language, export_format):
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
           
            # Handle different export formats
            if export_format == "CSV":
                self.export_csv(quiz_data)
            else:  # QTI
                self.export_qti(quiz_data)
       
        except Exception as e:
            print(f"Error details: {e}")  # Log the error details to the console
            self.root.after(0, lambda: self.status_var.set(f"Error: {str(e)}"))
            messagebox.showerror("Error", str(e))
        finally:
            self.root.after(0, lambda: self.update_progress(False))
    
    def export_csv(self, quiz_data):
        """Export quiz data in CSV format"""
        filepath = os.path.join(self.save_directory, self.filename.get() + ".csv")
        
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
        
        self.root.after(0, lambda: self.status_var.set(f"Quiz saved to {filepath} in CSV format"))
    
    def export_qti(self, quiz_data):
        """Export quiz data in QTI format (as a ZIP file)"""
        # Create a temporary directory to hold the QTI files
        import tempfile
        temp_dir = tempfile.mkdtemp()
        
        try:
            # Create the manifest file
            self.create_qti_manifest(temp_dir)
            
            # Create the quiz XML file
            self.create_qti_quiz(temp_dir, quiz_data)
            
            # Create the ZIP file
            zip_filepath = os.path.join(self.save_directory, self.filename.get() + ".zip")
            with zipfile.ZipFile(zip_filepath, 'w') as zip_file:
                for root, dirs, files in os.walk(temp_dir):
                    for file in files:
                        file_path = os.path.join(root, file)
                        arcname = os.path.relpath(file_path, temp_dir)
                        zip_file.write(file_path, arcname)
            
            self.root.after(0, lambda: self.status_var.set(f"Quiz saved to {zip_filepath} in QTI format"))
            
        except Exception as e:
            raise Exception(f"Failed to create QTI package: {str(e)}")
        finally:
            # Clean up the temporary directory
            import shutil
            shutil.rmtree(temp_dir)
    
    def create_qti_manifest(self, temp_dir):
        """Create the QTI manifest file"""
        manifest_content = """<?xml version="1.0" encoding="UTF-8"?>
    <manifest identifier="man1" xmlns="http://www.imsglobal.org/xsd/imscp_v1p1"
            xmlns:imsmd="http://www.imsglobal.org/xsd/imsmd_v1p2"
            xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
            xsi:schemaLocation="http://www.imsglobal.org/xsd/imscp_v1p1
            http://www.imsglobal.org/xsd/imscp_v1p1.xsd
            http://www.imsglobal.org/xsd/imsmd_v1p2
            http://www.imsglobal.org/xsd/imsmd_v1p2p2.xsd">
    <resources>
        <resource identifier="res1" type="imsqti_xmlv1p2" href="quiz.xml">
        <file href="quiz.xml" />
        </resource>
    </resources>
    </manifest>
    """
        
        # Write manifest to file
        with open(os.path.join(temp_dir, "imsmanifest.xml"), "w", encoding="utf-8") as f:
            f.write(manifest_content)
    
    def create_qti_quiz(self, temp_dir, quiz_data):
        """Create the QTI quiz XML file"""
        quiz_title = self.quiz_title.get() or "Spanish Vocabulary Quiz"
        
        # Start building the XML document
        doc = md.getDOMImplementation().createDocument(None, "questestinterop", None)
        root = doc.documentElement
        root.setAttribute("xmlns", "http://www.imsglobal.org/xsd/ims_qtiasiv1p2")
        root.setAttribute("xmlns:xsi", "http://www.w3.org/2001/XMLSchema-instance")
        
        # Create assessment element
        assessment = doc.createElement("assessment")
        assessment.setAttribute("title", quiz_title)
        root.appendChild(assessment)
        
        # Create section element
        section = doc.createElement("section")
        section.setAttribute("ident", "root_section")
        assessment.appendChild(section)
        
        # Create items for each question
        for i, question in enumerate(quiz_data):
            # Create item element
            item = doc.createElement("item")
            item.setAttribute("title", question.get("question", "")[:50])  # Truncate long titles
            item.setAttribute("ident", f"q{i+1}")
            
            # Create presentation element
            presentation = doc.createElement("presentation")
            item.appendChild(presentation)
            
            # Add question text
            material = doc.createElement("material")
            presentation.appendChild(material)
            
            mattext = doc.createElement("mattext")
            mattext.appendChild(doc.createTextNode(question.get("question", "")))
            material.appendChild(mattext)
            
            # Create response_lid element
            response_lid = doc.createElement("response_lid")
            response_lid.setAttribute("ident", "response1")
            response_lid.setAttribute("rcardinality", "Single")
            presentation.appendChild(response_lid)
            
            # Create render_choice element
            render_choice = doc.createElement("render_choice")
            response_lid.appendChild(render_choice)
            
            # Add answer choices
            for j, answer in enumerate(question.get("answers", [])):
                response_label = doc.createElement("response_label")
                response_label.setAttribute("ident", f"A{j+1}")
                render_choice.appendChild(response_label)
                
                choice_material = doc.createElement("material")
                response_label.appendChild(choice_material)
                
                choice_mattext = doc.createElement("mattext")
                choice_mattext.appendChild(doc.createTextNode(answer))
                choice_material.appendChild(choice_mattext)
            
            # Create resprocessing element
            resprocessing = doc.createElement("resprocessing")
            item.appendChild(resprocessing)
            
            # Create outcomes element
            outcomes = doc.createElement("outcomes")
            resprocessing.appendChild(outcomes)
            
            decvar = doc.createElement("decvar")
            outcomes.appendChild(decvar)
            
            varvalue = doc.createElement("varvalue")
            varvalue.appendChild(doc.createTextNode(str(question.get("points", 1))))
            decvar.appendChild(varvalue)
            
            # Create respcondition element
            respcondition = doc.createElement("respcondition")
            respcondition.setAttribute("title", "correct")
            resprocessing.appendChild(respcondition)
            
            # Create conditionvar element
            conditionvar = doc.createElement("conditionvar")
            respcondition.appendChild(conditionvar)
            
            # Set the correct answer
            varequal = doc.createElement("varequal")
            varequal.setAttribute("respident", "response1")
            varequal.appendChild(doc.createTextNode(f"A{question.get('correctAnswer', 1)}"))
            conditionvar.appendChild(varequal)
            
            # Create setvar element
            setvar = doc.createElement("setvar")
            setvar.setAttribute("action", "Set")
            setvar.appendChild(doc.createTextNode(str(question.get("points", 1))))
            respcondition.appendChild(setvar)
            
            # Add item to section
            section.appendChild(item)
        
        # Write quiz to file
        with open(os.path.join(temp_dir, "quiz.xml"), "w", encoding="utf-8") as f:
            f.write(doc.toprettyxml(indent="  ", encoding="UTF-8").decode("utf-8"))
    


if __name__ == "__main__":
    root = tk.Tk()
    app = SpanishQuizGenerator(root)
    root.mainloop()