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
    "lofi":         {"lofi": 1.0, "ambient": 0.6, "jazz": 0.4, "synthwave": 0.2, "pop": 0.1, "rock": 0.0, "soul": 0.3, "metal": 0.0, "country": 0.1, "electronic": 0.2, "r&b": 0.2, "folk": 0.4, "drum and bass": 0.1, "classical": 0.3},
    "ambient":      {"lofi": 0.6, "ambient": 1.0, "jazz": 0.3, "synthwave": 0.3, "pop": 0.1, "rock": 0.0, "soul": 0.2, "metal": 0.0, "country": 0.0, "electronic": 0.4, "r&b": 0.1, "folk": 0.3, "drum and bass": 0.1, "classical": 0.5},
    "jazz":         {"lofi": 0.4, "ambient": 0.3, "jazz": 1.0, "synthwave": 0.1, "pop": 0.2, "rock": 0.1, "soul": 0.5, "metal": 0.0, "country": 0.2, "electronic": 0.1, "r&b": 0.4, "folk": 0.3, "drum and bass": 0.1, "classical": 0.4},
    "synthwave":    {"lofi": 0.2, "ambient": 0.3, "jazz": 0.1, "synthwave": 1.0, "pop": 0.4, "rock": 0.2, "soul": 0.1, "metal": 0.1, "country": 0.0, "electronic": 0.6, "r&b": 0.1, "folk": 0.0, "drum and bass": 0.3, "classical": 0.1},
    "pop":          {"lofi": 0.1, "ambient": 0.1, "jazz": 0.2, "synthwave": 0.4, "pop": 1.0, "rock": 0.3, "soul": 0.3, "metal": 0.0, "country": 0.2, "electronic": 0.3, "r&b": 0.4, "folk": 0.2, "drum and bass": 0.1, "classical": 0.1},
    "rock":         {"lofi": 0.0, "ambient": 0.0, "jazz": 0.1, "synthwave": 0.2, "pop": 0.3, "rock": 1.0, "soul": 0.1, "metal": 0.5, "country": 0.2, "electronic": 0.1, "r&b": 0.1, "folk": 0.2, "drum and bass": 0.1, "classical": 0.0},
    "soul":         {"lofi": 0.3, "ambient": 0.2, "jazz": 0.5, "synthwave": 0.1, "pop": 0.3, "rock": 0.1, "soul": 1.0, "metal": 0.0, "country": 0.2, "electronic": 0.1, "r&b": 0.7, "folk": 0.2, "drum and bass": 0.0, "classical": 0.2},
    "metal":        {"lofi": 0.0, "ambient": 0.0, "jazz": 0.0, "synthwave": 0.1, "pop": 0.0, "rock": 0.5, "soul": 0.0, "metal": 1.0, "country": 0.0, "electronic": 0.1, "r&b": 0.0, "folk": 0.0, "drum and bass": 0.2, "classical": 0.0},
    "country":      {"lofi": 0.1, "ambient": 0.0, "jazz": 0.2, "synthwave": 0.0, "pop": 0.2, "rock": 0.2, "soul": 0.2, "metal": 0.0, "country": 1.0, "electronic": 0.0, "r&b": 0.1, "folk": 0.6, "drum and bass": 0.0, "classical": 0.1},
    "electronic":   {"lofi": 0.2, "ambient": 0.4, "jazz": 0.1, "synthwave": 0.6, "pop": 0.3, "rock": 0.1, "soul": 0.1, "metal": 0.1, "country": 0.0, "electronic": 1.0, "r&b": 0.2, "folk": 0.0, "drum and bass": 0.5, "classical": 0.1},
    "r&b":          {"lofi": 0.2, "ambient": 0.1, "jazz": 0.4, "synthwave": 0.1, "pop": 0.4, "rock": 0.1, "soul": 0.7, "metal": 0.0, "country": 0.1, "electronic": 0.2, "r&b": 1.0, "folk": 0.1, "drum and bass": 0.1, "classical": 0.1},
    "folk":         {"lofi": 0.4, "ambient": 0.3, "jazz": 0.3, "synthwave": 0.0, "pop": 0.2, "rock": 0.2, "soul": 0.2, "metal": 0.0, "country": 0.6, "electronic": 0.0, "r&b": 0.1, "folk": 1.0, "drum and bass": 0.0, "classical": 0.3},
    "drum and bass":{"lofi": 0.1, "ambient": 0.1, "jazz": 0.1, "synthwave": 0.3, "pop": 0.1, "rock": 0.1, "soul": 0.0, "metal": 0.2, "country": 0.0, "electronic": 0.5, "r&b": 0.1, "folk": 0.0, "drum and bass": 1.0, "classical": 0.0},
    "classical":    {"lofi": 0.3, "ambient": 0.5, "jazz": 0.4, "synthwave": 0.1, "pop": 0.1, "rock": 0.0, "soul": 0.2, "metal": 0.0, "country": 0.1, "electronic": 0.1, "r&b": 0.1, "folk": 0.3, "drum and bass": 0.0, "classical": 1.0},
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
        self.songs = songs

    def recommend(self, user: UserProfile, k: int = 5) -> List[Song]:
        # TODO: Implement recommendation logic
        return self.songs[:k]

    def explain_recommendation(self, user: UserProfile, song: Song) -> str:
        # TODO: Implement explanation logic
        return "Explanation placeholder"

def load_songs(csv_path: str) -> List[Dict]:
    """
    Loads songs from a CSV file.
    Required by src/main.py
    """
    # TODO: Implement CSV loading logic
    print(f"Loading songs from {csv_path}...")
    return []

def recommend_songs(user_prefs: Dict, songs: List[Dict], k: int = 5) -> List[Tuple[Dict, float, str]]:
    """
    Functional implementation of the recommendation logic.
    Required by src/main.py
    """
    # TODO: Implement scoring and ranking logic
    # Expected return format: (song_dict, score, explanation)
    return []
