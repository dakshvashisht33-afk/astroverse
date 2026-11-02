from typing import Dict, Any, List
from .astrology_engine import engine
from .transit_engine import transit_engine
from .database import BirthProfile

class AstrologyContextProvider:
    """
    Converts raw astrological data into a structured, natural-language
    context that an LLM can use to provide accurate interpretations.
    """

    def __init__(self):
        self.safety_system_prompt = (
            "You are Astro AI, a professional, empathetic, and insightful astrology consultant. "
            "Your goal is to provide guidance based on the provided astrological data. "
            "CRITICAL SAFETY RULES:\n"
            "1. NEVER provide medical diagnoses, medication advice, or treatment plans.\n"
            "2. NEVER provide legal advice or financial guarantees.\n"
            "3. NEVER predict the exact date of death, accidents, or pregnancy.\n"
            "4. Always use interpretive language (e.g., 'this suggests', 'indicates a tendency').\n"
            "5. If a user mentions self-harm or a crisis, immediately stop astrology and provide crisis resources.\n"
            "6. All content is for entertainment and self-reflection purposes only."
        )

    def build_context(self, birth_profile: BirthProfile) -> str:
        """
        Constructs a comprehensive astrological snapshot of the user.
        """
        # 1. Basic Data
        dt_str = f"{birth_profile.dob} {birth_profile.tob}"
        from datetime import datetime
        dob_dt = datetime.strptime(dt_str, "%Y-%m-%d %H:%M:%S")

        # 2. Calculate Natal Positions
        natal = engine.calculate_planetary_positions(dob_dt, birth_profile.timezone)

        # 3. Calculate Current Transits
        current_sky = transit_engine.get_current_sky()

        # 4. Build the text string
        context = [
            "### USER ASTROLOGICAL SNAPSHOT ###",
            f"Birth Details: Born in {birth_profile.birth_city} ({birth_profile.timezone})",
            "\n--- NATAL PLACEMENTS ---"
        ]

        for planet, data in natal.items():
            context.append(f"- {planet}: {data['sign']} at {data['degree']:.2f}°")

        context.append("\n--- CURRENT TRANSITS (Live Sky) ---")
        for planet, data in current_sky.items():
            context.append(f"- {planet}: {data['sign']} at {data['degree']:.2f}°")

        # 5. Calculate key aspects between Natal and Transit
        context.append("\n--- ACTIVE ASPECTS ---")
        for p_name, p_data in current_sky.items():
            if p_name in natal:
                aspect = transit_engine.calculate_aspects(
                    natal[p_name]["longitude"],
                    p_data["longitude"]
                )
                if aspect:
                    context.append(f"- Transit {p_name} {aspect} Natal {p_name}")

        return "\n".join(context)

context_provider = AstrologyContextProvider()
