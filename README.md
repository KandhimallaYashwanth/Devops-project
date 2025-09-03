# 🌱 Farm Link

## 📌 Project Overview
**Farm Link** is a web application designed to connect **farmers** and **buyers** directly.  
It helps farmers showcase their produce online and enables buyers to browse available produce or post their requirements.  
Both farmers and buyers can **chat directly**, reducing the role of middlemen and making transactions more transparent.

---

## ✨ Features

### 👨‍🌾 Farmers
- Post details about their produce (name, price, quantity, availability).
- Manage posts (edit, delete, schedule availability).
- View buyer requirements.
- Chat with buyers.
- Manage their profile.

### 🛒 Buyers
- Browse farmer posts.
- Post their own requirements.
- Chat with farmers.
- Manage their profile.

---

## 🛠 Tech Stack
- **Frontend:** HTML, CSS, JavaScript  
- **Backend:** Python (Flask)  
- **Database:** Supabase
- **Authentication:** JWT (JSON Web Tokens)  
- **Deployment:** Netlify (frontend), Render (backend + DB)  


## Continuous Integration (CI)
This project uses **GitHub Actions** to automatically run tests and checks on every push or pull request to the `main` branch.

### Workflow
- **Trigger:** On push or pull request to `main`
- **Steps:**
  1. Checkout the code
  2. Set up Python environment
  3. Install dependencies (`pip install -r backend/requirements.txt`)
  4. Run linting and tests
  5. Optional: Build or deploy steps can be added
