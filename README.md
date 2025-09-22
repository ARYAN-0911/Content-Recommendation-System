# 🎬 WhyWatch — Smart Movie Recommender

**WhyWatch** is a simple, explainable movie recommender built with **Streamlit**.  
Given a movie title, the app returns similar movies and provides short, human-readable explanations for each recommendation (shared genres, director, cast overlap, short plot snippet). Poster images and metadata are fetched from The Movie Database (TMDB) API.

---

## Demo
A local Streamlit UI where you can search or pick a movie, then click **Recommend** to see suggestions with posters and explanations.

---

## Features
- Search for a movie or choose from a dropdown.
- Configurable number of recommendations.
- Poster images fetched from TMDB.
- Explainable reasons for each recommendation (shared genres, same director, shared cast, short overview snippet).
- Clean Streamlit UI with responsive layout.

---

## Project structure
```
.
├─ App.py                 # Streamlit app (main UI & logic)
├─ Model.ipynb            # Notebook for generating movie features/similarity (training / preprocessing)
├─ movie_dict.pkl         # Pickled dict/list used to build movies DataFrame (required)
├─ similarity.pkl         # Pickled similarity matrix (required)
├─ requirements.txt       # Python dependencies
└─ README.md
```

---

## Requirements

Create a Python 3.10+ virtual environment and install dependencies.

Example `requirements.txt` is included.

Install:
```bash
python -m venv venv
source venv/bin/activate        # macOS / Linux
venv\Scripts\activate.bat       # Windows

pip install -r requirements.txt
```

---

## Setup & run

1. Place the required pickle files in the project root:
   - `movie_dict.pkl`
   - `similarity.pkl`

2. **TMDB API key**  
   The app fetches posters and credits from TMDB.

   Example:
   ```bash
   export TMDB_API_KEY="your_real_tmdb_api_key"
   ```

3. Run the Streamlit app:
```bash
streamlit run App.py
```

---

## Data files required
- `movie_dict.pkl`
- `similarity.pkl`
- 'Download this files from this link ' https://drive.google.com/drive/folders/16sb8RHV-ol6RHIW5T--UotzQJ3HWMpTV?usp=sharing

If not already present, generate them by running `Model.ipynb`.

---

## Credits
Built by **Aryan Patel**.
