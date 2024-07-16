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
            'raw': {'price': 10, 'demand': random.randint(5, 15)},
            'manufactured': {'price': 20, 'demand': random.randint(3, 10)},
            'luxury': {'price': 30, 'demand': random.randint(1, 5)}
        }
        self.units_sold = {'raw': 0, 'manufactured': 0, 'luxury': 0}
        
        self.setup_gui()
        self.update_display()
        
    def setup_gui(self):
        self.info_label = tk.Label(self.master, text="", justify=tk.LEFT)
        self.info_label.pack(pady=10)
        
        self.action_frame = tk.Frame(self.master)
        self.action_frame.pack()
        
        actions = [
            ("Produce (2 AP)", self.produce),
            ("Trade (1 AP)", self.trade),
            ("Research (3 AP)", self.research),
            ("Take Loan", self.take_loan),
            ("End Turn", self.end_turn)
        ]
        
        for text, command in actions:
            tk.Button(self.action_frame, text=text, command=command).pack(side=tk.LEFT)
        
    def update_display(self):
        player = self.players[self.current_player]
        info = f"Turn {self.turn}/{self.max_turns} - {player.name}'s Turn\n"
        info += f"Action Points: {player.action_points}/5\n"
        info += f"Money: ${player.money} (Loan: ${player.loan})\n"
        info += f"Goods: Raw {player.goods['raw']}, Manufactured {player.goods['manufactured']}, Luxury {player.goods['luxury']}\n"
        info += f"Production: Raw {player.production['raw']}, Manufactured {player.production['manufactured']}, Luxury {player.production['luxury']}\n"
        info += f"Technologies: {', '.join(player.technologies)}\n\n"
        info += "Market Information:\n"
        for good, data in self.market.items():
            info += f"{good.capitalize()}: ${data['price']} (Demand: {data['demand']})\n"
        self.info_label.config(text=info)
        
    def produce(self):
        player = self.players[self.current_player]
        if player.action_points < 2:
            messagebox.showinfo("Action Failed", "Not enough action points.")
            return
        
        good_type = simpledialog.askstring("Produce", "What type of good to produce? (raw/manufactured/luxury)")
        if good_type not in player.production:
            messagebox.showinfo("Invalid Input", "Invalid good type.")
            return
        
        production = random.randint(1, player.production[good_type])
        if good_type == 'manufactured' and player.goods['raw'] < production:
            production = player.goods['raw']
            player.goods['raw'] -= production
        elif good_type == 'luxury' and player.goods['manufactured'] < production:
            production = player.goods['manufactured']
            player.goods['manufactured'] -= production
        
        player.goods[good_type] += production
        player.action_points -= 2
        messagebox.showinfo("Production", f"You produced {production} {good_type} goods.")
        self.update_display()
        
    def trade(self):
        player = self.players[self.current_player]
        if player.action_points < 1:
            messagebox.showinfo("Action Failed", "Not enough action points.")
            return
        
        good_type = simpledialog.askstring("Trade", "What type of good to sell? (raw/manufactured/luxury)")
        if good_type not in self.market:
            messagebox.showinfo("Invalid Input", "Invalid good type.")
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
        player.money += revenue
        player.action_points -= 1
        self.units_sold[good_type] += units_to_sell
        
        messagebox.showinfo("Trade", f"You sold {units_to_sell} {good_type} goods for ${revenue}")
        self.update_display()
        
    def research(self):
        player = self.players[self.current_player]
        if player.action_points < 3:
            messagebox.showinfo("Action Failed", "Not enough action points.")
            return
        
        available_tech = [tech for tech in ['Efficiency', 'Marketing', 'Innovation'] if tech not in player.technologies]
        if not available_tech:
            messagebox.showinfo("Research", "No more technologies available.")
            return
        
        tech = simpledialog.askstring("Research", f"Which technology to research? ({'/'.join(available_tech)})")
        if tech not in available_tech:
            messagebox.showinfo("Invalid Input", "Invalid technology.")
            return
        
        player.technologies.append(tech)
        player.action_points -= 3
        if tech == 'Efficiency':
            for good in player.production:
                player.production[good] += 1
        elif tech == 'Marketing':
            player.trade_bonus = 0.1
        elif tech == 'Innovation':
            player.research_discount = 1
        
        messagebox.showinfo("Research", f"You have researched {tech}!")
        self.update_display()
        
    def take_loan(self):
        player = self.players[self.current_player]
        loan_amount = simpledialog.askinteger("Loan", "How much do you want to borrow?", minvalue=1, maxvalue=1000)
        if loan_amount is None:
            return
        player.money += loan_amount
        player.loan += loan_amount
        messagebox.showinfo("Loan", f"You borrowed ${loan_amount}. Remember to pay it back with 10% interest!")
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