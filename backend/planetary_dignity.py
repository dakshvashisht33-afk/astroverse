SIGNS = [
    "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
    "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces",
]

SIGN_LORD = {
    0: "Mars", 1: "Venus", 2: "Mercury", 3: "Moon", 4: "Sun", 5: "Mercury",
    6: "Venus", 7: "Mars", 8: "Jupiter", 9: "Saturn", 10: "Saturn", 11: "Jupiter",
}

EXALTATION = {"Sun": 0, "Moon": 1, "Mars": 9, "Mercury": 5, "Jupiter": 3, "Venus": 11, "Saturn": 6}
OWN_SIGNS = {
    "Sun": {4}, "Moon": {3}, "Mars": {0, 7}, "Mercury": {2, 5},
    "Jupiter": {8, 11}, "Venus": {1, 6}, "Saturn": {9, 10},
}
NATURAL_FRIENDS = {
    "Sun": {"Moon", "Mars", "Jupiter"},
    "Moon": {"Sun", "Mercury"},
    "Mars": {"Sun", "Moon", "Jupiter"},
    "Mercury": {"Sun", "Venus"},
    "Jupiter": {"Sun", "Moon", "Mars"},
    "Venus": {"Mercury", "Saturn"},
    "Saturn": {"Mercury", "Venus"},
}
NATURAL_ENEMIES = {
    "Sun": {"Venus", "Saturn"},
    "Moon": set(),
    "Mars": {"Mercury"},
    "Mercury": {"Moon"},
    "Jupiter": {"Mercury", "Venus"},
    "Venus": {"Sun", "Moon"},
    "Saturn": {"Sun", "Moon", "Mars"},
}


def dignity_for_sign(planet: str, sign_index: int) -> str:
    """Return classical seven-graha sign dignity using natural sign-lord relations."""
    if planet not in EXALTATION:
        return "Not classified"
    sign_index %= 12
    if EXALTATION[planet] == sign_index:
        return "Exalted"
    if (EXALTATION[planet] + 6) % 12 == sign_index:
        return "Debilitated"
    if sign_index in OWN_SIGNS[planet]:
        return "Own sign"

    lord = SIGN_LORD[sign_index]
    if lord == planet:
        return "Own sign"
    if lord in NATURAL_FRIENDS[planet]:
        return "Friendly sign"
    if lord in NATURAL_ENEMIES[planet]:
        return "Enemy sign"
    return "Neutral sign"
