import random
from core.factory import Factory
from core.faction import FACTIONS

class Player:
    def __init__(self, name, faction_name):
        self.name = name
        self.faction = FACTIONS[faction_name]
        self.money = 1000
        self.loan = 0
        self.factories = []
        self.technologies = []
        self.political_influence = 0
        self.actions_left = 3
        self.research_progress = 0

        self.inventory = {
            "raw": 0,
            "manufactured": 0,
            "luxury": 0
        }
        self.listed_goods = {
            "raw": [],
            "manufactured": [],
            "luxury": []
        }
        self.initialize_faction_benefits()

    def initialize_faction_benefits(self):
        if self.faction.name == "Political Machine":
            self.money = 750
            self.political_influence = 20
            self.factories = [Factory("raw", 4), Factory("manufactured", 2)]
        elif self.faction.name == "Technologist":
            self.money = 1200
            self.factories = [Factory("raw", 6, efficiency=1.2, labor_cost=8), Factory("manufactured", 4, efficiency=1.2, labor_cost=8)]
        elif self.faction.name == "Monopolist":
            self.factories = [Factory("raw", 8, labor_cost=8), Factory("manufactured", 5, labor_cost=8)]

    def get_bribery_cost(self, base_cost):
        return base_cost * self.faction.bribery_cost_multiplier

    def get_research_cost(self, base_cost):
        return base_cost * self.faction.research_cost_multiplier

    def get_market_power(self):
        return self.faction.market_power

    def advance_research(self, amount):
        self.research_progress += amount * self.faction.research_speed_multiplier

    def check_for_scandal(self):
        return random.random() < self.faction.scandal_chance

    def is_espionage_successful(self):
        return random.random() < self.faction.espionage_vulnerability * 0.1

    def can_buyout_factory(self, target_factory):
        return (self.faction.buyout_power * self.money) > (target_factory.value * 1.5)
    
    def produce(self, factory, market):
        production_cost = factory.labor_cost + factory.fixed_cost
        if self.money >= production_cost:
            self.money -= production_cost
            production = factory.production_capacity * factory.efficiency
            self.inventory[factory.product_type] += production
            return True
        return False

    def list_goods(self, product_type, quantity, price):
        if self.inventory[product_type] >= quantity:
            self.inventory[product_type] -= quantity
            self.listed_goods[product_type].append((quantity, price))
            return True
        return False

    def sell_at_market_price(self, product_type, quantity, market):
        if self.inventory[product_type] >= quantity:
            self.inventory[product_type] -= quantity
            price = market.sectors[product_type].get_price()
            revenue = price * quantity
            self.money += revenue
            market.sectors[product_type].add_supply(quantity)
            return True
        return False

    def update_listings(self, market):
        for product_type in self.listed_goods:
            for listing in self.listed_goods[product_type]:
                quantity, price = listing
                if price <= market.sectors[product_type].get_price():
                    self.money += price * quantity
                    market.sectors[product_type].add_supply(quantity)
            self.listed_goods[product_type] = []