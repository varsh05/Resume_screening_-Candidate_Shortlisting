import streamlit as st
import json
import pandas as pd
from dateutil import parser
import itertools
import heapq

st.title("Candidate Shortlisting App (Enhanced & Interactive)")

# --- Upload JSON ---
uploaded_file = st.file_uploader("Upload form_submissions.json", type=["json"])

# Sidebar filters and settings
st.sidebar.header("Filters & Settings")
skill_keywords = ["python", "ml", "aws", "sql", "tensorflow"]
skill_w = st.sidebar.slider("Weight for Skills", 0.0, 1.0, 0.6)
exp_w = st.sidebar.slider("Weight for Experience", 0.0, 1.0, 0.4)
top_n = st.sidebar.number_input("Number of finalists to show", min_value=1, max_value=100, value=5)

filter_skills = st.sidebar.multiselect("Filter by skills", skill_keywords)
filter_locations = st.sidebar.text_input("Filter by location (comma separated)")
filter_work_type = st.sidebar.multiselect("Filter by work availability", ["full-time","part-time"])

def compute_experience_years(work_experiences):
    total_years = 0
    for exp in work_experiences:
        start = exp.get("startDate")
        end = exp.get("endDate")
        try:
            start_year = parser.parse(start).year if start else 0
            end_year = parser.parse(end).year if end else 2025
            total_years += max(0, end_year - start_year)
        except:
            continue
    return total_years

if uploaded_file:
    with st.spinner("Processing submissions..."):
        data = json.load(uploaded_file)

        # Precompute scores
        candidates = []
        max_exp_years = 0
        for c in data:
            skills = [s.lower() for s in c.get("skills", [])]
            skill_score = sum(1 for kw in skill_keywords if kw in skills) / len(skill_keywords)
            exp_years = compute_experience_years(c.get("work_experiences", []))
            max_exp_years = max(max_exp_years, exp_years)
            candidates.append({
                "candidate": c,
                "skill_score": skill_score,
                "exp_years": exp_years
            })

        # Normalize experience scores
        for cand in candidates:
            cand["exp_score"] = cand["exp_years"] / max_exp_years if max_exp_years > 0 else 0

        # Apply filters
        filtered = []
        filter_locations_set = set(loc.strip().lower() for loc in filter_locations.split(",") if loc.strip())
        for cand in candidates:
            c = cand["candidate"]
            if filter_skills and not any(kw in [s.lower() for s in c.get("skills", [])] for kw in filter_skills):
                continue
            if filter_locations_set and c.get("location","").lower() not in filter_locations_set:
                continue
            if filter_work_type and not any(wt in c.get("work_availability", []) for wt in filter_work_type):
                continue
            filtered.append(cand)

        st.sidebar.markdown(f"**Total candidates after filters:** {len(filtered)}")

        # Compute final scores based on slider weights
        total_w = skill_w + exp_w
        w_skill = skill_w / total_w if total_w > 0 else 0.5
        w_exp = exp_w / total_w if total_w > 0 else 0.5
        for cand in filtered:
            cand["final_score"] = w_skill * cand["skill_score"] + w_exp * cand["exp_score"]

        # Use heap for Top N with diversity enforcement
        heap = []
        counter = itertools.count()
        selected_locations = set()
        selected_educations = set()

        for cand in sorted(filtered, key=lambda x: x["final_score"], reverse=True):
            c = cand["candidate"]
            location = c.get("location", "").lower()
            education = c.get("education", {}).get("highest_level", "").lower()

            # Ensure diversity (location + education)
            if location in selected_locations and education in selected_educations and len(heap) < top_n:
                continue

            candidate_dict = c.copy()
            candidate_dict["final_score"] = cand["final_score"]
            candidate_dict["exp_years"] = cand["exp_years"]

            # Explanation
            reasons = []
            if cand["skill_score"] >= 0.5:
                reasons.append("Strong skills match")
            elif cand["skill_score"] > 0.2:
                reasons.append("Moderate skills match")
            else:
                reasons.append("Low skills match")

            if cand["exp_years"] >= 5:
                reasons.append(f"{cand['exp_years']} years of experience")
            elif cand["exp_years"] >= 1:
                reasons.append(f"{cand['exp_years']} years experience")

            if candidate_dict.get("github"):
                reasons.append("GitHub portfolio available")
            if candidate_dict.get("linkedin"):
                reasons.append("LinkedIn profile available")

            candidate_dict["explanation"] = "; ".join(reasons)
            candidate_dict["key_skills"] = ", ".join(c.get("skills", []))

            # Track selected location/education for diversity
            selected_locations.add(location)
            selected_educations.add(education)

            # Heap push
            if len(heap) < top_n:
                heapq.heappush(heap, (cand["final_score"], next(counter), candidate_dict))
            else:
                heapq.heappushpop(heap, (cand["final_score"], next(counter), candidate_dict))

        finalists = [c for _, _, c in sorted(heap, reverse=True)]
        df_finalists = pd.DataFrame(finalists)

        # Show results
        st.subheader(f"Top {top_n} Finalists")
        for i, row in df_finalists.iterrows():
            st.markdown(f"### {row['name']} — Score: {row['final_score']:.2f}")
            st.markdown(f"**Key Skills:** {row['key_skills']}")
            st.markdown(f"**Experience (years):** {row['exp_years']}")
            st.markdown(f"**Portfolio / Profiles:** "
                        f"{'GitHub ' if row.get('github') else ''}"
                        f"{'LinkedIn' if row.get('linkedin') else ''}")
            st.markdown(f"**Why we hired them:** {row['explanation']}")
            st.markdown("---")

        # Download buttons
        st.download_button(
            "Download Finalists (CSV)",
            df_finalists.to_csv(index=False),
            "finalists.csv",
            "text/csv"
        )
        st.download_button(
            "Download Finalists (JSON)",
            df_finalists.to_json(orient="records", indent=2),
            "finalists.json",
            "application/json"
        )

    st.success("Processing complete!")
