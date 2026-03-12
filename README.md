# 🤖 ICA Workflow Chat with File Upload

A **Streamlit-based chat application** that connects to an **IBM Agent Studio / ICA Langflow workflow**.
The app allows users to:

* Chat with an AI workflow
* Upload files (PDF, images, Excel, Word, CSV, text)
* Send file content along with user queries to the workflow
* Maintain chat history per session

This project demonstrates how to build a **simple AI assistant UI for IBM Agent Studio workflows**.

---

# 🚀 Features

* 💬 Chat interface using Streamlit
* 📂 Multiple file upload support
* 📄 Document parsing for:

  * PDF
  * CSV
  * Excel
  * Word documents
  * Text / logs
* 🖼 Image preview
* 🔐 API authentication using `.env`
* 🧠 Session-based chat memory
* 🔎 Debug response viewer

---

# 📁 Project Structure

```
IBMStudio/
│
├── app.py                # Main Streamlit application
├── chatwithupload.py     # Chat + file upload workflow UI
├── requirements.txt      # Python dependencies
├── .env                  # API configuration (not committed)
└── venv/                 # Python virtual environment
```

---

# ⚙️ Requirements

* Python **3.9+**
* Streamlit
* IBM Agent Studio / ICA workflow
* API Key for the workflow

---

# 🔧 Installation

### 1️⃣ Clone the repository

```bash
git clone <your-repo-url>
cd IBMStudio
```

---

### 2️⃣ Create a virtual environment

```bash
python3 -m venv venv
```

Activate it:

**Mac / Linux**

```bash
source venv/bin/activate
```

**Windows**

```bash
venv\Scripts\activate
```

---

### 3️⃣ Install dependencies

```bash
pip install -r requirements.txt
```

---

# 🔑 Environment Configuration

Create a `.env` file in the project root.

```
IBM_AGENT_STUDIO_API_KEY=your_api_key_here
WORKFLOW_ID=your_workflow_id_here
```

Example:

```
IBM_AGENT_STUDIO_API_KEY=abcd1234xyz
WORKFLOW_ID=8e635116-b18e-**********************
```

---

# ▶️ Running the Application

Start the Streamlit server:

```bash
streamlit run app.py
```

The app will open in your browser:

```
http://localhost:8501
```

---

# 📂 Supported File Types

You can upload multiple files including:

| File Type | Supported       |
| --------- | --------------- |
| Text      | .txt .md .log   |
| Data      | .csv .xlsx      |
| Documents | .pdf .docx      |
| Images    | .png .jpg .jpeg |

Uploaded files are parsed and their content is included in the prompt sent to the workflow.

---

# 💬 Example Usage

1. Upload a file (e.g., `sales.csv`)
2. Ask a question:

```
What insights can you find in the uploaded data?
```

The file content and question are sent to the workflow.

---

# 🛠 Dependencies

```
streamlit
requests
python-dotenv
pandas
PyPDF2
python-docx
openpyxl
```

---

# 🧪 Troubleshooting

### Module not found errors

Install missing packages:

```bash
pip install -r requirements.txt
```

---

### API Key not detected

Ensure `.env` exists and contains:

```
IBM_AGENT_STUDIO_API_KEY=your_key
WORKFLOW_ID=your_workflow_id
```

---

### Streamlit command not found

Install Streamlit:

```bash
pip install streamlit
```

---

# 📌 Notes

* Large files are truncated before sending to the workflow to avoid token limits.
* Images are displayed but not parsed into text.

---

# 📄 License

This project is intended for **demonstration and internal use with IBM Agent Studio workflows**.
