import pygame
import sys
import random

pygame.init()

# Constants
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 800
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
FONT_SIZE = 20

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

class Button:
    def __init__(self, x, y, width, height, text, action):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.action = action

    def draw(self, screen, font):
        pygame.draw.rect(screen, GRAY, self.rect)
        text_surf = font.render(self.text, True, BLACK)
        text_rect = text_surf.get_rect(center=self.rect.center)
        screen.blit(text_surf, text_rect)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.action()

class Market:
    def __init__(self):
        self.goods = {
            'raw': {'price': 10, 'demand': random.randint(3, 8)},
            'manufactured': {'price': 20, 'demand': random.randint(2, 6)},
            'luxury': {'price': 30, 'demand': random.randint(1, 4)}
        }

    def update(self):
        for good in self.goods:
            self.goods[good]['price'] += random.randint(-2, 2)
            self.goods[good]['demand'] += random.randint(-1, 1)
            self.goods[good]['price'] = max(1, self.goods[good]['price'])
            self.goods[good]['demand'] = max(0, self.goods[good]['demand'])

class EconomicGame:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Economic Strategy Game")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, FONT_SIZE)
        
        self.players = [Player("Player 1"), Player("Player 2")]
        self.current_player = 0
        self.market = Market()
        self.turn = 1
        self.max_turns = 15

        self.buttons = [
            Button(50, 600, 150, 50, "Produce", self.produce),
            Button(220, 600, 150, 50, "Trade", self.trade),
            Button(390, 600, 150, 50, "Research", self.research),
            Button(560, 600, 150, 50, "Take Loan", self.take_loan),
            Button(730, 600, 150, 50, "End Turn", self.end_turn)
        ]

    def produce(self):
        player = self.players[self.current_player]
        if player.action_points >= 2:
            player.goods['raw'] += player.production['raw']
            player.action_points -= 2
            print(f"{player.name} produced {player.production['raw']} raw goods")

    def trade(self):
        player = self.players[self.current_player]
        if player.action_points >= 1 and player.goods['raw'] > 0:
            sold = min(player.goods['raw'], self.market.goods['raw']['demand'])
            revenue = sold * self.market.goods['raw']['price']
            player.goods['raw'] -= sold
            player.money += revenue
            player.action_points -= 1
            print(f"{player.name} sold {sold} raw goods for ${revenue}")

    def research(self):
        player = self.players[self.current_player]
        if player.action_points >= 3 and player.money >= 50:
            player.production['raw'] += 1
            player.money -= 50
            player.action_points -= 3
            print(f"{player.name} researched and improved raw production")

    def take_loan(self):
        player = self.players[self.current_player]
        loan_amount = 100
        player.money += loan_amount
        player.loan += loan_amount
        print(f"{player.name} took a loan of ${loan_amount}")

    def end_turn(self):
        self.current_player = 1 - self.current_player
        self.players[self.current_player].action_points = 5
        if self.current_player == 0:
            self.turn += 1
            self.market.update()
        if self.turn > self.max_turns:
            self.end_game()

    def end_game(self):
        for player in self.players:
            player.money -= player.loan
        winner = max(self.players, key=lambda p: p.money)
        print(f"Game Over! {winner.name} wins with ${winner.money}!")
        pygame.quit()
        sys.exit()

    def draw(self):
        self.screen.fill(WHITE)
        
        player = self.players[self.current_player]
        info_text = [
            f"Turn {self.turn}/{self.max_turns} - {player.name}'s Turn",
            f"Money: ${player.money} (Loan: ${player.loan})",
            f"Action Points: {player.action_points}",
            f"Raw Goods: {player.goods['raw']}",
            f"Manufactured Goods: {player.goods['manufactured']}",
            f"Luxury Goods: {player.goods['luxury']}",
            "",
            "Market Prices:",
            f"Raw: ${self.market.goods['raw']['price']} (Demand: {self.market.goods['raw']['demand']})",
            f"Manufactured: ${self.market.goods['manufactured']['price']} (Demand: {self.market.goods['manufactured']['demand']})",
            f"Luxury: ${self.market.goods['luxury']['price']} (Demand: {self.market.goods['luxury']['demand']})"
        ]
        for i, text in enumerate(info_text):
            text_surface = self.font.render(text, True, BLACK)
            self.screen.blit(text_surface, (50, 50 + i*30))

        for button in self.buttons:
            button.draw(self.screen, self.font)

    def run(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return
                for button in self.buttons:
                    button.handle_event(event)

            self.draw()
            pygame.display.flip()
            self.clock.tick(60)

if __name__ == "__main__":
    game = EconomicGame()
    game.run()