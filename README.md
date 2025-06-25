# CVAlign: AI-Powered Resume Evaluation

CVAlign is an AI-driven resume evaluation tool that assesses candidate CVs against job descriptions using Retrieval-Augmented Generation (RAG) and generative LLMs. It provides personalized feedback and a score based on the alignment between a candidate's resume and the job role.

---

## 🚀 Features

* 📄 Upload resumes in PDF or DOCX formats
* 📌 Upload a job description to compare against
* 🤖 RAG-based LLM analysis to generate evaluation and feedback
* 📝 Score breakdown on key alignment factors
* 🌐 User-friendly React frontend

---

## 📁 Project Structure

```
cv-align/
├── backend/                # Flask backend for file processing and model inference
│   ├── app.py              
│   ├── ml_logic/           # Custom ML logic for parsing, RAG, scoring
│   └── requirements.txt
├── frontend/               # React-based frontend using Vite + Tailwind + shadcn
│   ├── src/
│   └── package.json
├── README.md               # Project README (you're here)
```

---

## 🧰 Tech Stack

* **Frontend**: React, TailwindCSS, shadcn/ui, Vite
* **Backend**: Python (Flask), LangChain, FAISS, PyMuPDF, python-docx
* **Model**: LLM (via Ollama or OpenAI), RAG architecture

---

## 📦 Setup Instructions

### 🔧 Backend

1. Navigate to the backend folder:

   ```bash
   cd backend
   ```

2. (Optional) Create a virtual environment:

   ```bash
   python -m venv venv
   source venv/bin/activate
   ```

3. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

4. Run the backend:

   ```bash
   python app.py
   ```

---

### 🌐 Frontend

1. Navigate to the frontend folder:

   ```bash
   cd frontend
   ```

2. Install dependencies:

   ```bash
   npm install
   ```

3. Start the development server:

   ```bash
   npm run dev
   ```

---

## 🧪 Running the App

Once both frontend and backend are running:

* Open [http://localhost:5173](http://localhost:5173) to access the UI
* Upload a resume and job description
* View the alignment score and AI-generated feedback

---

## 📄 License

MIT License. See `LICENSE` file for details.

---

## 🤝 Contributing

Pull requests are welcome! For major changes, please open an issue first to discuss what you would like to change.

---

## ✨ Credits

Created by [Yavanash Sarma](https://github.com/Yavanash) as part of a personal AI project.
