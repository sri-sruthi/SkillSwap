
# SkillSwap: Democratizing Knowledge Exchange

**AI-powered peer learning platform for skill exchange**

Empowering communities to learn and teach together—AI matches skills, breaks barriers, and transforms education from a privilege into a shared, accessible right.

---

## Table of Contents

- [Setup and Running the Project](#setup-and-running-the-project)
- [Problem Statement](#problem-statement)
- [Solution Overview](#solution-overview)
- [AI Integration](#ai-integration)
- [Technology Stack](#technology-stack)
- [How to Use](#how-to-use)
- [Future Enhancements](#future-enhancements)

---

## Setup and Running the Project

### Prerequisites

- Python 3.8 or higher
- Node.js 16 or higher
- npm or yarn

### Backend Setup

1. Navigate to the backend directory:

```bash
cd backend
```

2. Install all dependencies:

```bash
pip install -r requirements.txt
```

3. Run the backend server:

```bash
python app.py
```

The backend will run at: `http://127.0.0.1:5000`

### Frontend Setup

1. Navigate to the frontend directory:

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

The frontend will run at: `http://localhost:5173/`

---

## Problem Statement

Students and professionals often want to learn new skills but struggle to find peers or mentors who can teach them effectively. Simultaneously, individuals with valuable expertise lack structured, accessible platforms to share their knowledge. This creates educational barriers and limits collaborative growth within communities, particularly for underserved populations who cannot afford traditional tutoring or courses.

---

## Solution Overview

SkillSwap is a full-stack web application that democratizes education by intelligently connecting learners and teachers based on complementary skill sets. The platform enables users to:

- Register their skills and learning goals
- Discover AI-matched learning partners within their community
- Track collaborative learning sessions
- Receive AI-generated summaries of their progress
- Visualize learning trends and achievements

By leveraging artificial intelligence for semantic skill matching and automatic progress summarization, SkillSwap makes peer learning more efficient, personalized, and accessible to all.

---

## AI Integration

### AI-Enhanced Skill Matching

SkillSwap employs a hybrid artificial intelligence approach to generate accurate, meaningful learning connections:

**Semantic Similarity Analysis**

- Utilizes TF-IDF vectorization and cosine similarity to identify related skills across different terminology
- Understands contextual relationships (e.g., recognizes that "Data Science" relates to "Machine Learning" and "Statistics")
- Enables flexible matching even when users describe skills differently

**Logical Overlap Matching**

- Ensures practical relevance by comparing skills a user wants to learn against skills another user can teach
- Validates bidirectional compatibility for mutual learning opportunities
- Filters matches based on complementary skill gaps and expertise

**Weighted Scoring System**

- Combines semantic and logical metrics using tunable weights
- Produces ranked recommendations that balance technical similarity with practical teaching capability
- Optimizes match quality through configurable parameters

### AI-Based Session Summarization

When users document their learning sessions, SkillSwap automatically generates concise summaries using the T5-small transformer model from Hugging Face. This feature:

- Extracts core concepts and key takeaways from session notes
- Produces consistent, readable summaries for progress tracking
- Enables better reflection and knowledge retention
- Reduces cognitive load by distilling lengthy notes into actionable insights

**Technical Implementation:**

- Model: `t5-small` (text-to-text transfer transformer)
- Libraries: `transformers`, `torch`, `sentencepiece`
- Processing: Real-time summarization with optimized inference

---

## Technology Stack

| Layer              | Technologies                                                                            |
| ------------------ | --------------------------------------------------------------------------------------- |
| **Frontend** | React.js (Vite), Framer Motion                                                          |
| **Backend**  | Flask (Python), SQLite                                                                  |
| **AI/NLP**   | Scikit-learn (TF-IDF, Cosine Similarity), Hugging Face Transformers (T5-small), PyTorch |
| **Styling**  | Plain CSS with modern responsive design                                                 |
| **Database** | SQLite (`skillswap.db`)                                                               |

---

## How to Use

1. **Add a User**: Enter name, location, skills you can teach, and skills you want to learn
2. **Select Profile**: Choose your user profile from the dropdown menu
3. **Get Matches**: Click to view AI-ranked peer recommendations based on skill compatibility
4. **Log Sessions**: Record learning session details including what was taught and learned
5. **View Summaries**: Receive AI-generated summaries of your session notes automatically
6. **Track Progress**: Visualize your top taught and learned skills through interactive dashboards

---

## Team

- Sri Sruthi Manikka Nagasamy
- Krishna Midula Karnan

---

## Future Enhancements

- **Cloud Deployment**: Host backend on Render and frontend on Netlify for public accessibility
- **Advanced AI Features**: Integrate fine-tuned language models for personalized learning path recommendations
- **Real-Time Communication**: Add chat-based tutoring assistance for live collaboration
- **Gamification**: Introduce achievement badges, learning streaks, and community leaderboards
- **Mobile Application**: Develop native iOS and Android apps for on-the-go learning
- **Expanded Analytics**: Provide deeper insights into learning patterns and skill acquisition rates

---

## License

This project is licensed under the MIT License.

---

**Built with the vision of making quality education accessible to everyone, everywhere.**
