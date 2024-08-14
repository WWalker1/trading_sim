import random

class Market:
    def __init__(self):
        self.sectors = {
            "raw": MarketSector("raw", base_price=10, base_demand=50),
            "manufactured": MarketSector("manufactured", base_price=20, base_demand=30),
            "luxury": MarketSector("luxury", base_price=30, base_demand=10)
        }
        self.economic_cycle = 0  # 0 to 100, representing the economic cycle

    def update(self):
        self.update_economic_cycle()
        for sector in self.sectors.values():
            sector.update(self.economic_cycle)

    def update_economic_cycle(self):
        # Simple economic cycle simulation
        self.economic_cycle += random.randint(-5, 5)
        self.economic_cycle = max(0, min(100, self.economic_cycle))

class MarketSector:
    def __init__(self, name, base_price, base_demand):
        self.name = name
        self.base_price = base_price
        self.base_demand = base_demand
        self.current_price = base_price
        self.current_demand = base_demand
        self.supply = 0

    def update(self, economic_cycle):
        # Update price based on supply and demand
        price_change = (self.current_demand - self.supply) / 100
        self.current_price += price_change
        self.current_price = max(self.base_price * 0.5, min(self.base_price * 2, self.current_price))

        # Update demand based on economic cycle
        cycle_effect = (economic_cycle - 50) / 100  # -0.5 to 0.5
        self.current_demand = self.base_demand * (1 + cycle_effect)

        # Reset supply for the next round
        self.supply = 0

    def add_supply(self, amount):
        self.supply += amount

    def get_price(self):
        return round(self.current_price, 2)

    def get_demand(self):
        return round(self.current_demand, 2)