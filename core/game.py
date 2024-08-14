import pygame
import random
from core.config import *
from core.player import Player
from core.market import Market
from core.button import Button
from core.faction import FACTIONS

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Economic Strategy Demo")
        self.font = pygame.font.Font(None, FONT_SIZE)
        self.clock = pygame.time.Clock()

        self.players = []
        self.current_player = 0
        self.market = Market()
        self.turn = 1
        self.viewing_factories = False
        self.selected_factory = None
        self.max_turns = 10
        
        self.main_buttons = [
            Button(50, 400, 150, 50, "Produce", self.produce),
            Button(220, 400, 150, 50, "Research", self.research),
            Button(390, 400, 150, 50, "Politics", self.influence_politics),
            Button(560, 400, 150, 50, "View Factories", self.toggle_factory_view),
            Button(50, 470, 150, 50, "End Turn", self.end_turn),
            Button(220, 470, 150, 50, "Faction Info", self.toggle_faction_benefits)
        ]

        self.factory_buttons = [
            Button(560, 400, 150, 50, "Back", self.toggle_factory_view),
            Button(560, 470, 150, 50, "Upgrade", self.upgrade_factory)
        ]

        self.faction_selection_done = False
        self.viewing_faction_benefits = False
        self.faction_buttons = [
            Button(50, 200 + i * 70, 300, 50, faction, self.select_faction)
            for i, faction in enumerate(FACTIONS.keys())
        ]    
        self.market = Market()
        self.selected_product = None
        self.listing_price = 0

        self.main_buttons.extend([
            Button(50, 540, 150, 50, "List Goods", self.show_listing_menu),
            Button(220, 540, 150, 50, "Sell at Market", self.show_market_sell_menu)
        ])
    
    def draw_game_state(self):
        self.screen.fill(WHITE)
        
        player = self.players[self.current_player]
        info_text = [
            f"Turn {self.turn}/{self.max_turns} - {player.name}'s Turn",
            f"Money: ${player.money} (Loan: ${player.loan})",
            f"Political Influence: {player.political_influence}",
            "",
            "Market Prices and Demand:",
            f"Raw: ${self.market.sectors['raw'].get_price()} (Demand: {self.market.sectors['raw'].get_demand()})",
            f"Manufactured: ${self.market.sectors['manufactured'].get_price()} (Demand: {self.market.sectors['manufactured'].get_demand()})",
            f"Luxury: ${self.market.sectors['luxury'].get_price()} (Demand: {self.market.sectors['luxury'].get_demand()})",
            f"Economic Cycle: {self.market.economic_cycle}%"
        ]
        for i, text in enumerate(info_text):
            text_surface = self.font.render(text, True, BLACK)
            self.screen.blit(text_surface, (50, 50 + i*30))

        if self.viewing_factories:
            self.draw_factory_view()
        else:
            for button in self.main_buttons:
                button.draw(self.screen, self.font)

    def draw_factory_view(self):
        player = self.players[self.current_player]
        for i, factory in enumerate(player.factories):
            y_pos = 50 + i * 100
            pygame.draw.rect(self.screen, GRAY, (50, y_pos, 500, 80))
            info_text = [
                f"Factory {i+1}: {factory.product_type.capitalize()}",
                f"Production: {factory.production_capacity} (Efficiency: {factory.efficiency:.1f})",
                f"Level: {factory.level} (Upgrade Cost: ${factory.upgrade_cost()})"
            ]
            for j, text in enumerate(info_text):
                text_surface = self.font.render(text, True, BLACK)
                self.screen.blit(text_surface, (60, y_pos + 10 + j*25))

            select_button = Button(560, y_pos, 150, 80, "Select", lambda f=factory: self.select_factory(f))
            select_button.draw(self.screen, self.font)

        for button in self.factory_buttons:
            button.draw(self.screen, self.font)

    def produce(self):
        player = self.players[self.current_player]
        if player.actions_left > 0:
            for factory in player.factories:
                if player.produce(factory, self.market):
                    player.actions_left -= 1
                else:
                    print(f"Not enough money to produce in {factory.product_type} factory")

    def show_listing_menu(self):
        self.viewing_factories = False
        self.listing_menu = True
        self.listing_buttons = [
            Button(50, 400, 150, 50, "Raw", lambda: self.select_product("raw")),
            Button(220, 400, 150, 50, "Manufactured", lambda: self.select_product("manufactured")),
            Button(390, 400, 150, 50, "Luxury", lambda: self.select_product("luxury")),
            Button(50, 470, 150, 50, "Confirm Listing", self.confirm_listing),
            Button(220, 470, 150, 50, "Cancel", self.cancel_listing)
        ]

    def show_market_sell_menu(self):
        self.viewing_factories = False
        self.market_sell_menu = True
        self.market_sell_buttons = [
            Button(50, 400, 150, 50, "Raw", lambda: self.sell_at_market("raw")),
            Button(220, 400, 150, 50, "Manufactured", lambda: self.sell_at_market("manufactured")),
            Button(390, 400, 150, 50, "Luxury", lambda: self.sell_at_market("luxury")),
            Button(50, 470, 150, 50, "Cancel", self.cancel_market_sell)
        ]

    def select_product(self, product_type):
        self.selected_product = product_type

    def confirm_listing(self):
        if self.selected_product and self.listing_price > 0:
            player = self.players[self.current_player]
            quantity = min(player.inventory[self.selected_product], 10)  # List up to 10 units at a time
            if player.list_goods(self.selected_product, quantity, self.listing_price):
                print(f"Listed {quantity} {self.selected_product} goods at ${self.listing_price} each")
            else:
                print("Not enough goods to list")
        self.cancel_listing()

    def cancel_listing(self):
        self.listing_menu = False
        self.selected_product = None
        self.listing_price = 0

    def sell_at_market(self, product_type):
        player = self.players[self.current_player]
        quantity = min(player.inventory[product_type], 10)  # Sell up to 10 units at a time
        if player.sell_at_market_price(product_type, quantity, self.market):
            print(f"Sold {quantity} {product_type} goods at market price")
        else:
            print("Not enough goods to sell")
        self.cancel_market_sell()

    def cancel_market_sell(self):
        self.market_sell_menu = False
    
    def research(self):
        player = self.players[self.current_player]
        if player.actions_left > 0 and len(player.technologies) < 3:
            tech_cost = 100
            if player.money >= tech_cost:
                player.money -= tech_cost
                player.technologies.append(random.choice(["Efficiency", "Marketing", "Innovation"]))
                player.actions_left -= 1

    def influence_politics(self):
        player = self.players[self.current_player]
        if player.actions_left > 0 and player.political_influence < 50:
            bribe_cost = 50
            if player.money >= bribe_cost:
                player.money -= bribe_cost
                player.political_influence += 10
                player.actions_left -= 1

    def toggle_factory_view(self):
        self.viewing_factories = not self.viewing_factories
        self.selected_factory = None

    def select_factory(self, factory):
        self.selected_factory = factory

    def upgrade_factory(self):
        if self.selected_factory:
            player = self.players[self.current_player]
            if player.actions_left > 0:
                upgrade_cost = self.selected_factory.upgrade_cost()
                if player.money >= upgrade_cost:
                    player.money -= upgrade_cost
                    self.selected_factory.upgrade()
                    player.actions_left -= 1

    def end_turn(self):
        self.current_player = 1 - self.current_player
        self.players[self.current_player].actions_left = ACTIONS_PER_TURN
        self.turn += 1
        if self.turn > MAX_TURNS:
            self.game_over()
        self.market.update()
        for player in self.players:
            player.update_listings(self.market)

    def game_over(self):
        winner = max(self.players, key=lambda p: p.money + p.political_influence)
        print(f"Game Over! {winner.name} wins with ${winner.money} and {winner.political_influence} political influence.")

    def select_faction(self, faction_name):
        if len(self.players) < 2:
            self.players.append(Player(f"Player {len(self.players) + 1}", faction_name))
            if len(self.players) == 2:
                self.faction_selection_done = True
                self.current_player = 0

    def draw_faction_selection(self):
        self.screen.fill(WHITE)
        title = self.font.render(f"Select Faction for Player {len(self.players) + 1}", True, BLACK)
        self.screen.blit(title, (50, 50))
        
        for button in self.faction_buttons:
            button.draw(self.screen, self.font)

    def draw_faction_benefits(self):
        self.screen.fill(WHITE)
        player = self.players[self.current_player]
        title = self.font.render(f"{player.name}'s Faction: {player.faction.name}", True, BLACK)
        self.screen.blit(title, (50, 50))
        
        description = self.font.render(player.faction.description, True, BLACK)
        self.screen.blit(description, (50, 100))
        
        for i, benefit in enumerate(player.faction.benefits):
            text = self.font.render(f"• {benefit}", True, BLACK)
            self.screen.blit(text, (50, 150 + i * 30))
        
        back_button = Button(50, 500, 150, 50, "Back", self.toggle_faction_benefits)
        back_button.draw(self.screen, self.font)

    def toggle_faction_benefits(self):
        self.viewing_faction_benefits = not self.viewing_faction_benefits

    def run(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if not self.faction_selection_done:
                        for button in self.faction_buttons:
                            if button.rect.collidepoint(event.pos):
                                button.action(button.text)
                    elif self.viewing_faction_benefits:
                        back_button = Button(50, 500, 150, 50, "Back", self.toggle_faction_benefits)
                        if back_button.rect.collidepoint(event.pos):
                            self.toggle_faction_benefits()
                    elif event.type == pygame.KEYDOWN and self.listing_menu:
                        if event.key == pygame.K_BACKSPACE:
                            self.listing_price = self.listing_price // 10
                        elif event.key in range(pygame.K_0, pygame.K_9 + 1):
                            self.listing_price = self.listing_price * 10 + int(event.unicode)
                    else:
                        for button in self.main_buttons:
                                if button.rect.collidepoint(event.pos):
                                    button.action()

            if not self.faction_selection_done:
                self.draw_faction_selection()
            elif self.viewing_faction_benefits:
                self.draw_faction_benefits()
            else:
                self.draw_game_state()

            pygame.display.flip()
            self.clock.tick(60)