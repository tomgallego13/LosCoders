# Los Coders - Technical Documentation


### Team - Los Coders:
- **Thomas Gallego**
- **Nadzumie Flores**
- **Maxwell Lindbergh**
- **Samuel Clark**
- **Diego Gomez**

### Course - CIS4914 Senior Project
### Advisor - Dr. Marull, cmarull@ufl.edu
### Presentation link: 

## Keywords:

## 1. Project Overview
This project aims to develop a tool that converts AI-generated test banks into Canvas quizzes or Respondus-compatible spreadsheets. The tool automates quiz formatting, reducing manual effort for educators. It leverages Python for data processing, Pandas for structuring content, and integrates with the Canvas API for seamless quiz uploads.

## 2. System Architecture
### Components:
- **Backend (Python & Pandas)**: Handles file parsing, data structuring, and conversion.
- **Frontend (React)**: Web-based interface for file uploads and format selection.
- **Canvas API Integration**: Enables direct upload of quiz data.
- **Respondus-compatible Spreadsheet Export**: Ensures generated files can be imported into Respondus.

## 3. Technology Stack
- **Backend**: Python, Pandas
- **Frontend**: React, Tailwind CSS
- **API Integration**: Canvas API
- **File Formats Supported**: TXT, DOCX, PDF

## 4. Functional Requirements
- Upload AI-generated test bank files.
- Parse and structure question data.
- Convert data into Canvas quiz format or Respondus-compatible spreadsheet.
- Provide web-based UI for user interaction.
- Support multiple question types (MCQ, True/False, etc.).
- Allow direct upload to Canvas.

## 5. API Integration Details
### Canvas API:

### Respondus Spreadsheet Format:
- **Required Columns**: Question Type, Question Text, Answer Choices, Correct Answer
- **File Type**: CSV or XLSX

## 6. Data Flow & Processing
1. **File Upload** (Frontend → Backend)
2. **Parsing & Structuring** (Backend using Pandas)
3. **Conversion to Target Format** (Canvas Quiz JSON / Respondus CSV)
4. **Download or Direct Upload to Canvas**

## 7. Web Interface Design
- **File Upload Section**: Drag-and-drop support.
- **Output Settings**: Format selection, question type options.
- **Conversion & Download Button**: Trigger file processing.

## 8. Testing & Validation
- **Unit Testing**: Python scripts for parsing and conversion.
- **Integration Testing**: API calls to Canvas.
- **User Testing**: Uploading real test banks and verifying results.


## 9. User Guide


## 10. Future Enhancements


---
This documentation provides a structured overview of the project and guides future development and deployment efforts.
