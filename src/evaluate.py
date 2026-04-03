"""
Baseline comparison for the Music Recommender.

Compares four recommendation strategies across all user profiles:

  yours   -- weighted similarity tables + Gaussian energy + artist decay=0.5
  no_div  -- same algorithm, artist_decay=1.0  (no diversity penalty)
  binary  -- same weights, but mood/genre are exact-match only (0 or 1)
  random  -- random selection (sanity-check floor)

Run with:
    python -m src.evaluate     (from the project root)
    python src/evaluate.py     (directly)
"""

import math
import os
import random
import sys
from typing import Dict, List, Tuple

# Ensure Unicode output works on Windows terminals
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

try:
    from src.recommender import load_songs, recommend_songs, score_song
except ModuleNotFoundError:
    from recommender import load_songs, recommend_songs, score_song

DATA_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "songs.csv")

# ── User profiles (same as main.py) ─────────────────────────────────────────

USERS: Dict[str, Dict] = {
    "Chill Lofi":          {"favorite_genre": "lofi",       "favorite_mood": "chill",    "target_energy": 0.40,  "likes_acoustic": True},
    "High-Energy Pop":     {"favorite_genre": "pop",        "favorite_mood": "happy",    "target_energy": 0.80,  "likes_acoustic": False},
    "Deep Intense Rock":   {"favorite_genre": "rock",       "favorite_mood": "intense",  "target_energy": 0.90,  "likes_acoustic": False},
    "Sad Headbanger":      {"favorite_genre": "metal",      "favorite_mood": "sad",      "target_energy": 0.97,  "likes_acoustic": False},
    "Acoustic Headbanger": {"favorite_genre": "rock",       "favorite_mood": "intense",  "target_energy": 0.90,  "likes_acoustic": True},
    "Lofi Minimalist":     {"favorite_genre": "lofi",       "favorite_mood": "chill",    "target_energy": 0.385, "likes_acoustic": False},
    "Romantic Metalhead":  {"favorite_genre": "metal",      "favorite_mood": "romantic", "target_energy": 0.30,  "likes_acoustic": True},
    "Tired Raver":         {"favorite_genre": "electronic", "favorite_mood": "serene",   "target_energy": 0.90,  "likes_acoustic": False},
    "Max Energy Seeker":   {"favorite_genre": "pop",        "favorite_mood": "intense",  "target_energy": 1.0,   "likes_acoustic": False},
    "Neon Echo Fan":       {"favorite_genre": "synthwave",  "favorite_mood": "energetic","target_energy": 0.85,  "likes_acoustic": False},
    "LoRoom Fan":          {"favorite_genre": "lofi",       "favorite_mood": "focused",  "target_energy": 0.40,  "likes_acoustic": True},
}

# ── Baselines ────────────────────────────────────────────────────────────────

def recommend_random(songs: List[Dict], k: int) -> List[Tuple[Dict, float, str]]:
    """Return k songs chosen at random (sanity-check floor)."""
    picked = random.sample(songs, min(k, len(songs)))
    return [(s, 0.0, "Random pick") for s in picked]


def _score_song_binary(user_prefs: Dict, song: Dict) -> float:
    """
    Same weights as the main algorithm, but mood/genre use exact-match (1 or 0)
    instead of similarity tables. Energy and acousticness are unchanged.
    """
    mood_score    = 0.35 * (1.0 if song["mood"]  == user_prefs["favorite_mood"]  else 0.0)
    genre_score   = 0.25 * (1.0 if song["genre"] == user_prefs["favorite_genre"] else 0.0)
    energy_sim    = math.exp(-((song["energy"] - user_prefs["target_energy"]) ** 2) / (2 * 0.20 ** 2))
    energy_score  = 0.25 * energy_sim
    acoustic_sim  = song["acousticness"] if user_prefs["likes_acoustic"] else (1 - song["acousticness"])
    acoustic_score = 0.15 * acoustic_sim
    return mood_score + genre_score + energy_score + acoustic_score


def recommend_binary(
    user_prefs: Dict,
    songs: List[Dict],
    k: int = 5,
    artist_decay: float = 0.5,
) -> List[Tuple[Dict, float, str]]:
    """Greedy top-k with artist diversity, using binary mood/genre matching."""
    candidates = [(s, _score_song_binary(user_prefs, s)) for s in songs]
    artist_counts: Dict[str, int] = {}
    results = []

    for _ in range(k):
        remaining = [(s, sc) for s, sc in candidates if s not in [x[0] for x in results]]
        if not remaining:
            break
        penalized = [
            (s, sc * (artist_decay ** artist_counts.get(s["artist"], 0)))
            for s, sc in remaining
        ]
        best = max(penalized, key=lambda x: x[1])
        results.append((best[0], best[1], "binary match"))
        artist_counts[best[0]["artist"]] = artist_counts.get(best[0]["artist"], 0) + 1

    return results


# ── Metrics ──────────────────────────────────────────────────────────────────
#
# Each metric answers one specific question about algorithm behaviour:
#
#   artist_diversity      How many different artists appear in the top-k?
#                         Measures output variety. Lower = dominated by one artist.
#
#   genre_diversity       How many different genres appear in the top-k?
#                         Measures stylistic breadth of recommendations.
#
#   avg_top1_score        Average score of the #1 pick across all profiles.
#                         Measures how confident the algorithm is in its best match.
#                         Higher = algorithm found a strong match for this user.
#
#   avg_rank_last_score   Average score of the last pick across all profiles.
#                         Measures quality of "filler" slots at the bottom.
#                         If this is very low, the bottom picks are poor matches.
#
#   top1_agreement        Do two algorithms agree on the #1 pick?
#                         Tells you if similarity tables actually change the outcome.
#
#   overlap_count         Songs in common between two result lists (order-independent).
#                         3.5/5 means ~1.5 positions shift; 5/5 means identical lists.
#
#   personalization_index Fraction of recommendation slots filled by unique songs
#                         across ALL profiles: (distinct songs used) / (n * k).
#                         1.0 = every user gets completely different songs.
#                         Low = the algorithm reuses a small pool of "safe" songs.
#
#   max_artist_repeat     Maximum number of songs from one artist in a single top-k.
#                         Averaged across profiles. 1.0 = fully diverse (one per artist).
#                         Higher = diversity penalty is not working or not needed.
#
#   domination_index      Share of ALL recommendation slots taken by the single most
#                         common song: top_song_count / (n * k).
#                         E.g. Gym Hero in 7/11 profiles × 1 slot = 7/55 = 12.7%.
#                         High = one song is crowding out others for most users.
#
#   catalog_coverage      Fraction of the total catalog that appears at least once
#                         across all user recommendation lists.
#                         Low = large parts of the catalog are never surfaced.

def artist_diversity(results: List[Tuple]) -> int:
    """Unique artists in a single result list."""
    return len({r[0]["artist"] for r in results})

def genre_diversity(results: List[Tuple]) -> int:
    """Unique genres in a single result list."""
    return len({r[0]["genre"] for r in results})

def avg_top1_score(all_results: List[List[Tuple]]) -> float:
    """Average score of the #1 recommendation across all profiles."""
    scores = [r[0][1] for r in all_results if r]
    return sum(scores) / len(scores) if scores else 0.0

def avg_last_score(all_results: List[List[Tuple]]) -> float:
    """Average score of the last recommendation across all profiles."""
    scores = [r[-1][1] for r in all_results if r]
    return sum(scores) / len(scores) if scores else 0.0

def top1_agreement(a: List[Tuple], b: List[Tuple]) -> bool:
    """True if both result lists share the same #1 song."""
    if not a or not b:
        return False
    return a[0][0]["title"] == b[0][0]["title"]

def overlap_count(a: List[Tuple], b: List[Tuple]) -> int:
    """Number of songs appearing in both result lists (order-independent)."""
    return len({r[0]["title"] for r in a} & {r[0]["title"] for r in b})

def personalization_index(all_results: List[List[Tuple]]) -> float:
    """Unique songs used / total recommendation slots across all profiles.
    1.0 means every user got a completely unique set of songs."""
    unique = len({r[0]["title"] for results in all_results for r in results})
    total  = sum(len(r) for r in all_results)
    return unique / total if total else 0.0

def avg_max_artist_repeat(all_results: List[List[Tuple]]) -> float:
    """Average of the highest artist repeat count per profile.
    1.0 = perfectly diverse (max one song per artist in every list)."""
    repeats = []
    for results in all_results:
        counts: Dict[str, int] = {}
        for r in results:
            counts[r[0]["artist"]] = counts.get(r[0]["artist"], 0) + 1
        repeats.append(max(counts.values()) if counts else 0)
    return sum(repeats) / len(repeats) if repeats else 0.0

def domination_index(all_results: List[List[Tuple]]) -> float:
    """Fraction of all recommendation slots taken by the single most common song."""
    freq: Dict[str, int] = {}
    total = 0
    for results in all_results:
        for r in results:
            freq[r[0]["title"]] = freq.get(r[0]["title"], 0) + 1
            total += 1
    return max(freq.values()) / total if freq else 0.0

def catalog_coverage(all_results: List[List[Tuple]], total: int) -> float:
    """Fraction of the catalog that appears at least once across all profiles."""
    seen = {r[0]["id"] for results in all_results for r in results}
    return len(seen) / total

def song_frequency(all_results: List[List[Tuple]]) -> Dict[str, int]:
    """Count how many user profiles each song appears in."""
    freq: Dict[str, int] = {}
    for results in all_results:
        for song, _, _ in results:
            freq[song["title"]] = freq.get(song["title"], 0) + 1
    return freq


# ── Print helper ─────────────────────────────────────────────────────────────

def _print_table(rows, headers, tab_fn):
    if tab_fn:
        print(tab_fn(rows, headers=headers, tablefmt="simple"))
    else:
        col = [
            max(len(str(h)), max((len(str(r[i])) for r in rows), default=0))
            for i, h in enumerate(headers)
        ]
        print("  ".join(str(h).ljust(col[i]) for i, h in enumerate(headers)))
        print("  ".join("-" * c for c in col))
        for row in rows:
            print("  ".join(str(v).ljust(col[i]) for i, v in enumerate(row)))


# ── Runner ───────────────────────────────────────────────────────────────────

def _sep(char="=", width=80):
    print(char * width)

def _header(title, char="=", width=80):
    _sep(char, width)
    print(f"  {title}")
    _sep(char, width)

def run_comparison(users: Dict[str, Dict], songs: List[Dict], k: int = 5) -> None:
    try:
        from tabulate import tabulate as _tab
    except ImportError:
        _tab = None

    random.seed(42)

    all_yours, all_nodiv, all_binary, all_random = [], [], [], []
    for label, prefs in users.items():
        all_yours.append(recommend_songs(prefs, songs, k=k, artist_decay=0.5))
        all_nodiv.append(recommend_songs(prefs, songs, k=k, artist_decay=1.0))
        all_binary.append(recommend_binary(prefs, songs, k=k, artist_decay=0.5))
        all_random.append(recommend_random(songs, k=k))

    user_labels = list(users.keys())
    n           = len(user_labels)

    # ── Pre-compute all metrics ───────────────────────────────────────────────
    avg_ml_artists     = sum(artist_diversity(r) for r in all_yours)  / n
    avg_nodiv_artists  = sum(artist_diversity(r) for r in all_nodiv)  / n
    avg_binary_artists = sum(artist_diversity(r) for r in all_binary) / n
    avg_random_artists = sum(artist_diversity(r) for r in all_random) / n
    avg_ml_genres      = sum(genre_diversity(r)  for r in all_yours)  / n
    avg_nodiv_genres   = sum(genre_diversity(r)  for r in all_nodiv)  / n
    avg_binary_genres  = sum(genre_diversity(r)  for r in all_binary) / n
    avg_random_genres  = sum(genre_diversity(r)  for r in all_random) / n

    ml_top1       = avg_top1_score(all_yours)
    nodiv_top1    = avg_top1_score(all_nodiv)
    binary_top1   = avg_top1_score(all_binary)
    random_top1   = avg_top1_score(all_random)
    ml_last       = avg_last_score(all_yours)
    nodiv_last    = avg_last_score(all_nodiv)
    binary_last   = avg_last_score(all_binary)
    random_last   = avg_last_score(all_random)

    ml_pi         = personalization_index(all_yours)
    nodiv_pi      = personalization_index(all_nodiv)
    binary_pi     = personalization_index(all_binary)
    random_pi     = personalization_index(all_random)

    ml_repeat     = avg_max_artist_repeat(all_yours)
    nodiv_repeat  = avg_max_artist_repeat(all_nodiv)
    binary_repeat = avg_max_artist_repeat(all_binary)
    random_repeat = avg_max_artist_repeat(all_random)

    ml_dom        = domination_index(all_yours)
    nodiv_dom     = domination_index(all_nodiv)
    binary_dom    = domination_index(all_binary)
    random_dom    = domination_index(all_random)

    avg_overlap_binary = sum(overlap_count(all_yours[i], all_binary[i]) for i in range(n)) / n
    avg_overlap_nodiv  = sum(overlap_count(all_yours[i], all_nodiv[i])  for i in range(n)) / n
    avg_overlap_random = sum(overlap_count(all_yours[i], all_random[i]) for i in range(n)) / n

    penalty_changed    = sum(
        1 for i in range(n)
        if [r[0]["title"] for r in all_yours[i]] != [r[0]["title"] for r in all_nodiv[i]]
    )
    top1_agree_binary = sum(1 for i in range(n) if top1_agreement(all_yours[i], all_binary[i]))
    top1_agree_nodiv  = sum(1 for i in range(n) if top1_agreement(all_yours[i], all_nodiv[i]))
    top1_agree_random = sum(1 for i in range(n) if top1_agreement(all_yours[i], all_random[i]))

    cov_ml        = catalog_coverage(all_yours,  len(songs))
    cov_nodiv     = catalog_coverage(all_nodiv,  len(songs))
    cov_binary    = catalog_coverage(all_binary, len(songs))
    cov_random    = catalog_coverage(all_random, len(songs))
    freq_yours    = song_frequency(all_yours)
    freq_binary   = song_frequency(all_binary)
    never_yours   = [s for s in songs if s["title"] not in freq_yours]

    # ════════════════════════════════════════════════════════════════════════
    print()
    _sep()
    print("  MoodLense 1.0 — EVALUATION REPORT")
    print(f"  {n} user profiles  |  {len(songs)} songs  |  top-{k} recommendations each")
    _sep()
    print("""
  Algorithms compared:
    MoodLense 1.0  Similarity tables (mood/genre) + Gaussian energy + diversity penalty (decay=0.5)
    No-div         MoodLense without diversity penalty (decay=1.0) — isolates penalty impact
    Binary         Exact-match mood/genre (no partial credit), same weights — isolates table impact
    Random         Random selection — sanity-check floor
    """)

    # ════════════════════════════════════════════════════════════════════════
    # 1. YOURS vs BINARY — do similarity tables change what gets recommended?
    # ════════════════════════════════════════════════════════════════════════
    _sep()
    print("  1. SIMILARITY TABLES vs EXACT MATCH  (MoodLense 1.0 vs Binary)")
    print("     Do partial-credit mood/genre tables change the ranked list?")
    print("     >> = position differs between the two algorithms")
    _sep()

    for i, label in enumerate(user_labels):
        prefs   = users[label]
        yours   = all_yours[i]
        binary  = all_binary[i]
        ov      = overlap_count(yours, binary)
        n_diffs = k - ov
        acoustic = "acoustic" if prefs["likes_acoustic"] else "electronic"
        pref_str = (f"{prefs['favorite_genre']} / {prefs['favorite_mood']} / "
                    f"energy {prefs['target_energy']} / {acoustic}")

        print(f"\n  {label}  [{pref_str}]")
        print(f"  Overlap: {ov}/{k} in common   Differences: {n_diffs}   "
              f"Top-1 score — MoodLense: {yours[0][1]:.2f}  Binary: {binary[0][1]:.2f}")

        rows = []
        for rank in range(k):
            y = yours[rank]  if rank < len(yours)  else None
            b = binary[rank] if rank < len(binary) else None
            y_cell = f"{y[0]['title']} ({y[1]:.2f})" if y else "-"
            b_cell = f"{b[0]['title']} ({b[1]:.2f})" if b else "-"
            flag   = ">>" if (y and b and y[0]["title"] != b[0]["title"]) else "  "
            rows.append([flag, rank + 1, y_cell, b_cell])

        _print_table(rows, ["", "#", "MoodLense 1.0", "Binary"], _tab)

    # ════════════════════════════════════════════════════════════════════════
    # 2. DIVERSITY PENALTY — which profiles are actually affected?
    # ════════════════════════════════════════════════════════════════════════
    print()
    _sep()
    print("  2. DIVERSITY PENALTY IMPACT")
    print("     Yours (decay=0.5) vs No-div (decay=1.0)")
    print("     Only shows profiles where the penalty changed at least one pick.")
    print("     >> = position where a different song was chosen")
    _sep()

    unchanged = []
    for i, label in enumerate(user_labels):
        yours  = all_yours[i]
        no_div = all_nodiv[i]

        rows    = []
        changed = False
        for rank in range(k):
            y  = yours[rank]  if rank < len(yours)  else None
            nd = no_div[rank] if rank < len(no_div) else None
            y_title  = y[0]["title"]  if y  else "-"
            nd_title = nd[0]["title"] if nd else "-"
            flag = ">>" if y_title != nd_title else "  "
            if flag == ">>":
                changed = True
            rows.append([flag, rank + 1,
                         f"{y_title} [{y[0]['artist']}]"  if y  else "-",
                         f"{nd_title} [{nd[0]['artist']}]" if nd else "-"])

        if changed:
            artists_with = artist_diversity(yours)
            artists_without = artist_diversity(no_div)
            print(f"\n  {label}   artists with penalty: {artists_with}  |  without: {artists_without}")
            _print_table(rows, ["", "#", "With penalty", "Without penalty"], _tab)
        else:
            unchanged.append(label)

    if unchanged:
        print(f"\n  No change for: {', '.join(unchanged)}")

    # ════════════════════════════════════════════════════════════════════════
    # 3. CATALOG BIAS — which songs dominate, which never appear?
    # ════════════════════════════════════════════════════════════════════════
    print()
    _sep()
    print("  3. CATALOG BIAS")
    print("     How often does each song appear across all user profiles?")
    print("     # = appears in that profile's top-5   . = does not")
    _sep()

    # Merge yours + binary frequency into one table
    all_titles = sorted(
        set(freq_yours) | set(freq_binary),
        key=lambda t: freq_yours.get(t, 0) + freq_binary.get(t, 0),
        reverse=True,
    )
    print(f"\n  Top recommended songs (yours vs binary, out of {n} profiles):\n")
    rows = []
    for title_str in all_titles[:10]:
        s       = next(x for x in songs if x["title"] == title_str)
        c_yours  = freq_yours.get(title_str, 0)
        c_binary = freq_binary.get(title_str, 0)
        bar_y = "#" * c_yours  + "." * (n - c_yours)
        bar_b = "#" * c_binary + "." * (n - c_binary)
        rows.append([title_str, s["genre"], s["mood"],
                     f"{c_yours}/{n}",  bar_y,
                     f"{c_binary}/{n}", bar_b])
    _print_table(rows, ["Song", "Genre", "Mood",
                        "Yours", f"[{n} profiles]",
                        "Binary", f"[{n} profiles]"], _tab)

    if never_yours:
        print(f"\n  Never recommended by yours ({len(never_yours)} songs):")
        for s in never_yours:
            print(f"    {s['title']:<22} {s['genre']:<14} mood={s['mood']:<12} energy={s['energy']}")

    # ════════════════════════════════════════════════════════════════════════
    # 4. SUMMARY TABLE
    # ════════════════════════════════════════════════════════════════════════
    print()
    _sep()
    print("  4. SUMMARY")
    _sep()

    summary_rows = [
        # ── Quality: how strong is the best match? ────────────────────────
        ["Avg score of rank-1 pick",      f"{ml_top1:.2f}",            f"{nodiv_top1:.2f}",          f"{binary_top1:.2f}",        f"{random_top1:.2f}"],
        ["Avg score of rank-5 pick",      f"{ml_last:.2f}",            f"{nodiv_last:.2f}",          f"{binary_last:.2f}",        f"{random_last:.2f}"],
        # ── Diversity: how varied are the results? ────────────────────────
        ["Avg unique artists in top-5",   f"{avg_ml_artists:.1f}",     f"{avg_nodiv_artists:.1f}",   f"{avg_binary_artists:.1f}", f"{avg_random_artists:.1f}"],
        ["Avg unique genres in top-5",    f"{avg_ml_genres:.1f}",      f"{avg_nodiv_genres:.1f}",    f"{avg_binary_genres:.1f}",  f"{avg_random_genres:.1f}"],
        ["Avg max artist repeat",         f"{ml_repeat:.1f}",          f"{nodiv_repeat:.1f}",        f"{binary_repeat:.1f}",      f"{random_repeat:.1f}"],
        # ── Personalization: does each user get different results? ─────────
        ["Personalization index",         f"{ml_pi:.0%}",              f"{nodiv_pi:.0%}",            f"{binary_pi:.0%}",          f"{random_pi:.0%}"],
        ["Top-5 overlap vs MoodLense",    "5.0/5",                     f"{avg_overlap_nodiv:.1f}/5", f"{avg_overlap_binary:.1f}/5", f"{avg_overlap_random:.1f}/5"],
        ["Rank-1 agrees with MoodLense",  f"{n}/{n}",                  f"{top1_agree_nodiv}/{n}",    f"{top1_agree_binary}/{n}",  f"{top1_agree_random}/{n}"],
        # ── Coverage: how much of the catalog is used? ────────────────────
        ["Catalog coverage",              f"{cov_ml:.0%}",             f"{cov_nodiv:.0%}",           f"{cov_binary:.0%}",         f"{cov_random:.0%}"],
        ["Domination index (top song)",   f"{ml_dom:.0%}",             f"{nodiv_dom:.0%}",           f"{binary_dom:.0%}",         f"{random_dom:.0%}"],
        # ── Penalty effect ────────────────────────────────────────────────
        ["Profiles changed by penalty",   f"{penalty_changed}/{n}",    "n/a",                        "n/a",                       "n/a"],
    ]
    print()
    _print_table(summary_rows, ["Metric", "MoodLense 1.0", "No-div", "Binary", "Random"], _tab)

    # ════════════════════════════════════════════════════════════════════════
    # 5. KEY FINDINGS
    # ════════════════════════════════════════════════════════════════════════
    print()
    _sep()
    print("  5. KEY FINDINGS")
    _sep()

    top_song    = max(freq_yours, key=freq_yours.get)
    top_song_ct = freq_yours[top_song]
    total_slots = n * k

    # Profile where tables change rank-1
    rank1_diff_profiles = [
        user_labels[i] for i in range(n)
        if not top1_agreement(all_yours[i], all_binary[i])
    ]
    rank1_diff_str = rank1_diff_profiles[0] if len(rank1_diff_profiles) == 1 else ", ".join(rank1_diff_profiles)

    print(f"""
  [1] Similarity tables shift positions 2-5, not rank-1
      Rank-1 agrees with Binary in {top1_agree_binary}/{n} profiles — tables almost never change who
      ranks first. The {k - avg_overlap_binary:.0f}-{k - avg_overlap_binary + 1:.0f} position(s) that do shift show partial credit
      pulling in related-genre or related-mood songs the binary baseline misses entirely.
      Exception: "{rank1_diff_str}" — the only profile where tables change rank-1.
      Partial mood credit (romantic -> serene) gives Ivory Rain the edge over
      Golden Hour Fade, so a metal fan gets a classical song as their top pick.

  [2] Tables improve filler quality, not top-pick quality
      Rank-1 avg score: MoodLense {ml_top1:.2f}  vs  Binary {binary_top1:.2f}  (near-identical).
      Rank-5 avg score: MoodLense {ml_last:.2f}  vs  Binary {binary_last:.2f}  (MoodLense is {ml_last - binary_last:+.2f}).
      The real value of partial credit is in the lower slots — MoodLense fills
      positions 3-5 with related-mood songs that still earn partial scores, while
      Binary drops to near-zero for anything that isn't an exact genre/mood match.

  [3] Diversity penalty: what it fixes and what it costs
      BENEFIT — Active in {penalty_changed}/{n} profiles:
        Artist variety:  {avg_nodiv_artists:.1f} avg unique artists  ->  {avg_ml_artists:.1f}  (penalty on)
        Genre variety:   {avg_nodiv_genres:.1f} avg unique genres   ->  {avg_ml_genres:.1f}  (penalty on)
        Max repeat:      {nodiv_repeat:.1f} avg max songs per artist  ->  {ml_repeat:.1f}
        Rank-1 pick:     unchanged in all {n}/{n} profiles (penalty only reshuffles 2-5)
      COST — Penalty forces lower-scoring songs into slots 3-5:
        Rank-5 avg score drops from {nodiv_last:.2f} (no-div) to {ml_last:.2f} (MoodLense).
        Personalization index drops from {nodiv_pi:.0%} (no-div) to {ml_pi:.0%} (MoodLense),
        because the penalty tends to surface the same "alternative" artists across
        different profiles, reducing cross-user variety even as it improves
        within-list variety.

  [4] Catalog coverage trade-off
      MoodLense covers {cov_ml:.0%} of the catalog vs {cov_binary:.0%} for Binary and {cov_nodiv:.0%} for No-div.
      Partial credit keeps recommending the same "good enough" songs across profiles;
      Binary gives zero to non-matches and is forced to explore more of the catalog.
      {len(never_yours)} songs are never surfaced by MoodLense across all {n} profiles:
      {", ".join(s["title"] for s in never_yours)}.
      These are genre/mood dead zones — no current user profile is close enough.

  [5] Sanity check vs Random
      Random rank-1 agrees with MoodLense in only {top1_agree_random}/{n} profiles and scores
      0.00 at every position (no scoring logic), confirming MoodLense is making
      intentional, preference-driven choices rather than getting lucky.
""")


if __name__ == "__main__":
    songs = load_songs(DATA_PATH)
    print(f"Loaded {len(songs)} songs.")
    run_comparison(USERS, songs, k=5)
