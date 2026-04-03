# 🎧 Model Card: Music Recommender Simulation

## 1. Model Name  

MoodLense 1.0
---

## 2. Intended Use    

MoodLense 1.0 is a content-based filtering model that suggests songs from a catalog based on four listener preferences: favourite genre, favourite mood, how energetic they want the music to feel, and whether they prefer acoustic or electronic sounds. It assumes the user taste can be described in those four terms and that those preferences stay constant — it does not learn overtime. This is a classroom simulation built to explore how scoring logic works and where it breaks down.

---

## 3. How the Model Works  

Explain your scoring approach in simple language.  

Prompts:  

- What features of each song are used (genre, energy, mood, etc.)  
- What user preferences are considered  
- How does the model turn those into a score  
- What changes did you make from the starter logic  

Avoid code here. Pretend you are explaining the idea to a friend who does not program.

Each song is described and evaluated by four  qualities: its genre (like lofi or metal), its mood (like chill or intense), an energy level on a scale from 0 to 1, and an acousticness score that says how "live and organic" versus "electronic and produced" it sounds.

When a listener comes in, they tell the system their favourite genre, favourite mood, how energetic they want the music, and whether they prefer acoustic or electronic sounds. The system then goes through every song in the catalog and gives it a score based on how well it matches those four preferences.

Mood and genre are not just yes-or-no matches — there are similarity tables that give partial credit for related categories. For example, if you want "chill" music and a song is "relaxed," it scores 70% of the full mood points rather than zero. Energy is scored using a bell curve: songs closest to your target energy score highest, and songs far away score near zero. Acoustic preference is scored as a straight percentage — the more acoustic a song is, the better it scores for someone who wants acoustic, and the worse for someone who does not.

The four component scores are then added up with different weights: mood counts for 35%, genre for 25%, energy for 25%, and acousticness for 15%. The songs with the highest totals are returned as the top recommendations.

The main changes from the starter logic were expanding the mood and genre similarity tables to cover a wider range of categories, and adding more song variety to the catalog to better test edge cases.

The additional change was the implementation of Diversity Penalty feature that penalizes the same artist apearing multiple times in the recommendation list. The feature uses the decay factor that controls how harsh that penalty is: 0.5 halves an artist's score with each repeat. 

---

## 4. Data  

Describe the dataset the model uses.  

Prompts:  

- How many songs are in the catalog  
- What genres or moods are represented  
- Did you add or remove data  
- Are there parts of musical taste missing in the dataset  

The catalog contains 18 songs spanning 15 genres — lofi, pop, rock, ambient, jazz, synthwave, indie pop, soul, metal, country, electronic, r&b, folk, drum and bass, and classical — and 14 moods ranging from chill and serene to aggressive and tense. Songs were added beyond the original starter set to improve genre and mood coverage.

The catalog is intentionally small for a simulation, which creates some gaps. Most genres and moods have only one song each, so when a listener's first-choice genre has no good match, the fallback options are very limited. Energy levels also cluster at the quiet end and the loud end, leaving almost nothing for listeners who want something in the middle. Styles like reggae, hip-hop, blues, and Latin are completely absent, as are moods like nostalgic longing or quiet joy that sit between the defined categories. Real listening taste is much more varied and personal than this dataset can capture.


---

## 5. Strengths  

Where does your system seem to work well  

Prompts:  

- User types for which it gives reasonable results  
- Any patterns you think your scoring captures correctly  
- Cases where the recommendations matched your intuition  

The system works best for listeners with clear, well-represented preferences. When a listener's genre and mood both have good catalog coverage, the scoring feels natural and the top result is a good match.

The partial credit system for related moods and genres also behaves sensibly in most cases. A lofi fan correctly gets ambient and jazz suggestions as runner-ups rather than something completely unrelated like metal.  

The bell curve for energy means small differences near the target barely affect the score, which prevents the system from being overly harsh about songs that are close but not exact — that feels right for how people actually listen.

---

## 6. Limitations and Bias 

Where the system struggles or behaves unfairly. 

Prompts:  

- Features it does not consider  
- Genres or moods that are underrepresented  
- Cases where the system overfits to one preference  
- Ways the scoring might unintentionally favor some users  

The system only knows four things about a listener — genre, mood, energy, and acoustic preference. It has no awareness of tempo, lyrics, language, listening history, time of day, or whether the listener wants something familiar or something new. Two songs can score identically and be nothing alike in practice.

Entire styles of music are missing from the catalog. Reggae, hip-hop, blues, Latin, and many others have no representation, so listeners whose taste lives in those areas will always get mismatched results. Even within represented genres, most have only one song, meaning the system runs out of good options quickly and fills the remaining slots with loosely related alternatives.

Some moods like aggressive or sad connect to very few others, so if the one matching song is not quite right, the remaining recommendations feel unrelated. Listeners who prefer moods like happy or intense connect to many more songs and naturally get better results.

The acoustic preference is weighted at only 15%, which is not enough to override mood and energy when they point in a different direction. In practice, a listener who specifically wants acoustic music will often receive electronic-sounding recommendations because the other dimensions outweigh that preference. 

The system also has no way to penalise a song for appearing too often — so one song with broadly average qualities can end up recommended to almost every listener regardless of how different their tastes are.

---

## 7. Evaluation  

How you checked whether the recommender behaved as expected. 

Prompts:  

- Which user profiles you tested  
- What you looked for in the recommendations  
- What surprised you  
- Any simple tests or comparisons you ran  

No need for numeric metrics unless you created some.

**Which user profiles you tested**
We tested three typical listeners — someone who likes calm lo-fi music, a pop fan who wants upbeat songs, and a rock fan who wants intense music. Then we created six "tricky" listeners on purpose: someone who wants sad music but at very high energy, someone who likes acoustic instruments but also wants high-energy songs, a metal fan who wants romantic music, and a few others where the preferences intentionally contradict each other or push the system to its limits.

**What you looked for in the recommendations**
We checked whether the songs the system suggested actually matched what each listener asked for — right genre, right mood, right energy level. We also checked whether the scores made sense: the #1 recommendation should score noticeably higher than #5, not just win by a tiny margin.

**What surprised you**
One song — Gym Hero — kept showing up for almost every listener, even ones who asked for completely different genres like metal or electronic. It won by being "good enough" at everything rather than perfect for anyone. We also found that when a listener's preferences conflicted (like wanting calm but high-energy), the system quietly ignored whichever preference carried less mathematical weight. A self-described metal fan received a classical music recommendation as their top result.

**Any simple tests or comparisons you ran**
We ran the program and manually counted how many times each song appeared across all nine top-five lists to spot which songs dominated.  We also hand-calculated approximate scores for a few specific cases — like the Romantic Metalhead — to verify whether the numbers matched what the output showed.
---

## 8. Future Work  

Ideas for how you would improve the model next.  

Prompts:  

- Additional features or preferences  
- Better ways to explain recommendations  
- Improving diversity among the top results  
- Handling more complex user tastes  

Adding more song attributes would make matching more precise — tempo, danceability, and valence are already in the dataset but currently unused. Letting listeners rank their preferences (for example, "mood matters more to me than genre") would also help instead of applying the same fixed weights to everyone.

$CURSOR$[Completed in Updated Version] ✅ Artist Diversity Feature Implemented ~~The diversity problem could be addressed by adding a rule that penalises a song slightly if something very similar has already been selected — so the top 5 feels varied rather than clustered around one corner of the catalog.~~

$CURSOR$[Completed in Updated Version] ✅ Friendly Explanations & Tabulate Display Implemented ~~Explanations could be friendlier. Instead of showing raw numbers, the system could say something like "this song matches your mood perfectly and is close to your energy target" in plain language.~~

For more complex tastes, the system could allow multiple moods or genres rather than just one of each — for example, someone who listens to both jazz and lo-fi, or wants something that is both focused and a little melancholic.

---

## 9. Personal Reflection  

A few sentences about your experience.  

Prompts:  

- What you learned about recommender systems  
- Something unexpected or interesting you discovered  
- How this changed the way you think about music recommendation apps  

I learned that there are different types of recommender systems — content-based and collaborative. I was surprised by how many factors shape what gets recommended: the weights, how preferences are defined, how data is labelled and processed. Small changes in any of those can change the results completely. It made me think differently about the apps I use every day and how much is happening behind something that feels effortless.
