class Factory:
    def __init__(self, product_type, production_capacity, efficiency=1.0, labor_cost=10):
        self.product_type = product_type
        self.production_capacity = production_capacity
        self.efficiency = 1.0
        self.labor_cost = 10
        self.fixed_cost = 50
        self.level = 1

    def upgrade(self):
        self.level += 1
        self.production_capacity += 2
        self.efficiency += 0.1

    def upgrade_cost(self):
        return self.level * 100