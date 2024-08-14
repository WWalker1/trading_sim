class Faction:
    def __init__(self, name, description, benefits, bribery_cost_multiplier=1.0, 
                 research_cost_multiplier=1.0, market_power=1.0, research_speed_multiplier=1.0,
                 scandal_chance=0.0, espionage_vulnerability=1.0, buyout_power=1.0):
        self.name = name
        self.description = description
        self.benefits = benefits
        self.bribery_cost_multiplier = bribery_cost_multiplier
        self.research_cost_multiplier = research_cost_multiplier
        self.market_power = market_power
        self.research_speed_multiplier = research_speed_multiplier
        self.scandal_chance = scandal_chance
        self.espionage_vulnerability = espionage_vulnerability
        self.buyout_power = buyout_power

FACTIONS = {
    "Political Machine": Faction(
        "Political Machine",
        "Masters of political influence and manipulation.",
        [
            "Start with more political power",
            "Cheaper briberies",
            "Can influence market prices",
            "Risk of political scandals"
        ],
        bribery_cost_multiplier=0.7,
        market_power=1.1,
        scandal_chance=0.1
    ),
    "Technologist": Faction(
        "Technologist",
        "Leaders in technological innovation and efficiency.",
        [
            "Start with more efficient factories",
            "Cheaper and faster research",
            "Lower variable costs",
            "Vulnerable to industrial espionage"
        ],
        research_cost_multiplier=0.7,
        research_speed_multiplier=1.5,
        espionage_vulnerability=1.5
    ),
    "Monopolist": Faction(
        "Monopolist",
        "Dominant market force with significant economic power.",
        [
            "Start with larger factories",
            "More market power",
            "Can buy out smaller factories",
            "Risk of antitrust investigations"
        ],
        market_power=1.3,
        buyout_power=1.5
    )
}