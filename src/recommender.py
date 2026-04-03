from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass

# Mood similarity table — partial credit for adjacent moods.
# Original moods: chill, relaxed, focused, moody, happy, intense
# Added: melancholic, nostalgic, romantic, sad, serene, energetic, aggressive, tense
MOOD_SIMILARITY: Dict[str, Dict[str, float]] = {
    "chill":       {"chill": 1.0, "relaxed": 0.7, "focused": 0.4, "moody": 0.2, "happy": 0.1, "intense": 0.0, "melancholic": 0.2, "nostalgic": 0.3, "romantic": 0.3, "sad": 0.1, "serene": 0.8, "energetic": 0.0, "aggressive": 0.0, "tense": 0.0},
    "relaxed":     {"chill": 0.7, "relaxed": 1.0, "focused": 0.4, "moody": 0.3, "happy": 0.2, "intense": 0.0, "melancholic": 0.2, "nostalgic": 0.4, "romantic": 0.4, "sad": 0.1, "serene": 0.6, "energetic": 0.1, "aggressive": 0.0, "tense": 0.0},
    "focused":     {"chill": 0.4, "relaxed": 0.4, "focused": 1.0, "moody": 0.2, "happy": 0.1, "intense": 0.1, "melancholic": 0.1, "nostalgic": 0.1, "romantic": 0.1, "sad": 0.0, "serene": 0.3, "energetic": 0.3, "aggressive": 0.0, "tense": 0.2},
    "moody":       {"chill": 0.2, "relaxed": 0.3, "focused": 0.2, "moody": 1.0, "happy": 0.0, "intense": 0.2, "melancholic": 0.6, "nostalgic": 0.4, "romantic": 0.2, "sad": 0.5, "serene": 0.1, "energetic": 0.1, "aggressive": 0.2, "tense": 0.3},
    "happy":       {"chill": 0.1, "relaxed": 0.2, "focused": 0.1, "moody": 0.0, "happy": 1.0, "intense": 0.3, "melancholic": 0.0, "nostalgic": 0.3, "romantic": 0.4, "sad": 0.0, "serene": 0.2, "energetic": 0.5, "aggressive": 0.0, "tense": 0.0},
    "intense":     {"chill": 0.0, "relaxed": 0.0, "focused": 0.1, "moody": 0.2, "happy": 0.3, "intense": 1.0, "melancholic": 0.0, "nostalgic": 0.0, "romantic": 0.0, "sad": 0.0, "serene": 0.0, "energetic": 0.7, "aggressive": 0.6, "tense": 0.5},
    "melancholic": {"chill": 0.2, "relaxed": 0.2, "focused": 0.1, "moody": 0.6, "happy": 0.0, "intense": 0.0, "melancholic": 1.0, "nostalgic": 0.5, "romantic": 0.2, "sad": 0.7, "serene": 0.1, "energetic": 0.0, "aggressive": 0.0, "tense": 0.1},
    "nostalgic":   {"chill": 0.3, "relaxed": 0.4, "focused": 0.1, "moody": 0.4, "happy": 0.3, "intense": 0.0, "melancholic": 0.5, "nostalgic": 1.0, "romantic": 0.4, "sad": 0.3, "serene": 0.3, "energetic": 0.1, "aggressive": 0.0, "tense": 0.0},
    "romantic":    {"chill": 0.3, "relaxed": 0.4, "focused": 0.1, "moody": 0.2, "happy": 0.4, "intense": 0.0, "melancholic": 0.2, "nostalgic": 0.4, "romantic": 1.0, "sad": 0.1, "serene": 0.4, "energetic": 0.2, "aggressive": 0.0, "tense": 0.0},
    "sad":         {"chill": 0.1, "relaxed": 0.1, "focused": 0.0, "moody": 0.5, "happy": 0.0, "intense": 0.0, "melancholic": 0.7, "nostalgic": 0.3, "romantic": 0.1, "sad": 1.0, "serene": 0.1, "energetic": 0.0, "aggressive": 0.0, "tense": 0.1},
    "serene":      {"chill": 0.8, "relaxed": 0.6, "focused": 0.3, "moody": 0.1, "happy": 0.2, "intense": 0.0, "melancholic": 0.1, "nostalgic": 0.3, "romantic": 0.4, "sad": 0.1, "serene": 1.0, "energetic": 0.0, "aggressive": 0.0, "tense": 0.0},
    "energetic":   {"chill": 0.0, "relaxed": 0.1, "focused": 0.3, "moody": 0.1, "happy": 0.5, "intense": 0.7, "melancholic": 0.0, "nostalgic": 0.1, "romantic": 0.2, "sad": 0.0, "serene": 0.0, "energetic": 1.0, "aggressive": 0.4, "tense": 0.3},
    "aggressive":  {"chill": 0.0, "relaxed": 0.0, "focused": 0.0, "moody": 0.2, "happy": 0.0, "intense": 0.6, "melancholic": 0.0, "nostalgic": 0.0, "romantic": 0.0, "sad": 0.0, "serene": 0.0, "energetic": 0.4, "aggressive": 1.0, "tense": 0.5},
    "tense":       {"chill": 0.0, "relaxed": 0.0, "focused": 0.2, "moody": 0.3, "happy": 0.0, "intense": 0.5, "melancholic": 0.1, "nostalgic": 0.0, "romantic": 0.0, "sad": 0.1, "serene": 0.0, "energetic": 0.3, "aggressive": 0.5, "tense": 1.0},
}

# Genre similarity table — structurally related genres get partial credit.
# Original genres: lofi, ambient, jazz, synthwave, pop, rock
# Added: soul, metal, country, electronic, r&b, folk, drum and bass, classical
GENRE_SIMILARITY: Dict[str, Dict[str, float]] = {
    "lofi":         {"lofi": 1.0, "ambient": 0.6, "jazz": 0.4, "synthwave": 0.2, "pop": 0.1, "rock": 0.0, "soul": 0.3, "metal": 0.0, "country": 0.1, "electronic": 0.2, "r&b": 0.2, "folk": 0.4, "drum and bass": 0.1, "classical": 0.3, "indie pop": 0.2},
    "ambient":      {"lofi": 0.6, "ambient": 1.0, "jazz": 0.3, "synthwave": 0.3, "pop": 0.1, "rock": 0.0, "soul": 0.2, "metal": 0.0, "country": 0.0, "electronic": 0.4, "r&b": 0.1, "folk": 0.3, "drum and bass": 0.1, "classical": 0.5, "indie pop": 0.2},
    "jazz":         {"lofi": 0.4, "ambient": 0.3, "jazz": 1.0, "synthwave": 0.1, "pop": 0.2, "rock": 0.1, "soul": 0.5, "metal": 0.0, "country": 0.2, "electronic": 0.1, "r&b": 0.4, "folk": 0.3, "drum and bass": 0.1, "classical": 0.4, "indie pop": 0.2},
    "synthwave":    {"lofi": 0.2, "ambient": 0.3, "jazz": 0.1, "synthwave": 1.0, "pop": 0.4, "rock": 0.2, "soul": 0.1, "metal": 0.1, "country": 0.0, "electronic": 0.6, "r&b": 0.1, "folk": 0.0, "drum and bass": 0.3, "classical": 0.1, "indie pop": 0.3},
    "pop":          {"lofi": 0.1, "ambient": 0.1, "jazz": 0.2, "synthwave": 0.4, "pop": 1.0, "rock": 0.3, "soul": 0.3, "metal": 0.0, "country": 0.2, "electronic": 0.3, "r&b": 0.4, "folk": 0.2, "drum and bass": 0.1, "classical": 0.1, "indie pop": 0.7},
    "rock":         {"lofi": 0.0, "ambient": 0.0, "jazz": 0.1, "synthwave": 0.2, "pop": 0.3, "rock": 1.0, "soul": 0.1, "metal": 0.5, "country": 0.2, "electronic": 0.1, "r&b": 0.1, "folk": 0.2, "drum and bass": 0.1, "classical": 0.0, "indie pop": 0.3},
    "soul":         {"lofi": 0.3, "ambient": 0.2, "jazz": 0.5, "synthwave": 0.1, "pop": 0.3, "rock": 0.1, "soul": 1.0, "metal": 0.0, "country": 0.2, "electronic": 0.1, "r&b": 0.7, "folk": 0.2, "drum and bass": 0.0, "classical": 0.2, "indie pop": 0.2},
    "metal":        {"lofi": 0.0, "ambient": 0.0, "jazz": 0.0, "synthwave": 0.1, "pop": 0.0, "rock": 0.5, "soul": 0.0, "metal": 1.0, "country": 0.0, "electronic": 0.1, "r&b": 0.0, "folk": 0.0, "drum and bass": 0.2, "classical": 0.0, "indie pop": 0.0},
    "country":      {"lofi": 0.1, "ambient": 0.0, "jazz": 0.2, "synthwave": 0.0, "pop": 0.2, "rock": 0.2, "soul": 0.2, "metal": 0.0, "country": 1.0, "electronic": 0.0, "r&b": 0.1, "folk": 0.6, "drum and bass": 0.0, "classical": 0.1, "indie pop": 0.2},
    "electronic":   {"lofi": 0.2, "ambient": 0.4, "jazz": 0.1, "synthwave": 0.6, "pop": 0.3, "rock": 0.1, "soul": 0.1, "metal": 0.1, "country": 0.0, "electronic": 1.0, "r&b": 0.2, "folk": 0.0, "drum and bass": 0.5, "classical": 0.1, "indie pop": 0.2},
    "r&b":          {"lofi": 0.2, "ambient": 0.1, "jazz": 0.4, "synthwave": 0.1, "pop": 0.4, "rock": 0.1, "soul": 0.7, "metal": 0.0, "country": 0.1, "electronic": 0.2, "r&b": 1.0, "folk": 0.1, "drum and bass": 0.1, "classical": 0.1, "indie pop": 0.3},
    "folk":         {"lofi": 0.4, "ambient": 0.3, "jazz": 0.3, "synthwave": 0.0, "pop": 0.2, "rock": 0.2, "soul": 0.2, "metal": 0.0, "country": 0.6, "electronic": 0.0, "r&b": 0.1, "folk": 1.0, "drum and bass": 0.0, "classical": 0.3, "indie pop": 0.4},
    "drum and bass":{"lofi": 0.1, "ambient": 0.1, "jazz": 0.1, "synthwave": 0.3, "pop": 0.1, "rock": 0.1, "soul": 0.0, "metal": 0.2, "country": 0.0, "electronic": 0.5, "r&b": 0.1, "folk": 0.0, "drum and bass": 1.0, "classical": 0.0, "indie pop": 0.0},
    "classical":    {"lofi": 0.3, "ambient": 0.5, "jazz": 0.4, "synthwave": 0.1, "pop": 0.1, "rock": 0.0, "soul": 0.2, "metal": 0.0, "country": 0.1, "electronic": 0.1, "r&b": 0.1, "folk": 0.3, "drum and bass": 0.0, "classical": 1.0, "indie pop": 0.1},
    "indie pop":    {"lofi": 0.2, "ambient": 0.2, "jazz": 0.2, "synthwave": 0.3, "pop": 0.7, "rock": 0.3, "soul": 0.2, "metal": 0.0, "country": 0.2, "electronic": 0.2, "r&b": 0.3, "folk": 0.4, "drum and bass": 0.0, "classical": 0.1, "indie pop": 1.0},
}

@dataclass
class Song:
    """
    Represents a song and its attributes.
    Required by tests/test_recommender.py
    """
    id: int
    title: str
    artist: str
    genre: str
    mood: str
    energy: float
    tempo_bpm: float
    valence: float
    danceability: float
    acousticness: float

@dataclass
class UserProfile:
    """
    Represents a user's taste preferences.
    Required by tests/test_recommender.py
    """
    favorite_genre: str
    favorite_mood: str
    target_energy: float
    likes_acoustic: bool

class Recommender:
    """
    OOP implementation of the recommendation logic.
    Required by tests/test_recommender.py
    """
    def __init__(self, songs: List[Song]):
        """Initialize the Recommender with a list of songs."""
        self.songs = songs

    def _to_prefs(self, user: UserProfile) -> Dict:
        """Convert a UserProfile dataclass into a preferences dict for score_song."""
        return {
            "favorite_genre": user.favorite_genre,
            "favorite_mood":  user.favorite_mood,
            "target_energy":  user.target_energy,
            "likes_acoustic": user.likes_acoustic,
        }

    def _to_dict(self, song: Song) -> Dict:
        """Convert a Song dataclass into a dict of scoring-relevant fields."""
        return {
            "genre":        song.genre,
            "mood":         song.mood,
            "energy":       song.energy,
            "acousticness": song.acousticness,
        }

    def recommend(self, user: UserProfile, k: int = 5, artist_decay: float = 0.5) -> List[Song]:
        """Return the top k songs ranked by score against the user's profile.

        Uses a greedy diversity penalty to avoid recommending too many songs
        from the same artist. Instead of sorting all songs once and slicing,
        songs are selected one at a time. Each time an artist is already
        represented in the results, every remaining song by that artist has
        its score multiplied by `artist_decay` before the next pick.

        artist_decay controls how harshly repeat artists are penalized:
            1.0 — no penalty (same as a plain top-k sort)
            0.5 — score halved for each additional song from the same artist
            0.0 — hard block: only one song per artist ever selected
        """
        prefs = self._to_prefs(user)
        candidates = [(s, score_song(prefs, self._to_dict(s))[0]) for s in self.songs]
        artist_counts: Dict[str, int] = {}
        results: List[Song] = []

        for _ in range(k):
            remaining = [(s, sc) for s, sc in candidates if s not in results]
            if not remaining:
                break
            penalized = [
                (s, sc * (artist_decay ** artist_counts.get(s.artist, 0)))
                for s, sc in remaining
            ]
            best = max(penalized, key=lambda x: x[1])
            results.append(best[0])
            artist_counts[best[0].artist] = artist_counts.get(best[0].artist, 0) + 1

        return results

    def explain_recommendation(self, user: UserProfile, song: Song) -> str:
        """Return a human-readable breakdown of why a song was recommended."""
        _, reasons = score_song(self._to_prefs(user), self._to_dict(song))
        return "\n".join(reasons)

def score_song(user_prefs: Dict, song: Dict) -> Tuple[float, List[str]]:
    """
    Scores a single song against user preferences.
    Returns (total_score, reasons) where reasons explains each component.
    """
    import math
    reasons = []

    # Mood score — similarity table lookup
    user_mood = user_prefs["favorite_mood"]
    song_mood = song["mood"]
    mood_sim = MOOD_SIMILARITY.get(user_mood, {}).get(song_mood, 0.0)
    mood_score = 0.35 * mood_sim
    reasons.append(f"mood '{song_mood}' vs '{user_mood}' (+{mood_score:.2f})")

    # Genre score — similarity table lookup
    user_genre = user_prefs["favorite_genre"]
    song_genre = song["genre"]
    genre_sim = GENRE_SIMILARITY.get(user_genre, {}).get(song_genre, 0.0)
    genre_score = 0.25 * genre_sim
    reasons.append(f"genre '{song_genre}' vs '{user_genre}' (+{genre_score:.2f})")

    # Energy score — Gaussian proximity (σ = 0.20)
    target_energy = user_prefs["target_energy"]
    energy_sim = math.exp(-((song["energy"] - target_energy) ** 2) / (2 * 0.20 ** 2))
    energy_score = 0.25 * energy_sim
    reasons.append(f"energy {song['energy']:.2f} vs target {target_energy:.2f} (+{energy_score:.2f})")

    # Acousticness score — boolean directional
    likes_acoustic = user_prefs["likes_acoustic"]
    acoustic_sim = song["acousticness"] if likes_acoustic else (1 - song["acousticness"])
    acoustic_score = 0.15 * acoustic_sim
    reasons.append(f"acousticness {song['acousticness']:.2f} ({'acoustic' if likes_acoustic else 'electronic'} preference) (+{acoustic_score:.2f})")

    total = mood_score + genre_score + energy_score + acoustic_score
    return total, reasons


def load_songs(csv_path: str) -> List[Dict]:
    """
    Loads songs from a CSV file.
    Required by src/main.py
    """
    import csv
    songs = []
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            songs.append({
                "id":            int(row["id"]),
                "title":         row["title"],
                "artist":        row["artist"],
                "genre":         row["genre"],
                "mood":          row["mood"],
                "energy":        float(row["energy"]),
                "tempo_bpm":     float(row["tempo_bpm"]),
                "valence":       float(row["valence"]),
                "danceability":  float(row["danceability"]),
                "acousticness":  float(row["acousticness"]),
            })
    return songs

def recommend_songs(user_prefs: Dict, songs: List[Dict], k: int = 5, artist_decay: float = 0.5) -> List[Tuple[Dict, float, str]]:
    """
    Functional implementation of the recommendation logic.
    Required by src/main.py

    Uses a greedy diversity penalty to avoid recommending too many songs
    from the same artist. Instead of sorting all songs once and slicing,
    songs are selected one at a time. Each time an artist is already
    represented in the results, every remaining song by that artist has
    its score multiplied by `artist_decay` before the next pick.

    artist_decay controls how harshly repeat artists are penalized:
        1.0 — no penalty (same as a plain top-k sort)
        0.5 — score halved for each additional song from the same artist
        0.0 — hard block: only one song per artist ever selected
    """
    candidates = [(song, *score_song(user_prefs, song)) for song in songs]
    artist_counts: Dict[str, int] = {}
    results = []

    for _ in range(k):
        remaining = [(s, sc, r) for s, sc, r in candidates if s not in [x[0] for x in results]]
        if not remaining:
            break
        penalized = [
            (s, sc * (artist_decay ** artist_counts.get(s["artist"], 0)), r)
            for s, sc, r in remaining
        ]
        best = max(penalized, key=lambda x: x[1])
        results.append(best)
        artist_counts[best[0]["artist"]] = artist_counts.get(best[0]["artist"], 0) + 1

    return [(song, score, "\n  ".join(reasons)) for song, score, reasons in results]
