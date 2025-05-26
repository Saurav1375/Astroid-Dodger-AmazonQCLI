import pygame
import sys
import os
from scripts.game import Game
from scripts.menu import Menu
from scripts.campaign import Campaign

# Initialize pygame
pygame.init()
pygame.mixer.init()

# Game constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

# Create the game window
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Asteroid Dodger")

# Set up the clock
clock = pygame.time.Clock()

def main():
    # Create game and menu instances
    game = Game(screen, SCREEN_WIDTH, SCREEN_HEIGHT)
    menu = Menu(screen, SCREEN_WIDTH, SCREEN_HEIGHT, game)
    
    # Game state
    current_state = "menu"  # Can be "menu", "game", "game_over", "campaign_select"
    
    # Create campaign instance
    campaign = None
    
    # Main game loop
    running = True
    while running:
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            # Pass events to the current state
            if current_state == "menu":
                menu_action = menu.handle_event(event)
                if menu_action == "arcade":
                    current_state = "game"
                    game.reset()
                    game.game_mode = "arcade"
                elif menu_action == "campaign":
                    current_state = "campaign_select"
                    campaign = Campaign(SCREEN_WIDTH, SCREEN_HEIGHT)
                elif menu_action == "quit":
                    running = False
            elif current_state == "game":
                game_action = game.handle_event(event)
                if game_action == "game_over":
                    current_state = "game_over"
                elif game_action == "pause":
                    current_state = "paused"
            elif current_state == "game_over":
                game_over_action = menu.handle_game_over_event(event)
                if game_over_action == "restart":
                    current_state = "game"
                    game.reset()
                elif game_over_action == "menu":
                    current_state = "menu"
            elif current_state == "paused":
                pause_action = menu.handle_pause_event(event)
                if pause_action == "resume":
                    current_state = "game"
                elif pause_action == "menu":
                    current_state = "menu"
        
        # Update the current state
        if current_state == "menu":
            menu.update()
        elif current_state == "game":
            game_status = game.update()
            if game_status == "game_over":
                current_state = "game_over"
                menu.set_final_score(game.score)
        elif current_state == "game_over":
            menu.update_game_over()
        elif current_state == "paused":
            menu.update_pause()
        elif current_state == "campaign_select":
            if campaign:
                campaign.update(1/60)  # Assuming 60 FPS
                campaign_action = campaign.handle_event(event)
                if campaign_action == "start_mission":
                    current_state = "game"
                    game.reset()
                    game.game_mode = "campaign"
                    game.set_campaign_mission(campaign.get_current_sector())
                elif campaign_action == "back_to_menu":
                    current_state = "menu"
        
        # Draw the current state
        if current_state == "menu":
            menu.draw()
        elif current_state == "game":
            game.draw()
            # If shop is active, draw it on top
            if game.shop_active:
                game.shop.draw(screen)
        elif current_state == "game_over":
            menu.draw_game_over()
        elif current_state == "paused":
            game.draw()
            menu.draw_pause()
        elif current_state == "campaign_select":
            if campaign:
                campaign.draw(screen)
        
        # Update the display
        pygame.display.flip()
        
        # Cap the frame rate
        clock.tick(FPS)
    
    # Clean up
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
