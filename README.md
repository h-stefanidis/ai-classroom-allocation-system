# ClassForge: AI-Powered Classroom Allocation System

**ClassForge** is an AI-driven platform designed to optimize classroom allocations by leveraging social network analysis, academic data, and wellbeing metrics. The system aims to enhance student outcomes and foster school cohesion through intelligent grouping strategies.

---

## 🚀 Features

- **AI-Driven Allocation**: Utilizes Graph Neural Networks (GNNs) and Genetic Algorithms to form optimal student groupings.
- **Social Network Analysis**: Incorporates social connections to promote positive peer interactions.
- **User-Friendly Interface**: Built with React and Chakra UI for an intuitive user experience.
- **Data Visualization**: Employs Recharts for insightful visual representations.
- **Robust Backend**: Powered by Flask and Supabase (PostgreSQL) for efficient data handling.

---

## 🛠️ Tech Stack

- **Frontend**: React, Chakra UI, Recharts
- **Backend**: Flask (Python)
- **Machine Learning**: PyTorch, GNNs, Genetic Algorithms
- **Database**: Supabase (hosted PostgreSQL)

---

## 📁 Project Structure

```
ai-classroom-allocation-system/
├── backend/            # Flask API and business logic
├── frontend/           # React application
├── ml/                 # Machine learning models and scripts
├── db/                 # Database schemas and seed data (if applicable)
├── requirements.txt    # Python dependencies
├── package.json        # Node.js dependencies
├── run.sh / run.bat    # (Optional) Scripts to run the application
├── setup.sh            # Setup script for Unix-based systems
└── README.md           # Project documentation
```

---

## 🧑‍💻 Prerequisites

Ensure the following are installed on your system:

- **Python** (version 3.8 or higher)
- **Node.js** and **npm**

> ✅ **Note:** We use [Supabase](https://supabase.com/) for our database which is an online PostgreSQL platform — no local installation required.

---

## ⚙️ Setup Instructions

### 1. Clone the Repository

```bash
git clone https://github.com/h-stefanidis/ai-classroom-allocation-system.git
cd ai-classroom-allocation-system
```

### 2. Backend Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r ../requirements.txt
```

### 3. Frontend Setup

```bash
cd ../frontend
npm install
```

### 4. Environment Configuration

Make sure your environment variables for Supabase (e.g., URL, API key) are set up in a `.env` file inside the `backend` folder. You will be provided this file or the necessary values by the development team.

### 5. Run the Application

- **Backend**:

  ```bash
  cd backend
  python run.py
  ```

- **Frontend**:

  ```bash
  cd frontend
  npm start
  ```

> 🔄 Make sure you are in the correct directory (`frontend/` or `backend/`) before running the respective commands.

The application will be accessible at `http://localhost:3000`.

---

## 🧪 Testing

To run the test suite:

```bash
cd backend
pytest
```

---

## 📄 License

This project is licensed under the MIT License. See the [LICENSE](https://github.com/h-stefanidis/ai-classroom-allocation-system/blob/main/LICENSE) file for details.

---

## 📬 Contact

For any questions or support, please open an issue on the [GitHub repository](https://github.com/h-stefanidis/ai-classroom-allocation-system/issues).
