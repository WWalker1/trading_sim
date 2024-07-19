import tkinter as tk
from tkinter import messagebox, simpledialog
import random

class EconomicGame:
    def __init__(self, master):
        self.master = master
        self.master.title("Advanced Economic Strategy Game")
        
        self.players = [Player("Player 1"), Player("Player 2")]
        self.current_player = 0
        self.turn = 1
        self.max_turns = 15
        self.market = {
            'raw': {'price': 10, 'demand': random.randint(3, 8)},
            'manufactured': {'price': 20, 'demand': random.randint(2, 6)},
            'luxury': {'price': 30, 'demand': random.randint(1, 4)}
        }
        self.listed_products = []
        self.units_sold = {'raw': 0, 'manufactured': 0, 'luxury': 0}
        
        self.production_costs = {
            'raw': {'fixed': 20, 'variable': 5, 'increasing': 0.1},
            'manufactured': {'fixed': 30, 'variable': 10, 'increasing': 0.2},
            'luxury': {'fixed': 50, 'variable': 15, 'increasing': 0.3}
        }
        
        self.setup_gui()
        self.update_display()
        
    def setup_gui(self):
        self.info_label = tk.Label(self.master, text="", justify=tk.LEFT)
        self.info_label.pack(pady=10)
        
        self.action_frame = tk.Frame(self.master)
        self.action_frame.pack()
        
        actions = [
            ("Produce (2 AP)", self.produce, "Produce goods. Costs 2 AP and varies by good type and quantity."),
            ("List for Sale (1 AP)", self.list_for_sale, "List goods for sale. Costs 1 AP."),
            ("Buy (1 AP)", self.buy, "Buy goods from other players or the market. Costs 1 AP."),
            ("Research (3 AP)", self.research, "Research new technologies. Costs 3 AP and $50."),
            ("Take Loan", self.take_loan, "Borrow money. No AP cost, but 10% interest per turn."),
            ("End Turn", self.end_turn, "End your turn and pass to the next player.")
        ]
        
        for text, command, tooltip in actions:
            button = tk.Button(self.action_frame, text=text, command=command)
            button.pack(side=tk.LEFT)
            self.create_tooltip(button, tooltip)
        
    def create_tooltip(self, widget, text):
        def enter(event):
            self.tooltip = tk.Toplevel(self.master)
            self.tooltip.wm_overrideredirect(True)
            self.tooltip.wm_geometry(f"+{event.x_root+10}+{event.y_root+10}")
            label = tk.Label(self.tooltip, text=text, justify=tk.LEFT, background="#ffffe0", relief=tk.SOLID, borderwidth=1)
            label.pack()

        def leave(event):
            if self.tooltip:
                self.tooltip.destroy()

        widget.bind("<Enter>", enter)
        widget.bind("<Leave>", leave)
        
    def update_display(self):
        player = self.players[self.current_player]
        info = f"Turn {self.turn}/{self.max_turns} - {player.name}'s Turn\n"
        info += f"Action Points: {player.action_points}/5\n"
        info += f"Money: ${player.money} (Loan: ${player.loan})\n"
        info += f"Goods: Raw {player.goods['raw']}, Manufactured {player.goods['manufactured']}, Luxury {player.goods['luxury']}\n"
        info += f"Production Capacity: Raw {player.production['raw']}, Manufactured {player.production['manufactured']}, Luxury {player.production['luxury']}\n"
        info += f"Technologies: {', '.join(player.technologies)}\n\n"
        info += "Market Information:\n"
        info += "Listed Products:\n"
        for listing in self.listed_products:
            info += f"{listing['player'].name}: {listing['good_type']} x{listing['quantity']} @ ${listing['price']}/unit\n"
        self.info_label.config(text=info)
        for good, data in self.market.items():
            info += f"{good.capitalize()}: ${data['price']} (Demand: {data['demand']})\n"
        self.info_label.config(text=info)

    def list_for_sale(self):
        player = self.players[self.current_player]
        if player.action_points < 1:
            messagebox.showinfo("Action Failed", "Not enough action points. Listing requires 1 AP.")
            return

        good_type = simpledialog.askstring("List for Sale", "What type of good to list? (raw/manufactured/luxury)")
        if good_type not in self.market:
            messagebox.showinfo("Invalid Input", "Invalid good type. Choose raw, manufactured, or luxury.")
            return

        if player.goods[good_type] == 0:
            messagebox.showinfo("List for Sale", f"You don't have any {good_type} goods to list.")
            return

        quantity = simpledialog.askinteger("List for Sale", f"How many {good_type} units to list? (1-{player.goods[good_type]})", minvalue=1, maxvalue=player.goods[good_type])
        if quantity is None:
            return

        price = simpledialog.askfloat("List for Sale", f"At what price per unit? (Current market price: ${self.market[good_type]['price']})")
        if price is None:
            return

        self.listed_products.append({
            'player': player,
            'good_type': good_type,
            'quantity': quantity,
            'price': price
        })

        player.action_points -= 1
        messagebox.showinfo("List for Sale", f"You listed {quantity} {good_type} goods for sale at ${price} per unit.")
        self.update_display()  

    def produce(self):
        player = self.players[self.current_player]
        if player.action_points < 2:
            messagebox.showinfo("Action Failed", "Not enough action points. Production requires 2 AP.")
            return
        
        good_type = simpledialog.askstring("Produce", "What type of good to produce? (raw/manufactured/luxury)")
        if good_type not in player.production:
            messagebox.showinfo("Invalid Input", "Invalid good type. Choose raw, manufactured, or luxury.")
            return
        
        max_production = player.production[good_type]
        if good_type == 'manufactured':
            max_production = min(max_production, player.goods['raw'])
        elif good_type == 'luxury':
            max_production = min(max_production, player.goods['manufactured'])
        
        cost_info = self.calculate_production_cost(good_type, max_production)
        production = simpledialog.askinteger("Produce", f"How many {good_type} goods to produce? (1-{max_production})\n\n{cost_info}", minvalue=1, maxvalue=max_production)
        if production is None:
            return
        
        total_cost = self.calculate_total_cost(good_type, production)
        if player.money < total_cost:
            messagebox.showinfo("Production Failed", f"Not enough money. Production costs ${total_cost}.")
            return
        
        player.money -= total_cost
        
        if good_type == 'manufactured':
            player.goods['raw'] -= production
        elif good_type == 'luxury':
            player.goods['manufactured'] -= production
        
        player.goods[good_type] += production
        player.action_points -= 2
        messagebox.showinfo("Production", f"You produced {production} {good_type} goods for ${total_cost}.")
        self.update_display()
        
    def calculate_production_cost(self, good_type, quantity):
        costs = self.production_costs[good_type]
        fixed_cost = costs['fixed']
        variable_cost = costs['variable']
        increasing_cost = costs['increasing']
        
        total_cost = fixed_cost + (variable_cost * quantity) + (increasing_cost * (quantity ** 2) / 2)
        
        info = f"Production Costs for {good_type.capitalize()} Goods:\n"
        info += f"Fixed Cost: ${fixed_cost}\n"
        info += f"Variable Cost: ${variable_cost} per unit\n"
        info += f"Increasing Marginal Cost: ${increasing_cost} per additional unit\n\n"
        info += f"Total Cost for {quantity} units: ${total_cost:.2f}"
        
        return info
    
    def calculate_total_cost(self, good_type, quantity):
        costs = self.production_costs[good_type]
        fixed_cost = costs['fixed']
        variable_cost = costs['variable']
        increasing_cost = costs['increasing']
        
        total_cost = fixed_cost + (variable_cost * quantity) + (increasing_cost * (quantity ** 2) / 2)
        return total_cost
        
    def trade(self):
        player = self.players[self.current_player]
        if player.action_points < 1:
            messagebox.showinfo("Action Failed", "Not enough action points. Trading requires 1 AP.")
            return
        
        good_type = simpledialog.askstring("Trade", "What type of good to sell? (raw/manufactured/luxury)")
        if good_type not in self.market:
            messagebox.showinfo("Invalid Input", "Invalid good type. Choose raw, manufactured, or luxury.")
            return
        
        max_trade = min(player.goods[good_type], self.market[good_type]['demand'] - self.units_sold[good_type])
        if max_trade <= 0:
            messagebox.showinfo("Trade", "No demand or goods available for this type.")
            return
        
        units_to_sell = simpledialog.askinteger("Trade", f"How many {good_type} units to sell? (1-{max_trade})", minvalue=1, maxvalue=max_trade)
        if units_to_sell is None:
            return
        
        player.goods[good_type] -= units_to_sell
        revenue = units_to_sell * self.market[good_type]['price']
        revenue_with_bonus = revenue * (1 + player.trade_bonus)
        player.money += revenue_with_bonus
        player.action_points -= 1
        self.units_sold[good_type] += units_to_sell
        
        messagebox.showinfo("Trade", f"You sold {units_to_sell} {good_type} goods for ${revenue_with_bonus:.2f} (including trade bonus)")
        self.update_display()
    
    def sell(self):
        player = self.players[self.current_player]
        if player.action_points < 1:
            messagebox.showinfo("Action Failed", "Not enough action points. Selling requires 1 AP.")
            return
        
        good_type = simpledialog.askstring("Sell", "What type of good to sell? (raw/manufactured/luxury)")
        if good_type not in self.market:
            messagebox.showinfo("Invalid Input", "Invalid good type. Choose raw, manufactured, or luxury.")
            return
        
        if player.goods[good_type] == 0:
            messagebox.showinfo("Sell", f"You don't have any {good_type} goods to sell.")
            return
        
        demand_schedule = self.generate_demand_schedule(good_type)
        schedule_info = "Demand Schedule:\n" + "\n".join([f"Price: ${price}, Demand: {demand}" for price, demand in demand_schedule])
        
        units_to_sell = simpledialog.askinteger("Sell", f"How many {good_type} units to sell? (1-{player.goods[good_type]})\n\n{schedule_info}", minvalue=1, maxvalue=player.goods[good_type])
        if units_to_sell is None:
            return
        
        total_revenue, units_sold = self.execute_sale(good_type, units_to_sell, demand_schedule)
        player.goods[good_type] -= units_sold
        player.money += total_revenue
        player.action_points -= 1
        
        messagebox.showinfo("Sell", f"You sold {units_sold} {good_type} goods for ${total_revenue:.2f}")
        self.update_display()
        
    def generate_demand_schedule(self, good_type):
        base_price = self.market[good_type]['price']
        base_demand = self.market[good_type]['demand']
        schedule = []
        for i in range(5):
            price = base_price - i
            demand = base_demand + i * 2
            schedule.append((price, demand))
        return schedule
        
    def execute_sale(self, good_type, units_to_sell, demand_schedule):
        total_revenue = 0
        units_sold = 0
        for price, demand in demand_schedule:
            if units_to_sell == 0:
                break
            sold = min(units_to_sell, demand)
            total_revenue += sold * price
            units_sold += sold
            units_to_sell -= sold
        return total_revenue, units_sold
        
    def buy(self):
        player = self.players[self.current_player]
        if player.action_points < 1:
            messagebox.showinfo("Action Failed", "Not enough action points. Buying requires 1 AP.")
            return

        good_type = simpledialog.askstring("Buy", "What type of good to buy? (raw/manufactured/luxury)")
        if good_type not in self.market:
            messagebox.showinfo("Invalid Input", "Invalid good type. Choose raw, manufactured, or luxury.")
            return

        player_listings = [listing for listing in self.listed_products if listing['good_type'] == good_type and listing['player'] != player]
        market_price = self.market[good_type]['price']

        buy_options = "0. Buy from the market at ${:.2f} per unit\n".format(market_price)
        for i, listing in enumerate(player_listings, 1):
            buy_options += f"{i}. Buy from {listing['player'].name} at ${listing['price']} per unit (x{listing['quantity']} available)\n"

        choice = simpledialog.askinteger("Buy", f"Choose an option to buy {good_type} goods:\n\n{buy_options}", minvalue=0, maxvalue=len(player_listings))
        if choice is None:
            return

        if choice == 0:
            max_units = self.market[good_type]['demand']
            price = market_price
            seller = None
        else:
            listing = player_listings[choice - 1]
            max_units = listing['quantity']
            price = listing['price']
            seller = listing['player']

        units_to_buy = simpledialog.askinteger("Buy", f"How many {good_type} units to buy? (1-{max_units})", minvalue=1, maxvalue=max_units)
        if units_to_buy is None:
            return

        total_cost = units_to_buy * price
        if player.money < total_cost:
            messagebox.showinfo("Buy", f"Not enough money. Total cost: ${total_cost:.2f}")
            return

        player.money -= total_cost
        player.goods[good_type] += units_to_buy
        player.action_points -= 1

        if seller:
            seller.money += total_cost
            seller.goods[good_type] -= units_to_buy
            listing['quantity'] -= units_to_buy
            if listing['quantity'] == 0:
                self.listed_products.remove(listing)
            messagebox.showinfo("Buy", f"You bought {units_to_buy} {good_type} goods from {seller.name} for ${total_cost:.2f}")
        else:
            self.market[good_type]['demand'] -= units_to_buy
            messagebox.showinfo("Buy", f"You bought {units_to_buy} {good_type} goods from the market for ${total_cost:.2f}")

        self.update_market_demand(good_type, -units_to_buy)
        self.update_display()
    
    def research(self):
        player = self.players[self.current_player]
        ap_cost = 3 - player.research_discount
        money_cost = 50
        if player.action_points < ap_cost:
            messagebox.showinfo("Action Failed", f"Not enough action points. Research requires {ap_cost} AP.")
            return
        if player.money < money_cost:
            messagebox.showinfo("Action Failed", f"Not enough money. Research costs ${money_cost}.")
            return
        
        available_tech = [tech for tech in ['Efficiency', 'Marketing', 'Innovation'] if tech not in player.technologies]
        if not available_tech:
            messagebox.showinfo("Research", "No more technologies available.")
            return
        
        tech_info = {
            'Efficiency': "Increases production capacity for all goods by 1",
            'Marketing': "Adds a 10% bonus to all trade revenues",
            'Innovation': "Reduces research AP cost by 1"
        }
        
        tech_choices = "\n".join([f"{tech}: {tech_info[tech]}" for tech in available_tech])
        tech = simpledialog.askstring("Research", f"Which technology to research?\n\n{tech_choices}")
        if tech not in available_tech:
            messagebox.showinfo("Invalid Input", "Invalid technology.")
            return
        
        player.technologies.append(tech)
        player.action_points -= ap_cost
        player.money -= money_cost
        if tech == 'Efficiency':
            for good in player.production:
                player.production[good] += 1
        elif tech == 'Marketing':
            player.trade_bonus = 0.1
        elif tech == 'Innovation':
            player.research_discount = 1
        
        messagebox.showinfo("Research", f"You have researched {tech} for ${money_cost}!")
        self.update_display()
        
    def take_loan(self):
        player = self.players[self.current_player]
        loan_amount = simpledialog.askinteger("Loan", "How much do you want to borrow? (10% interest per turn)", minvalue=1, maxvalue=1000)
        if loan_amount is None:
            return
        player.money += loan_amount
        player.loan += loan_amount
        messagebox.showinfo("Loan", f"You borrowed ${loan_amount}. Remember to pay it back with 10% interest per turn!")
        self.update_display()
        
    def end_turn(self):
        player = self.players[self.current_player]
        interest = int(player.loan * 0.1)
        player.money -= interest
        player.loan += interest
        
        self.current_player = 1 - self.current_player
        self.players[self.current_player].action_points = 5
        
        if self.current_player == 0:
            self.turn += 1
            self.adjust_market()
            self.trigger_event()
        
        if self.turn > self.max_turns:
            self.end_game()
        else:
            self.update_display()
        self.listed_products = [listing for listing in self.listed_products if listing['player'] != player]

    def adjust_market(self):
        for good, data in self.market.items():
            if self.units_sold[good] < data['demand']:
                data['price'] = min(50, data['price'] + random.randint(1, 3))
            elif self.units_sold[good] > data['demand']:
                data['price'] = max(5, data['price'] - random.randint(1, 3))
            data['demand'] = random.randint(1, 15)
            self.units_sold[good] = 0
        
    def trigger_event(self):
        events = [
            ("Economic Boom", "All goods' demands increased", lambda: self.modify_demands(2)),
            ("Recession", "All goods' demands decreased", lambda: self.modify_demands(-2)),
            ("Raw Material Shortage", "Raw material price doubled", lambda: self.modify_price('raw', 2)),
            ("Luxury Goods Craze", "Luxury goods demand tripled", lambda: self.modify_demand('luxury', 3))
        ]
        
        event = random.choice(events)
        messagebox.showinfo("Economic Event", f"{event[0]}: {event[1]}")
        event[2]()
        
    def modify_demands(self, change):
        for good in self.market:
            self.market[good]['demand'] = max(1, self.market[good]['demand'] + change)
            
    def modify_price(self, good, factor):
        self.market[good]['price'] *= factor
        
    def modify_demand(self, good, factor):
        self.market[good]['demand'] *= factor

    def update_market_demand(self, good_type, change):
        self.market[good_type]['demand'] = max(0, self.market[good_type]['demand'] + change)
        price_change = -0.1 * change  # Adjust price based on supply/demand
        self.market[good_type]['price'] = max(1, self.market[good_type]['price'] + price_change)

    def generate_demand_schedule(self, good_type):
        base_price = self.market[good_type]['price']
        base_demand = self.market[good_type]['demand']
        schedule = []
        for i in range(3):  # Reduced to 3 price points
            price = base_price - i
            demand = max(0, base_demand - i)
            schedule.append((price, demand))
        return schedule

    def adjust_market(self):
        for good, data in self.market.items():
            data['demand'] = max(1, data['demand'] + random.randint(-1, 1))
            data['price'] = max(1, data['price'] + random.uniform(-0.5, 0.5))

    def end_game(self):
        for player in self.players:
            player.money -= player.loan
        winner = max(self.players, key=lambda p: p.money + sum(p.goods[g] * self.market[g]['price'] for g in p.goods))
        total_value = winner.money + sum(winner.goods[g] * self.market[g]['price'] for g in winner.goods)
        messagebox.showinfo("Game Over", f"{winner.name} wins with a total value of ${total_value}!")
        self.master.quit()

class Player:
    def __init__(self, name):
        self.name = name
        self.money = 200
        self.loan = 0
        self.goods = {'raw': 0, 'manufactured': 0, 'luxury': 0}
        self.production = {'raw': 5, 'manufactured': 3, 'luxury': 1}
        self.technologies = []
        self.action_points = 5
        self.trade_bonus = 0
        self.research_discount = 0

if __name__ == "__main__":
    root = tk.Tk()
    game = EconomicGame(root)
    root.mainloop()