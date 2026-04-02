# 🎵 Music Recommender Simulation

## Project Summary

In this project you will build and explain a small music recommender system.

Your goal is to:

- Represent songs and a user "taste profile" as data
- Design a scoring rule that turns that data into recommendations
- Evaluate what your system gets right and wrong
- Reflect on how this mirrors real world AI recommenders

Replace this paragraph with your own summary of what your version does.

---

## How The System Works

This system uses **content-based filtering** — it scores songs based on their attributes matched against a user's stored preferences. No other users' behavior is involved.

### Song Features

Each `Song` uses two types of features:

**Categorical** — describe identity and intent:
- `genre` — lofi, pop, rock, ambient, jazz, synthwave
- `mood` — chill, intense, happy, focused, moody, relaxed

**Numeric** — describe sonic character (all normalized to 0–1):
- `energy` — intensity, from calm to driving
- `acousticness` — organic vs. electronic/synthetic
- `valence` — emotional tone, from dark to uplifting
- `danceability` — rhythmic groove and movement

### User Profile

`UserProfile` directly mirrors the song features. It stores the user's preferred values, built by averaging feature values across songs the user has liked or listened to completion:

```
preferred_mood         = "chill"
preferred_genre        = "lofi"
preferred_energy       = 0.75
preferred_acousticness = True 
```

### How the Recommender Scores Each Song

Each song is scored individually against the user profile using two rules:

**Categorical features → similarity table** (partial credit for related categories, not binary 0 or 1):

Mood similarity — adjacent moods get partial credit:

| | chill | relaxed | focused | moody | happy | intense |
|---|---|---|---|---|---|---|
| **chill** | 1.0 | 0.7 | 0.4 | 0.2 | 0.1 | 0.0 |
| **relaxed** | 0.7 | 1.0 | 0.4 | 0.3 | 0.2 | 0.0 |
| **focused** | 0.4 | 0.4 | 1.0 | 0.2 | 0.1 | 0.1 |
| **moody** | 0.2 | 0.3 | 0.2 | 1.0 | 0.0 | 0.2 |
| **happy** | 0.1 | 0.2 | 0.1 | 0.0 | 1.0 | 0.3 |
| **intense** | 0.0 | 0.0 | 0.1 | 0.2 | 0.3 | 1.0 |

Genre similarity — structurally related genres get partial credit:

| | lofi | ambient | jazz | synthwave | pop | rock |
|---|---|---|---|---|---|---|
| **lofi** | 1.0 | 0.6 | 0.4 | 0.2 | 0.1 | 0.0 |
| **ambient** | 0.6 | 1.0 | 0.3 | 0.3 | 0.1 | 0.0 |
| **jazz** | 0.4 | 0.3 | 1.0 | 0.1 | 0.2 | 0.1 |
| **synthwave** | 0.2 | 0.3 | 0.1 | 1.0 | 0.4 | 0.2 |
| **pop** | 0.1 | 0.1 | 0.2 | 0.4 | 1.0 | 0.3 |
| **rock** | 0.0 | 0.0 | 0.1 | 0.2 | 0.3 | 1.0 |

```
mood_score  = MOOD_SIMILARITY[user.preferred_mood][song.mood]
genre_score = GENRE_SIMILARITY[user.preferred_genre][song.genre]
```

**Numeric features → Gaussian proximity** (rewards closeness to the user's preference, not just high or low values):
```
score(feature) = exp( -(song_value - user_preference)² / (2 × 0.20²) )
```
- At distance 0 → score = 1.0 (perfect match)
- Score falls off smoothly as the gap grows
- σ = 0.20 controls how forgiving the system is

**Acousticness → boolean directional score** (`likes_acoustic` is a bool, not a target value):
```
acousticness_score = song.acousticness        if likes_acoustic = True
                   = 1 − song.acousticness    if likes_acoustic = False
```
- `True` → rewards organic/acoustic songs
- `False` → rewards electronic/synthetic songs

**Weighted combination:**
```
total_score = 0.35 × mood_score
            + 0.25 × genre_score
            + 0.25 × energy_score
            + 0.15 × acousticness_score
```

| Feature | Weight | Scoring method | Reason |
|---|---|---|---|
| mood | 0.35 | similarity table | Captures current listening intent; cuts across genres |
| genre | 0.25 | similarity table | Structural sound preference, close behind mood |
| energy | 0.25 | Gaussian (σ = 0.20) | Strongest numeric separator in the dataset |
| acousticness | 0.15 | boolean directional | Cleanly separates organic from electronic |

### How Songs Are Chosen

Once every song has a score, the ranking rule builds the final list:

1. Score every song in the catalog
2. Sort by score descending
3. Enforce diversity — no two consecutive songs with the same genre + mood
4. Break ties by energy proximity
5. Return top N

### Full Flow
<img src="dataflow.png" alt="Dataflow" width="500" />

### Potential Biases

-the system has mood as the highest weight, it will favour songs with right mood over mached genre
-acoustic preference is binary, so it will treat user who slightly likes and who exclusively listens to acoustic music the same
-tempo, danceability, or valence factors are ignored
-fixed user profile


```

---

## Getting Started

### Setup

1. Create a virtual environment (optional but recommended):

   ```bash
   python -m venv .venv
   source .venv/bin/activate      # Mac or Linux
   .venv\Scripts\activate         # Windows

2. Install dependencies

```bash
pip install -r requirements.txt
```

3. Run the app:

```bash
python -m src.main
```

### Running Tests

Run the starter tests with:

```bash
pytest
```

You can add more tests in `tests/test_recommender.py`.

---

## Experiments You Tried

Use this section to document the experiments you ran. For example:

- What happened when you changed the weight on genre from 2.0 to 0.5
- What happened when you added tempo or valence to the score
- How did your system behave for different types of users

---

## Limitations and Risks

Summarize some limitations of your recommender.

Examples:

- It only works on a tiny catalog
- It does not understand lyrics or language
- It might over favor one genre or mood

You will go deeper on this in your model card.

---

## Reflection

Read and complete `model_card.md`:

[**Model Card**](model_card.md)

Write 1 to 2 paragraphs here about what you learned:

- about how recommenders turn data into predictions
- about where bias or unfairness could show up in systems like this


---

## 7. `model_card_template.md`

Combines reflection and model card framing from the Module 3 guidance. :contentReference[oaicite:2]{index=2}  

```markdown
# 🎧 Model Card - Music Recommender Simulation

## 1. Model Name

Give your recommender a name, for example:

> VibeFinder 1.0

---

## 2. Intended Use

- What is this system trying to do
- Who is it for

Example:

> This model suggests 3 to 5 songs from a small catalog based on a user's preferred genre, mood, and energy level. It is for classroom exploration only, not for real users.

---

## 3. How It Works (Short Explanation)

Describe your scoring logic in plain language.

- What features of each song does it consider
- What information about the user does it use
- How does it turn those into a number

Try to avoid code in this section, treat it like an explanation to a non programmer.


The recommender reads your 4 preferences (genre, mood, energy level, and whether you like acoustic music), then goes through every song in the library and gives it a score based on how well it matches. Genre and mood aren't all-or-nothing — "lofi" and "ambient" are close enough to earn partial credit, while "lofi" and "metal" score zero. Energy is scored by how close the song's vibe is to your target. All four scores are combined into one final number per song, the top 5 are picked,

---

## 4. Data

Describe your dataset.

- How many songs are in `data/songs.csv`
- Did you add or remove any songs
- What kinds of genres or moods are represented
- Whose taste does this data mostly reflect

---

## 5. Strengths

Where does your recommender work well

You can think about:
- Situations where the top results "felt right"
- Particular user profiles it served well
- Simplicity or transparency benefits

---

## 6. Limitations and Bias

Where does your recommender struggle

Some prompts:
- Does it ignore some genres or moods
- Does it treat all users as if they have the same taste shape
- Is it biased toward high energy or one genre by default
- How could this be unfair if used in a real product

---

## 7. Evaluation

How did you check your system

Examples:
- You tried multiple user profiles and wrote down whether the results matched your expectations
- You compared your simulation to what a real app like Spotify or YouTube tends to recommend
- You wrote tests for your scoring logic

You do not need a numeric metric, but if you used one, explain what it measures.

---

## 8. Future Work

If you had more time, how would you improve this recommender

Examples:

- Add support for multiple users and "group vibe" recommendations
- Balance diversity of songs instead of always picking the closest match
- Use more features, like tempo ranges or lyric themes

---

## 9. Personal Reflection

A few sentences about what you learned:

- What surprised you about how your system behaved
- How did building this change how you think about real music recommenders
- Where do you think human judgment still matters, even if the model seems "smart"

