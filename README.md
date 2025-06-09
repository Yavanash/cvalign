# 🧠 CV Evaluator – AI-Powered Resume Scoring with RAG

CV Evaluator is an AI-powered web application that evaluates resumes against job descriptions using a Retrieval-Augmented Generation (RAG) model. It extracts and processes content from uploaded PDF/DOCX CVs and provides relevance scores and detailed feedback using LLMs.

---

## 🚀 Features

* Upload resumes in PDF or DOCX format
* Upload job descriptions for targeted evaluation
* Backend scoring with LLM (via Python)
* File parsing and handling via Go server
* Fast and simple frontend UI for interaction
* Retrieval-Augmented Generation (RAG) architecture using FAISS & LangChain

---

## 🧱️ Project Structure

```
cv-evaluator/
│
├── backend/                  # Go server for file uploads
│   ├── uploads/              # Folder to store uploaded files (create manually)
│   ├── main.go               # Go server code
│   └── Dockerfile            # Container setup for backend
│
├── ml/                       # Python LLM server
│   └── mock.py               # FastAPI (or Flask) server to run ML scoring logic
│
├── frontend/                 # Static frontend
│   └── index.html            # Frontend UI
│
└── README.md
```

---

## ⚙️ How to Run the Project

> ✅ **Make sure to manually create a folder at** `backend/uploads` **if you're running locally. Docker will handle it inside the container if not.**

### 🟩 Start the Go Backend Server (PORT `8080`)

```bash
cd backend
docker build -t backend-app .
docker run -p 8080:8080 backend-app
```

### 🐍 Start the Python ML Scoring Server (PORT `8000`)

```bash
cd ml
python mock.py
```

### 🌐 Start the Frontend (PORT `5500`)

```bash
cd frontend
npx serve -p 5500
```

> ⚠️ The `npx serve` command is used instead of Live Server in VS Code to prevent automatic page reloads on every POST request.

---

## 🧠 Technologies Used

* **LangChain + FAISS** for RAG-based LLM response generation
* **Python + FastAPI** for scoring and feedback
* **Go** for handling file uploads and server-side routing
* **Docker** for backend containerization
* **HTML + JS (Static Site)** for frontend
* **Pydantic** for response modeling

---

## 📂 Sample Inputs

* **CVs**: Upload PDF or DOCX files
* **Job Descriptions**: Paste or upload the JD for evaluation context

---

## 📌 Future Enhancements

* Integrate OAuth for user login
* Track CV evaluation history
* Use production-grade LLM endpoints

---

## 📄 License

This project is licensed under the MIT License.

---

## 🤝 Contributions

Feel free to open issues or submit pull requests! Any contributions to improve the scoring logic, UI, or documentation are welcome.
