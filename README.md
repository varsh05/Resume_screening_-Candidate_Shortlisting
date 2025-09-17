An interactive Streamlit web app that processes large JSON form submissions and helps recruiters shortlist the Top 5 finalists for hiring based on skills, experience, and diversity filters.

This project was built as part of a timed hiring challenge. The app enables recruiters to explore, filter, and rank candidates while ensuring fairness, transparency, and diversity in the selection process.



✨ Features

📂 Upload JSON Data: Ingests large-scale form submissions (form_submissions.json).
⚡ Efficient Processing: Handles 50k+ candidate records with optimized scoring and heap-based selection.
🧮 Dynamic Scoring: Weights for skills vs. experience are adjustable via sliders.
🔎 Smart Filters:
  By skills (e.g., Python, ML, AWS, SQL, TensorFlow)
  By location (comma-separated inputs)
  By work type (full-time/part-time)
📊 Candidate Ranking: Generates a final weighted score and explanation for each finalist.
🧑‍🤝‍🧑 Diversity Lens: Highlights underrepresented skill mixes and varied work histories.
📥 Download Finalists: Export top candidates as CSV or JSON.
💡 Explanations: Each finalist is annotated with reasons (skills match, experience years, portfolio availability).
