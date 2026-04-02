"""
Command line runner for the Music Recommender Simulation.

This file helps you quickly run and test your recommender.

You will implement the functions in recommender.py:
- load_songs
- score_song
- recommend_songs
"""

import os
from recommender import load_songs, recommend_songs

DATA_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "songs.csv")


def main() -> None:
    songs = load_songs(DATA_PATH)
    print(f"Loaded songs: {len(songs)}")

    # Taste profile — keys match UserProfile fields in recommender.py exactly.
    user_prefs = {
        "favorite_genre":  "lofi",   # categorical, looked up in GENRE_SIMILARITY
        "favorite_mood":   "chill",  # categorical, looked up in MOOD_SIMILARITY
        "target_energy":   0.40,     # 0–1 float, scored with Gaussian proximity
        "likes_acoustic":  True,     # bool: prefers organic/acoustic over electronic
    }

    recommendations = recommend_songs(user_prefs, songs, k=5)

    print("\nTop recommendations:\n")
    for rec in recommendations:
        # You decide the structure of each returned item.
        # A common pattern is: (song, score, explanation)
        song, score, explanation = rec
        print(f"Title: {song['title']:<30} Score: {score:.2f}")
        print(f"Reasons: {explanation}")
        print()


if __name__ == "__main__":
    main()
