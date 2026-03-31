# ⚖️ Fairness Tracker

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Django](https://img.shields.io/badge/Django-4.2+-092e20.svg?logo=django&logoColor=white)](https://www.djangoproject.com/)
[![React](https://img.shields.io/badge/React-18-61dafb.svg?logo=react&logoColor=black)](https://reactjs.org/)
[![WebSockets](https://img.shields.io/badge/Real--time-WebSocket-000000.svg?logo=socket.io&logoColor=white)](https://channels.readthedocs.io/en/latest/)

Fairness Tracker is a modern project management and peer-to-peer accountability system designed to ensure every team member's contribution is measured and verified fairly. It bridges the gap between individual effort and team success through a transparent, verified contribution logging system.

## 🚀 Key Features

*   **👥 Advanced Team Management**: Create or join teams using unique 6-digit codes.
*   **✅ Verified Contributions**: Students log work hours with mandatory **Proof Uploads** (PDFs, Images, Documents).
*   **🗳️ Peer-to-Peer Verification**: Contributions undergo peer review for accountability before final lead approval.
*   **💬 Real-Time Collaboration**: Integrated team chat powered by WebSockets (Django Channels/Daphne).
*   **🔔 Automated Notification System**: Instant alerts for task assignments, verification updates, and disputes.
*   **📊 Insightful Analytics**: Track progress and contribution balance across projects and members.
*   **🔐 Secure Verification**: Role-based access control with mandatory **Instructor Email Verification**.

---

## 🛠️ Technology Stack

| Layer | Technology |
| :--- | :--- |
| **Frontend** | React, Vite, Tailwind CSS, Lucide Icons, Framer Motion |
| **Backend** | Django 4.2+, Django REST Framework (DRF) |
| **Real-time** | Django Channels, Daphne, WebSockets |
| **Database** | PostgreSQL (Production), SQLite (Development) |
| **Auth** | JWT (SimpleJWT), Custom RBAC |

---

## 🏁 Getting Started

### 📦 Backend Setup
1.  **Clone the repository**:
    ```bash
    git clone https://github.com/yourusername/fairness-tracker.git
    cd fairness-tracker
    ```
2.  **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    ```
3.  **Run migrations**:
    ```bash
    python manage.py migrate
    ```
4.  **Start the development server**:
    ```bash
    # Use Daphne for WebSockets
    daphne -b 0.0.0.0 -p 8000 fairness_tracker.asgi:application
    ```

### 💻 Frontend Setup
1.  **Navigate to the frontend directory**:
    ```bash
    cd frontend
    ```
2.  **Install dependencies**:
    ```bash
    npm install
    ```
3.  **Start the dev server**:
    ```bash
    npm run dev
    ```

---

## 📂 Project Structure

```text
├── accounts/          # User authentication and RBAC
├── contributions/     # Verification and work logging logic
├── tasks/             # Project task management
├── teams/             # Team and membership handling
├── chat/              # WebSocket-based real-time chat
├── notifications/      # Signal-based alerting system
└── frontend/          # React Vite application
```

---

## 🔒 Environment Variables

Create a `.env` file in the root directory:
```env
DEBUG=True
SECRET_KEY=your_secret_key_here
DATABASE_URL=sqlite:///db.sqlite3
# Production Redis (for Chat)
# REDIS_URL=redis://localhost:6379
```

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1.  Fork the Project
2.  Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3.  Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4.  Push to the Branch (`git push origin feature/AmazingFeature`)
5.  Open a Pull Request

---

## 📄 License

Distributed under the MIT License. See `LICENSE` for more information.

---
**Fairness Tracker** — *Measure effort fairly, build teams stronger.*
