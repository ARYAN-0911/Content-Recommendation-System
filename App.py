import requests
import streamlit as st
import pickle
import pandas as pd


#  Configuration
st.set_page_config(
    page_title="✨ WhyWatch — Smart Movie Recommender",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="auto",
)

TMDB_API_KEY = "ADD YOUR API KEY HERE"  # original Key

# Helper functions (cached where appropriate)
@st.cache_data(show_spinner=False)
def get_movie_details(movie_id):
    """
    Returns a dict with keys: 'genres' (list of names), 'overview' (str),
    'title' (str), 'director' (str or None), 'cast' (list of names)
    """
    url = f'https://api.themoviedb.org/3/movie/{movie_id}'
    params = {
        'api_key': TMDB_API_KEY,
        'append_to_response': 'credits'
    }
    r = requests.get(url, params=params, timeout=8)
    if r.status_code != 200:
        return {}
    data = r.json()
    genres = [g['name'] for g in data.get('genres', [])]
    overview = data.get('overview', '') or ''
    title = data.get('title', '')
    credits = data.get('credits', {})
    director = None
    for person in credits.get('crew', []):
        if person.get('job') == 'Director':
            director = person.get('name')
            break
    cast = [c.get('name') for c in credits.get('cast', [])[:5]]
    return {
        'movie_id': movie_id,
        'title': title,
        'genres': genres,
        'overview': overview,
        'director': director,
        'cast': cast
    }

@st.cache_data(show_spinner=False)
def fatch_poster(movie_id):
    """Fetch poster url from TMDB (cached)."""
    try:
        response = requests.get(
            f'https://api.themoviedb.org/3/movie/{movie_id}',
            params={'api_key': TMDB_API_KEY, 'language': 'en-US'},
            timeout=6
        )
        data = response.json()
        poster_path = data.get('poster_path') or ""
        return "https://image.tmdb.org/t/p/w500/" + poster_path if poster_path else None
    except Exception:
        return None

def short_overview(text, max_chars=140):
    if not text:
        return ""
    text = " ".join(text.split())
    return (text[:max_chars].rsplit(' ', 1)[0] + '...') if len(text) > max_chars else text

def make_reason_string(base_meta, rec_meta):
    reasons = []
    base_genres = set(g.lower() for g in base_meta.get('genres', []))
    rec_genres = set(g.lower() for g in rec_meta.get('genres', []))
    shared_genres = base_genres.intersection(rec_genres)
    if shared_genres:
        sg = ", ".join(sorted([g.title() for g in shared_genres]))
        reasons.append(f"Both movies share genres: {sg}")

    if base_meta.get('director') and rec_meta.get('director'):
        if base_meta['director'] == rec_meta['director']:
            reasons.append(f"Both are directed by {base_meta['director']}")

    base_cast = set([c.lower() for c in base_meta.get('cast', [])])
    rec_cast = set([c.lower() for c in rec_meta.get('cast', [])])
    common_cast = base_cast.intersection(rec_cast)
    if common_cast:
        names = ", ".join([n.title() for n in list(common_cast)[:2]])
        reasons.append(f"Shared cast: {names}")

    base_tokens = set(w.lower().strip(".,:;!?'\"") for w in base_meta.get('overview','').split() if len(w) > 3)
    rec_tokens  = set(w.lower().strip(".,:;!?'\"") for w in rec_meta.get('overview','').split() if len(w) > 3)
    token_overlap = base_tokens.intersection(rec_tokens)
    # Keep heuristic but don't necessarily surface tokens unless we want to
    if reasons:
        explanation = ". ".join(reasons) + "."
    else:
        explanation = "Recommendations are based on content similarity (genre, themes, plot and crew)."

    short_over = short_overview(rec_meta.get('overview', ''), max_chars=180)
    if short_over:
        explanation += " " + short_over

    return explanation

@st.cache_data(show_spinner=False)
def explain_recommendation_for_movie(base_movie_title, rec_titles, movies_df):
    try:
        base_idx = movies_df[movies_df['title'] == base_movie_title].index[0]
    except Exception:
        return [""] * len(rec_titles)
    base_id = movies_df.iloc[base_idx].movie_id
    base_meta = get_movie_details(base_id)
    explanations = []
    for rt in rec_titles:
        try:
            ridx = movies_df[movies_df['title'] == rt].index[0]
            rec_id = movies_df.iloc[ridx].movie_id
        except Exception:
            explanations.append("")
            continue
        rec_meta = get_movie_details(rec_id)
        explanations.append(make_reason_string(base_meta, rec_meta))
    return explanations

# ---------- Load model/data (as in original file) ----------
@st.cache_data(show_spinner=False)
def load_data():
    movies_dict = pickle.load(open('movie_dict.pkl','rb'))
    movies_df = pd.DataFrame(movies_dict)
    similarity_mat = pickle.load(open('similarity.pkl','rb'))
    return movies_df, similarity_mat

movies, similarity = load_data()

# Keep Recommend function logic unchanged
def Recommend(movie, top_k=5):
    movie_index = movies[movies['title'] == movie].index[0]
    distances = similarity[movie_index]
    movies_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1: top_k+1]
    recommended_movie = []
    recommended_posters = []
    for i in movies_list:
        movie_id = movies.iloc[i[0]].movie_id
        recommended_movie.append(movies.iloc[i[0]].title)
        recommended_posters.append(fatch_poster(movie_id))
    return recommended_movie, recommended_posters

# ---------- UI styling ----------
st.markdown(
    """
    
    <h1 style='color:#00BFA5; text-align:center;'>🎬 <span style="color:#F72585; font-weight:bold;">WhyWatch</span> - The Smart Movie Recommender</h1>

    <style>
    .stApp { background: linear-gradient(180deg, #0f172a 0%, #071029 100%); color: #e6eef8; }
    .movie-card { padding: 12px; border-radius: 12px; background: rgba(255,255,255,0.03); box-shadow: 0 6px 18px rgba(2,6,23,0.6); }
    .title { font-weight: 700; font-size: 32px; }
    .muted { color: #9fb1d4; }
    .small { font-size: 13px; color:#bcd2f0; }
    </style>
    """,
    unsafe_allow_html=True
)

# ---------- Sidebar ----------
with st.sidebar:
    st.title("🎬 WhyWatch")
    st.write("An explainable movie recommender — shows *why* each suggestion was chosen.")
    st.markdown("---")
    st.markdown("**Controls**")
    rec_count = st.slider("Number of recommendations", min_value=1, max_value=8, value=5, step=1)
    st.markdown("---")
    st.markdown("**About**")
    st.markdown("This UI is a cleaned, modern view of the original Streamlit app. Poster and metadata are fetched from TMDB API.")
    st.markdown("---")

# ---------- Main layout ----------
col_left, col_right = st.columns([3,1])

with col_left:
    #st.markdown('<div class="title">WhyWatch — Smart Recommendations</div>', unsafe_allow_html=True)
    st.markdown('<div class="muted">Select a movie and get explainable recommendations</div>', unsafe_allow_html=True)
    st.markdown("")

    # Provide both a text input (for typing) and a selectbox (for quick pick)
    search = st.text_input("Search title (type full or partial)", key="movie_search", placeholder="e.g. Avatar")
    # Filter suggestions based on typed text
    if search:
        options = movies[movies['title'].str.contains(search, case=False, na=False, regex=False)].title.values.tolist()
        if not options:
            options = movies['title'].values[:200].tolist()
    else:
        options = movies['title'].values[:200].tolist()

    selected_movie_name = st.selectbox("Or choose from list", options=options, index=0 if 'selected_movie' not in st.session_state else None)

    # Allow Enter or button to recommend
    recommend_btn = st.button("Recommend", key="recommend_button")

with col_right:
    st.markdown("### Selected movie")
    # Show a small preview box for currently selected movie
    try:
        if selected_movie_name:
            idx = movies[movies['title'] == selected_movie_name].index[0]
            mid = movies.iloc[idx].movie_id
            poster_url = fatch_poster(mid)
            st.markdown(f"**{selected_movie_name}**")
            if poster_url:
                # <-- fix applied here: use_container_width instead of deprecated use_column_width
                st.image(poster_url, use_container_width=True)
            # show small metadata
            md = get_movie_details(mid)
            if md:
                st.markdown(f"*Genres:* {', '.join(md.get('genres', [])[:3])}")
                if md.get('director'):
                    st.markdown(f"*Director:* {md.get('director')}")
                if md.get('cast'):
                    st.markdown(f"*Cast:* {', '.join(md.get('cast', [])[:3])}")
    except Exception:
        st.info("Select a valid movie from the list")

st.markdown("---")

# ---------- Recommendation results ----------
if recommend_btn:
    with st.spinner("Finding movies similar to \"" + str(selected_movie_name) + "\" ..."):
        try:
            names, posters = Recommend(selected_movie_name, top_k=rec_count)
            explanations = explain_recommendation_for_movie(selected_movie_name, names, movies)

            # Responsive grid: choose 3 columns on wide screens or dynamic based on rec_count
            per_row = 3 if rec_count >= 3 else rec_count
            rows = (rec_count + per_row - 1) // per_row
            idx = 0
            for r in range(rows):
                cols = st.columns(per_row)
                for c in cols:
                    if idx >= len(names):
                        break
                    with c:
                        st.markdown(f'<div class="movie-card">', unsafe_allow_html=True)
                        st.markdown(f"**{names[idx]}**")
                        if posters[idx]:
                            # <-- fix applied here as well
                            st.image(posters[idx], use_container_width=True)
                        else:
                            st.info("Poster not available")
                        # short metadata line
                        try:
                            m_idx = movies[movies['title'] == names[idx]].index[0]
                            m_id = movies.iloc[m_idx].movie_id
                            md = get_movie_details(m_id)
                            if md:
                                genres = ", ".join(md.get('genres', [])[:3])
                                director = md.get('director') or "Unknown"
                                st.markdown(f"<div class='small'>Genres: {genres}</div>", unsafe_allow_html=True)
                                st.markdown(f"<div class='small'>Director: {director}</div>", unsafe_allow_html=True)
                        except Exception:
                            pass

                        # explanation in an expander for cleanliness
                        if explanations and explanations[idx]:
                            with st.expander("Why this recommendation?"):
                                st.write(explanations[idx])
                        st.markdown("</div>", unsafe_allow_html=True)
                        idx += 1
                st.write("")  # spacing
        except Exception as e:
            st.error("Something went wrong while computing recommendations: " + str(e))
            st.stop()

else:
    st.info("Pick a movie and click **Recommend** to get suggestions.")

# ---------- footer ----------
st.markdown("---")
st.markdown("Built By Aryan Patel")
