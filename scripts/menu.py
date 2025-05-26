import pygame
import os
import json

class Button:
    def __init__(self, x, y, width, height, text, font, action=None):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.font = font
        self.action = action
        self.hover = False
        
        # Colors
        self.bg_color = (50, 50, 50)
        self.hover_color = (80, 80, 80)
        self.text_color = (255, 255, 255)
    
    def draw(self, screen):
        # Draw button background
        color = self.hover_color if self.hover else self.bg_color
        pygame.draw.rect(screen, color, self.rect)
        pygame.draw.rect(screen, (200, 200, 200), self.rect, 2)  # Border
        
        # Draw text
        text_surf = self.font.render(self.text, True, self.text_color)
        text_rect = text_surf.get_rect(center=self.rect.center)
        screen.blit(text_surf, text_rect)
    
    def check_hover(self, pos):
        self.hover = self.rect.collidepoint(pos)
        return self.hover
    
    def check_click(self, pos):
        if self.rect.collidepoint(pos):
            return self.action
        return None


class Menu:
    def __init__(self, screen, width, height, game):
        self.screen = screen
        self.width = width
        self.height = height
        self.game = game
        
        # Load fonts
        self.font_title = pygame.font.SysFont(None, 72)
        self.font_large = pygame.font.SysFont(None, 48)
        self.font_medium = pygame.font.SysFont(None, 32)
        self.font_small = pygame.font.SysFont(None, 24)
        
        # Create buttons
        button_width = 200
        button_height = 50
        button_spacing = 20
        start_y = height // 2
        
        self.main_menu_buttons = [
            Button(width // 2 - button_width // 2, start_y, 
                  button_width, button_height, "Arcade Mode", self.font_medium, "arcade"),
            Button(width // 2 - button_width // 2, start_y + button_height + button_spacing, 
                  button_width, button_height, "Campaign Mode", self.font_medium, "campaign"),
            Button(width // 2 - button_width // 2, start_y + (button_height + button_spacing) * 2, 
                  button_width, button_height, "High Scores", self.font_medium, "high_scores"),
            Button(width // 2 - button_width // 2, start_y + (button_height + button_spacing) * 3, 
                  button_width, button_height, "Quit", self.font_medium, "quit")
        ]
        
        self.game_over_buttons = [
            Button(width // 2 - button_width // 2, start_y, 
                  button_width, button_height, "Play Again", self.font_medium, "restart"),
            Button(width // 2 - button_width // 2, start_y + button_height + button_spacing, 
                  button_width, button_height, "Main Menu", self.font_medium, "menu")
        ]
        
        self.pause_buttons = [
            Button(width // 2 - button_width // 2, start_y, 
                  button_width, button_height, "Resume", self.font_medium, "resume"),
            Button(width // 2 - button_width // 2, start_y + button_height + button_spacing, 
                  button_width, button_height, "Main Menu", self.font_medium, "menu")
        ]
        
        # High scores
        self.high_scores = self.load_high_scores()
        self.final_score = 0
        self.show_high_scores = False
    
    def load_high_scores(self):
        try:
            if os.path.exists("high_scores.json"):
                with open("high_scores.json", "r") as f:
                    return json.load(f)
            return []
        except:
            return []
    
    def save_high_scores(self):
        try:
            with open("high_scores.json", "w") as f:
                json.dump(self.high_scores, f)
        except:
            pass
    
    def add_high_score(self, score):
        self.high_scores.append(score)
        self.high_scores.sort(reverse=True)
        self.high_scores = self.high_scores[:10]  # Keep only top 10
        self.save_high_scores()
    
    def set_final_score(self, score):
        self.final_score = score
        self.add_high_score(score)
    
    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            # Check button hover
            for button in self.main_menu_buttons:
                button.check_hover(event.pos)
        
        elif event.type == pygame.MOUSEBUTTONDOWN:
            # Check button clicks
            for button in self.main_menu_buttons:
                action = button.check_click(event.pos)
                if action:
                    if action == "high_scores":
                        self.show_high_scores = not self.show_high_scores
                    else:
                        return action
        
        return None
    
    def handle_game_over_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            # Check button hover
            for button in self.game_over_buttons:
                button.check_hover(event.pos)
        
        elif event.type == pygame.MOUSEBUTTONDOWN:
            # Check button clicks
            for button in self.game_over_buttons:
                action = button.check_click(event.pos)
                if action:
                    return action
        
        return None
    
    def handle_pause_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            # Check button hover
            for button in self.pause_buttons:
                button.check_hover(event.pos)
        
        elif event.type == pygame.MOUSEBUTTONDOWN:
            # Check button clicks
            for button in self.pause_buttons:
                action = button.check_click(event.pos)
                if action:
                    return action
        
        return None
    
    def update(self):
        # Update menu animations or effects if needed
        pass
    
    def update_game_over(self):
        # Update game over screen animations if needed
        pass
    
    def update_pause(self):
        # Update pause screen animations if needed
        pass
    
    def draw(self):
        # Clear the screen
        self.screen.fill((0, 0, 0))
        
        # Draw starfield background
        if hasattr(self.game, 'starfield'):
            self.game.starfield.draw(self.screen)
        
        # Draw title
        title_text = self.font_title.render("ASTEROID DODGER", True, (255, 255, 255))
        self.screen.blit(title_text, (self.width // 2 - title_text.get_width() // 2, 100))
        
        if self.show_high_scores:
            # Draw high scores
            self.draw_high_scores()
        else:
            # Draw buttons
            for button in self.main_menu_buttons:
                button.draw(self.screen)
    
    def draw_game_over(self):
        # Draw semi-transparent overlay
        overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))
        
        # Draw game over text
        game_over_text = self.font_title.render("GAME OVER", True, (255, 50, 50))
        self.screen.blit(game_over_text, (self.width // 2 - game_over_text.get_width() // 2, 100))
        
        # Draw final score
        score_text = self.font_large.render(f"Score: {self.final_score}", True, (255, 255, 255))
        self.screen.blit(score_text, (self.width // 2 - score_text.get_width() // 2, 180))
        
        # Draw buttons
        for button in self.game_over_buttons:
            button.draw(self.screen)
    
    def draw_pause(self):
        # Draw semi-transparent overlay
        overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))
        
        # Draw pause text
        pause_text = self.font_title.render("PAUSED", True, (255, 255, 255))
        self.screen.blit(pause_text, (self.width // 2 - pause_text.get_width() // 2, 100))
        
        # Draw buttons
        for button in self.pause_buttons:
            button.draw(self.screen)
    
    def draw_high_scores(self):
        # Draw high scores title
        title_text = self.font_large.render("HIGH SCORES", True, (255, 255, 255))
        self.screen.blit(title_text, (self.width // 2 - title_text.get_width() // 2, 200))
        
        # Draw scores
        y = 250
        for i, score in enumerate(self.high_scores[:10]):
            score_text = self.font_medium.render(f"{i+1}. {score}", True, (255, 255, 255))
            self.screen.blit(score_text, (self.width // 2 - score_text.get_width() // 2, y))
            y += 30
        
        # Draw back button
        back_text = self.font_medium.render("Back to Menu", True, (255, 255, 255))
        back_rect = back_text.get_rect(center=(self.width // 2, y + 40))
        
        # Highlight if mouse is over
        mouse_pos = pygame.mouse.get_pos()
        if back_rect.collidepoint(mouse_pos):
            pygame.draw.rect(self.screen, (80, 80, 80), back_rect.inflate(20, 10))
            
            # Check for click
            if pygame.mouse.get_pressed()[0]:
                self.show_high_scores = False
        
        # Draw the text
        self.screen.blit(back_text, back_rect)
