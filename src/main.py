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

USERS = {
    "Chill Lofi": {
        "favorite_genre": "lofi",
        "favorite_mood":  "chill",
        "target_energy":  0.40,
        "likes_acoustic": True,
    },
    "High-Energy Pop": {
        "favorite_genre": "pop",
        "favorite_mood":  "happy",
        "target_energy":  0.80,
        "likes_acoustic": False,
    },
    "Deep Intense Rock": {
        "favorite_genre": "rock",
        "favorite_mood":  "intense",
        "target_energy":  0.90,
        "likes_acoustic": False,
    },

    # --- ADVERSARIAL / EDGE CASE PROFILES ---

    # sad→aggressive = 0.0, so mood contributes nothing (35% weight zeroed out).
    # genre+energy (50%) dominate — expect "Shattered Glass" to rank high
    # despite being the emotional opposite of what was requested.
    "Sad Headbanger": {
        "favorite_genre": "metal",
        "favorite_mood":  "sad",
        "target_energy":  0.97,
        "likes_acoustic": False,
    },


    # likes_acoustic=True conflicts with target_energy=0.90 — every high-energy
    # song in the catalog has near-zero acousticness and vice versa.
    # The 15% acoustic weight is overwhelmed; expect acoustic_score ≈ 0.006.
    "Acoustic Headbanger": {
        "favorite_genre": "rock",
        "favorite_mood":  "intense",
        "target_energy":  0.90,
        "likes_acoustic": True,
    },

    # target_energy=0.385 is equidistant from Library Rain (0.35) and
    # Midnight Coding (0.42) — both perfect lofi/chill matches.
    # Acousticness becomes the only tiebreaker, acting as a hidden ranking signal.
    "Lofi Minimalist": {
        "favorite_genre": "lofi",
        "favorite_mood":  "chill",
        "target_energy":  0.385,
        "likes_acoustic": False,
    },

    # romantic→aggressive = 0.0, low energy, and likes_acoustic=True all point
    # away from metal. Expect "Ivory Rain" (classical) to beat "Shattered Glass"
    # (~0.52 vs ~0.26) — genre alone (25%) loses to three aligned dimensions.
    "Romantic Metalhead": {
        "favorite_genre": "metal",
        "favorite_mood":  "romantic",
        "target_energy":  0.30,
        "likes_acoustic": True,
    },

    # serene→energetic = 0.0: no high-energy song earns mood credit, no serene
    # song can match target_energy=0.90. The system must choose between a mood
    # match with wrong energy or an energy match with zero mood score.
    "Tired Raver": {
        "favorite_genre": "electronic",
        "favorite_mood":  "serene",
        "target_energy":  0.90,
        "likes_acoustic": False,
    },

    # target_energy=1.0 is the hard ceiling — the Gaussian is asymmetric here.
    # "Shattered Glass" (energy=0.97) may beat "Gym Hero" (energy=0.93) because
    # a 0.04 energy edge outweighs the genre gap, surfacing metal for a pop fan.
    "Max Energy Seeker": {
        "favorite_genre": "pop",
        "favorite_mood":  "intense",
        "target_energy":  1.0,
        "likes_acoustic": False,
    },
}


def print_recommendations(label: str, recommendations) -> None:
    print(f"\n{'='*50}")
    print(f"User Profile: {label}")
    print(f"{'='*50}")
    for song, score, explanation in recommendations:
        print(f"Title: {song['title']:<30} Score: {score:.2f}")
        print(f"Reasons: {explanation}")
        print()

def main() -> None:
    songs = load_songs(DATA_PATH)
    print(f"Loaded songs: {len(songs)}")

    for label, user_prefs in USERS.items():
        recommendations = recommend_songs(user_prefs, songs, k=5)
        print_recommendations(label, recommendations)


if __name__ == "__main__":
    main()
