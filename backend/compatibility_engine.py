"""Transparent 36-point Ashtakoota matching tables (Muhurta Chintamani convention)."""
from __future__ import annotations
from typing import Any

SIGNS = ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo", "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"]
NAKSHATRAS = ["Ashwini", "Bharani", "Krittika", "Rohini", "Mrigashira", "Ardra", "Punarvasu", "Pushya", "Ashlesha", "Magha", "Purva Phalguni", "Uttara Phalguni", "Hasta", "Chitra", "Swati", "Vishakha", "Anuradha", "Jyeshtha", "Mula", "Purva Ashadha", "Uttara Ashadha", "Shravana", "Dhanishta", "Shatabhisha", "Purva Bhadrapada", "Uttara Bhadrapada", "Revati"]
YONI_ANIMAL = ["Horse", "Elephant", "Sheep", "Serpent", "Serpent", "Dog", "Cat", "Sheep", "Cat", "Rat", "Rat", "Cow", "Buffalo", "Tiger", "Tiger", "Buffalo", "Deer", "Deer", "Dog", "Monkey", "Mongoose", "Monkey", "Lion", "Horse", "Lion", "Cow", "Elephant"]
GANA = ["Deva", "Manushya", "Rakshasa", "Manushya", "Deva", "Manushya", "Deva", "Deva", "Rakshasa", "Rakshasa", "Manushya", "Manushya", "Deva", "Rakshasa", "Deva", "Rakshasa", "Deva", "Rakshasa", "Rakshasa", "Manushya", "Manushya", "Deva", "Rakshasa", "Rakshasa", "Manushya", "Manushya", "Deva"]
NADI = ["Adi", "Madhya", "Antya", "Antya", "Madhya", "Adi", "Adi", "Madhya", "Antya", "Antya", "Madhya", "Adi", "Adi", "Madhya", "Antya", "Antya", "Madhya", "Adi", "Adi", "Madhya", "Antya", "Antya", "Madhya", "Adi", "Adi", "Madhya", "Antya"]
YONI_ORDER = ["Horse", "Elephant", "Sheep", "Serpent", "Dog", "Cat", "Rat", "Cow", "Buffalo", "Tiger", "Deer", "Monkey", "Mongoose", "Lion"]
YONI_MATRIX = [
 [4,2,3,2,2,3,3,3,0,1,3,2,2,1],
 [2,4,3,2,2,3,3,3,3,2,2,2,2,0],
 [3,3,4,3,2,3,1,3,3,1,3,0,3,1],
 [2,2,3,4,2,2,1,1,2,2,2,2,0,2],
 [2,2,2,2,4,1,1,2,2,1,0,2,2,1],
 [2,2,3,2,1,4,0,2,2,1,2,2,2,2],
 [2,2,2,1,1,0,4,2,2,2,2,2,2,1],
 [3,2,3,1,2,2,2,4,3,0,3,2,3,1],
 [0,3,3,2,2,2,2,3,4,1,2,2,2,3],
 [1,2,1,2,1,1,2,0,1,4,2,1,2,2],
 [3,2,3,2,0,2,2,3,2,1,4,2,2,2],
 [2,3,0,2,2,2,2,2,2,1,2,4,2,3],
 [2,2,3,0,2,2,2,3,2,2,2,2,4,2],
 [1,0,1,2,1,2,1,1,3,2,2,2,2,4],
]
RASHI_LORD = ["Mars", "Venus", "Mercury", "Moon", "Sun", "Mercury", "Venus", "Mars", "Jupiter", "Saturn", "Saturn", "Jupiter"]
NATURAL_FRIENDS = {
 "Sun": {"Moon", "Mars", "Jupiter"}, "Moon": {"Sun", "Mercury"}, "Mars": {"Sun", "Moon", "Jupiter"},
 "Mercury": {"Sun", "Venus"}, "Jupiter": {"Sun", "Moon", "Mars"}, "Venus": {"Mercury", "Saturn"}, "Saturn": {"Mercury", "Venus"},
}
NATURAL_ENEMIES = {
 "Sun": {"Venus", "Saturn"}, "Moon": set(), "Mars": {"Mercury"}, "Mercury": {"Moon"},
 "Jupiter": {"Mercury", "Venus"}, "Venus": {"Sun", "Moon"}, "Saturn": {"Sun", "Moon", "Mars"},
}
VARNA = {0:3, 1:2, 2:1, 3:4, 4:3, 5:2, 6:1, 7:4, 8:3, 9:2, 10:1, 11:4} # Kshatriya=3, Vaishya=2, Shudra=1, Brahmin=4
VASHYA = {0:1,1:1,2:0,3:2,4:1,5:0,6:0,7:3,8:1,9:2,10:2,11:2} # human, quadruped, water, insect
VASHYA_SCORE = [[2,.5,.5,1],[.5,2,2,2],[.5,2,2,2],[1,2,2,2]]
GANA_SCORE = {("Deva","Deva"):6,("Deva","Manushya"):5,("Deva","Rakshasa"):1,("Manushya","Deva"):6,("Manushya","Manushya"):6,("Manushya","Rakshasa"):0,("Rakshasa","Deva"):0,("Rakshasa","Manushya"):0,("Rakshasa","Rakshasa"):6}

def _tara(a: int, b: int) -> float:
    def tara(x: int, y: int) -> int:
        count = ((y-x) % 27) + 1
        return count % 9 or 9
    x, y = tara(a,b), tara(b,a)
    return 1.5 if (x in {3,5,7}) != (y in {3,5,7}) else 0 if x in {3,5,7} else 3

def _maitri(a: int, b: int) -> float:
    la, lb = RASHI_LORD[a], RASHI_LORD[b]
    if la == lb: return 5
    ab = "friend" if lb in NATURAL_FRIENDS[la] else "enemy" if lb in NATURAL_ENEMIES[la] else "neutral"
    ba = "friend" if la in NATURAL_FRIENDS[lb] else "enemy" if la in NATURAL_ENEMIES[lb] else "neutral"
    scores = {("friend","friend"):5,("friend","neutral"):4,("neutral","friend"):4,("neutral","neutral"):3,("friend","enemy"):1,("enemy","friend"):1,("neutral","enemy"):.5,("enemy","neutral"):.5,("enemy","enemy"):0}
    return scores[(ab,ba)]

def compare_ashtakoota(bride: dict[str, Any], groom: dict[str, Any]) -> dict[str, Any]:
    a, b = bride["sign_index"], groom["sign_index"]
    na, nb = bride["nakshatra_index"], groom["nakshatra_index"]
    animal_a, animal_b = YONI_ANIMAL[na], YONI_ANIMAL[nb]
    kootas = [
      {"name":"Varna","score":1 if VARNA[b] >= VARNA[a] else 0,"max":1,"detail":f"{SIGNS[a]} / {SIGNS[b]} sign varna; conventional bride-to-groom ordering."},
      {"name":"Vashya","score":VASHYA_SCORE[VASHYA[a]][VASHYA[b]],"max":2,"detail":"Rashi vashya classes and directional score table."},
      {"name":"Tara (Dina)","score":_tara(na,nb),"max":3,"detail":f"Nakshatra counts: {((nb-na)%27)+1} and {((na-nb)%27)+1}; 3rd, 5th, and 7th taras are treated as unfavorable."},
      {"name":"Yoni","score":YONI_MATRIX[YONI_ORDER.index(animal_a)][YONI_ORDER.index(animal_b)],"max":4,"detail":f"{animal_a} / {animal_b} yoni table."},
      {"name":"Graha Maitri","score":_maitri(a,b),"max":5,"detail":f"Natural relationship between {RASHI_LORD[a]} and {RASHI_LORD[b]}, the Moon-sign lords."},
      {"name":"Gana","score":GANA_SCORE[(GANA[na],GANA[nb])],"max":6,"detail":f"{GANA[na]} / {GANA[nb]} nakshatra gana."},
      {"name":"Bhakoot (Rashi)","score":0 if (b-a)%12 in {1,11,4,8,5,7} else 7,"max":7,"detail":f"Moon-sign distance: {((b-a)%12)+1} signs from Partner A to Partner B."},
      {"name":"Nadi","score":0 if NADI[na]==NADI[nb] else 8,"max":8,"detail":f"{NADI[na]} / {NADI[nb]} nadi."},
    ]
    score = sum(k["score"] for k in kootas)
    exceptions=[]
    if (b-a)%12 in {1,11,4,8,5,7} and RASHI_LORD[a] == RASHI_LORD[b]: exceptions.append("Bhakoot exception noted: Moon-sign lords are the same; this does not alter the displayed base score.")
    if na == nb and a == b and bride.get("pada") != groom.get("pada"): exceptions.append("Same Moon sign and nakshatra but different padas; some traditions treat this as a Nadi/Gana exception. Base score remains unchanged.")
    return {"score":score,"max_score":36,"threshold_note":"18/36 is a commonly used traditional reference threshold, not a prediction of relationship success.","kootas":kootas,"exceptions":exceptions,"partners":{"a":{"rashi":SIGNS[a],"nakshatra":NAKSHATRAS[na],"pada":bride["pada"],"nadi":NADI[na],"gana":GANA[na],"yoni":animal_a},"b":{"rashi":SIGNS[b],"nakshatra":NAKSHATRAS[nb],"pada":groom["pada"],"nadi":NADI[nb],"gana":GANA[nb],"yoni":animal_b}},"method":"North Indian Ashtakoota, 36-point scoring with Muhurta Chintamani tables. Scores shown in conventional bride-to-groom orientation; results are traditional screening only."}
