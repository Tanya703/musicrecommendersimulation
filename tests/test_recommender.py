import math
import pytest
from src.recommender import Song, UserProfile, Recommender, score_song


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def make_song(
    id=1,
    title="Test Song",
    artist="Artist A",
    genre="pop",
    mood="happy",
    energy=0.8,
    acousticness=0.2,
    tempo_bpm=120,
    valence=0.9,
    danceability=0.8,
) -> Song:
    return Song(
        id=id, title=title, artist=artist, genre=genre, mood=mood,
        energy=energy, tempo_bpm=tempo_bpm, valence=valence,
        danceability=danceability, acousticness=acousticness,
    )


def make_small_recommender() -> Recommender:
    songs = [
        Song(
            id=1,
            title="Test Pop Track",
            artist="Test Artist",
            genre="pop",
            mood="happy",
            energy=0.8,
            tempo_bpm=120,
            valence=0.9,
            danceability=0.8,
            acousticness=0.2,
        ),
        Song(
            id=2,
            title="Chill Lofi Loop",
            artist="Test Artist",
            genre="lofi",
            mood="chill",
            energy=0.4,
            tempo_bpm=80,
            valence=0.6,
            danceability=0.5,
            acousticness=0.9,
        ),
    ]
    return Recommender(songs)


def test_recommend_returns_songs_sorted_by_score():
    user = UserProfile(
        favorite_genre="pop",
        favorite_mood="happy",
        target_energy=0.8,
        likes_acoustic=False,
    )
    rec = make_small_recommender()
    results = rec.recommend(user, k=2)

    assert len(results) == 2
    # Starter expectation: the pop, happy, high energy song should score higher
    assert results[0].genre == "pop"
    assert results[0].mood == "happy"


def test_explain_recommendation_returns_non_empty_string():
    user = UserProfile(
        favorite_genre="pop",
        favorite_mood="happy",
        target_energy=0.8,
        likes_acoustic=False,
    )
    rec = make_small_recommender()
    song = rec.songs[0]

    explanation = rec.explain_recommendation(user, song)
    assert isinstance(explanation, str)
    assert explanation.strip() != ""


# ---------------------------------------------------------------------------
# 3. recommend returns exactly k results when k <= catalog size
# ---------------------------------------------------------------------------

def test_recommend_returns_exactly_k_results():
    songs = [make_song(id=i, title=f"Song {i}", artist=f"Artist {i}") for i in range(10)]
    rec = Recommender(songs)
    user = UserProfile(favorite_genre="pop", favorite_mood="happy", target_energy=0.8, likes_acoustic=False)

    assert len(rec.recommend(user, k=5)) == 5


# ---------------------------------------------------------------------------
# 4. recommend returns all songs when k exceeds catalog size
# ---------------------------------------------------------------------------

def test_recommend_k_exceeds_catalog_returns_all_songs():
    songs = [make_song(id=i, title=f"Song {i}", artist=f"Artist {i}") for i in range(3)]
    rec = Recommender(songs)
    user = UserProfile(favorite_genre="pop", favorite_mood="happy", target_energy=0.8, likes_acoustic=False)

    assert len(rec.recommend(user, k=100)) == 3


# ---------------------------------------------------------------------------
# 5. recommend with k=0 returns empty list
# ---------------------------------------------------------------------------

def test_recommend_k_zero_returns_empty_list():
    rec = make_small_recommender()
    user = UserProfile(favorite_genre="pop", favorite_mood="happy", target_energy=0.8, likes_acoustic=False)

    assert rec.recommend(user, k=0) == []


# ---------------------------------------------------------------------------
# 6. Diversity: decay=0.5 prevents picking two songs from same artist
#    when a lower-scoring song from a different artist exists
# ---------------------------------------------------------------------------

def test_diversity_penalty_prevents_repeat_artist():
    # A1, A2 are perfect matches from "Dominant Artist"
    # B scores lower (genre mismatch) but from "Other Artist"
    songs = [
        make_song(id=1, title="A1", artist="Dominant Artist", genre="pop", mood="happy", energy=0.8, acousticness=0.0),
        make_song(id=2, title="A2", artist="Dominant Artist", genre="pop", mood="happy", energy=0.8, acousticness=0.0),
        make_song(id=3, title="B",  artist="Other Artist",    genre="lofi", mood="happy", energy=0.8, acousticness=0.0),
    ]
    rec = Recommender(songs)
    user = UserProfile(favorite_genre="pop", favorite_mood="happy", target_energy=0.8, likes_acoustic=False)
    results = rec.recommend(user, k=2, artist_decay=0.5)

    artists = [s.artist for s in results]
    assert "Dominant Artist" in artists
    assert "Other Artist" in artists


# ---------------------------------------------------------------------------
# 7. Diversity: decay=1.0 (no penalty) allows repeat artist in top-k
# ---------------------------------------------------------------------------

def test_diversity_decay_one_allows_repeat_artist():
    songs = [
        make_song(id=1, title="A1", artist="Dominant Artist", genre="pop", mood="happy", energy=0.8, acousticness=0.0),
        make_song(id=2, title="A2", artist="Dominant Artist", genre="pop", mood="happy", energy=0.8, acousticness=0.0),
        make_song(id=3, title="B",  artist="Other Artist",    genre="metal", mood="aggressive", energy=0.95, acousticness=0.0),
    ]
    rec = Recommender(songs)
    user = UserProfile(favorite_genre="pop", favorite_mood="happy", target_energy=0.8, likes_acoustic=False)
    results = rec.recommend(user, k=2, artist_decay=1.0)

    assert sum(1 for s in results if s.artist == "Dominant Artist") == 2


# ---------------------------------------------------------------------------
# 8. Diversity: decay=0.0 hard-blocks — at most one song per artist
# ---------------------------------------------------------------------------

def test_diversity_decay_zero_hard_blocks_artist():
    # 2 songs from "Solo Artist" both outscore "Other Artist", but decay=0.0
    # zeros out the second Solo Artist pick — so Other Artist wins slot 2.
    songs = [
        make_song(id=1, title="A1", artist="Solo Artist", genre="pop", mood="happy", energy=0.8, acousticness=0.0),
        make_song(id=2, title="A2", artist="Solo Artist", genre="pop", mood="happy", energy=0.8, acousticness=0.0),
        make_song(id=3, title="B",  artist="Other Artist", genre="lofi", mood="chill", energy=0.4, acousticness=0.9),
    ]
    rec = Recommender(songs)
    user = UserProfile(favorite_genre="pop", favorite_mood="happy", target_energy=0.8, likes_acoustic=False)
    results = rec.recommend(user, k=2, artist_decay=0.0)

    assert sum(1 for s in results if s.artist == "Solo Artist") == 1
    assert sum(1 for s in results if s.artist == "Other Artist") == 1


# ---------------------------------------------------------------------------
# 9. score_song: perfect match on all dimensions scores exactly 1.0
# ---------------------------------------------------------------------------

def test_score_song_perfect_match_scores_one():
    prefs = {"favorite_genre": "pop", "favorite_mood": "happy", "target_energy": 0.8, "likes_acoustic": False}
    song  = {"genre": "pop", "mood": "happy", "energy": 0.8, "acousticness": 0.0}

    score, _ = score_song(prefs, song)
    assert abs(score - 1.0) < 1e-9


# ---------------------------------------------------------------------------
# 10. score_song: mood exact match contributes full 0.35 weight
# ---------------------------------------------------------------------------

def test_score_song_mood_exact_match_contributes_full_weight():
    # likes_acoustic=True with acousticness=0.0 → acoustic component = 0
    prefs = {"favorite_genre": "pop", "favorite_mood": "happy", "target_energy": 0.8, "likes_acoustic": True}
    song  = {"genre": "pop", "mood": "happy", "energy": 0.8, "acousticness": 0.0}

    score, _ = score_song(prefs, song)
    # mood: 0.35, genre: 0.25, energy: 0.25, acoustic: 0.15*0.0 = 0.0 → total 0.85
    assert abs(score - 0.85) < 1e-9


# ---------------------------------------------------------------------------
# 11. score_song: related moods receive partial credit (chill → relaxed = 0.7)
# ---------------------------------------------------------------------------

def test_score_song_mood_partial_credit_for_related_moods():
    prefs = {"favorite_genre": "lofi", "favorite_mood": "chill", "target_energy": 0.4, "likes_acoustic": True}
    song_exact   = {"genre": "lofi", "mood": "chill",   "energy": 0.4, "acousticness": 1.0}
    song_related = {"genre": "lofi", "mood": "relaxed", "energy": 0.4, "acousticness": 1.0}

    score_exact, _   = score_song(prefs, song_exact)
    score_related, _ = score_song(prefs, song_related)

    assert score_related < score_exact
    # Mood diff = 0.35*(1.0 - 0.7) = 0.105
    assert abs((score_exact - score_related) - 0.35 * (1.0 - 0.7)) < 1e-9


# ---------------------------------------------------------------------------
# 12. score_song: unknown mood in table defaults to 0.0, no KeyError raised
# ---------------------------------------------------------------------------

def test_score_song_unknown_mood_does_not_raise():
    prefs = {"favorite_genre": "pop", "favorite_mood": "unknown_mood_xyz", "target_energy": 0.8, "likes_acoustic": False}
    song  = {"genre": "pop", "mood": "happy", "energy": 0.8, "acousticness": 0.0}

    score, reasons = score_song(prefs, song)
    assert isinstance(score, float)
    assert score >= 0.0
    assert any("doesn't really match" in r for r in reasons)


# ---------------------------------------------------------------------------
# 13. score_song: unknown genre in table defaults to 0.0, no KeyError raised
# ---------------------------------------------------------------------------

def test_score_song_unknown_genre_does_not_raise():
    prefs = {"favorite_genre": "unknown_genre_xyz", "favorite_mood": "happy", "target_energy": 0.8, "likes_acoustic": False}
    song  = {"genre": "pop", "mood": "happy", "energy": 0.8, "acousticness": 0.0}

    score, reasons = score_song(prefs, song)
    assert isinstance(score, float)
    assert score >= 0.0
    assert any("outside your usual style" in r for r in reasons)


# ---------------------------------------------------------------------------
# 14. score_song: exact energy match gives full Gaussian contribution (0.25)
# ---------------------------------------------------------------------------

def test_score_song_energy_exact_match_full_gaussian():
    # Use unknown genre/mood so those contribute 0; acousticness=1.0 with likes_acoustic=False → 0
    prefs = {"favorite_genre": "unknown_x", "favorite_mood": "unknown_y", "target_energy": 0.5, "likes_acoustic": False}
    song  = {"genre": "unknown_x", "mood": "unknown_y", "energy": 0.5, "acousticness": 1.0}

    score, _ = score_song(prefs, song)
    assert abs(score - 0.25) < 1e-9


# ---------------------------------------------------------------------------
# 15. score_song: acousticness preference respected in both directions
# ---------------------------------------------------------------------------

def test_score_song_acousticness_matches_user_preference():
    base = {"favorite_genre": "pop", "favorite_mood": "happy", "target_energy": 0.8}
    acoustic_song     = {"genre": "pop", "mood": "happy", "energy": 0.8, "acousticness": 1.0}
    electronic_song   = {"genre": "pop", "mood": "happy", "energy": 0.8, "acousticness": 0.0}

    score_wants_acoustic, _    = score_song({**base, "likes_acoustic": True},  acoustic_song)
    score_wants_electronic, _  = score_song({**base, "likes_acoustic": False}, acoustic_song)
    score_electronic_match, _  = score_song({**base, "likes_acoustic": False}, electronic_song)

    # Acoustic song scores higher when user likes acoustic
    assert score_wants_acoustic > score_wants_electronic
    # Electronic song scores highest for user who wants electronic
    assert score_electronic_match > score_wants_electronic
