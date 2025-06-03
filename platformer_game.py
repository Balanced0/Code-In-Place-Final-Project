"""
Simple Platformer Game
Code in Place Final Project
Created with Tkinter Canvas
"""

import tkinter as tk
import random
import time

# Game constants
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
PLAYER_WIDTH = 30
PLAYER_HEIGHT = 50
PLATFORM_HEIGHT = 20
GRAVITY = 0.5
JUMP_FORCE = -12
MOVE_SPEED = 5

class PlatformerGame:
    def __init__(self, master):
        self.master = master
        self.master.title("Simple Platformer")
        self.master.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
        self.master.resizable(False, False)
        
        # Create canvas
        self.canvas = tk.Canvas(self.master, width=WINDOW_WIDTH, height=WINDOW_HEIGHT, bg="skyblue")
        self.canvas.pack()
        
        # Game variables
        self.game_running = False
        self.score = 0
        self.level = 1
        
        # Player properties
        self.player_x = 100
        self.player_y = 300
        self.velocity_y = 0
        self.velocity_x = 0
        self.on_ground = False
        self.facing_right = True
        
        # Controls
        self.left_pressed = False
        self.right_pressed = False
        
        # Platforms
        self.platforms = []
        
        # Create start menu
        self.show_start_menu()
        
        # Set up key bindings
        self.master.bind("<KeyPress>", self.key_press)
        self.master.bind("<KeyRelease>", self.key_release)
    
    def show_start_menu(self):
        self.canvas.delete("all")
        self.canvas.create_rectangle(0, 0, WINDOW_WIDTH, WINDOW_HEIGHT, fill="skyblue")
        self.canvas.create_text(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 3, 
                               text="SIMPLE PLATFORMER", font=("Arial", 30, "bold"), fill="white")
        self.canvas.create_text(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2, 
                               text="Press SPACE to start", font=("Arial", 20), fill="white")
        self.canvas.create_text(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 50, 
                               text="Controls: Arrow keys to move, Up to jump", 
                               font=("Arial", 14), fill="white")
    
    def start_game(self):
        self.game_running = True
        self.score = 0
        self.level = 1
        self.player_x = 100
        self.player_y = 300
        self.velocity_y = 0
        self.velocity_x = 0
        
        # Create initial platforms
        self.create_platforms()
        
        # Start game loop
        self.update()
    
    def create_platforms(self):
        self.platforms = []
        
        # Ground platform
        self.platforms.append({
            'x': 0,
            'y': WINDOW_HEIGHT - 50,
            'width': WINDOW_WIDTH,
            'height': PLATFORM_HEIGHT,
            'color': 'green'
        })
        
        # Add random platforms based on level
        num_platforms = 5 + self.level * 2
        for _ in range(num_platforms):
            platform_width = random.randint(70, 200)
            self.platforms.append({
                'x': random.randint(0, WINDOW_WIDTH - platform_width),
                'y': random.randint(100, WINDOW_HEIGHT - 100),
                'width': platform_width,
                'height': PLATFORM_HEIGHT,
                'color': 'brown'
            })
        
        # Add goal platform
        self.goal_platform = {
            'x': WINDOW_WIDTH - 100,
            'y': 100,
            'width': 80,
            'height': PLATFORM_HEIGHT,
            'color': 'gold'
        }
        self.platforms.append(self.goal_platform)
    
    def draw_game(self):
        self.canvas.delete("all")
        
        # Draw background
        self.canvas.create_rectangle(0, 0, WINDOW_WIDTH, WINDOW_HEIGHT, fill="skyblue")
        
        # Draw platforms
        for platform in self.platforms:
            self.canvas.create_rectangle(
                platform['x'], platform['y'],
                platform['x'] + platform['width'], platform['y'] + platform['height'],
                fill=platform['color'], outline=""
            )
        
        # Draw player
        player_color = "blue"
        self.canvas.create_rectangle(
            self.player_x, self.player_y,
            self.player_x + PLAYER_WIDTH, self.player_y + PLAYER_HEIGHT,
            fill=player_color, outline=""
        )
        
        # Draw eyes to show direction
        eye_size = 5
        if self.facing_right:
            self.canvas.create_oval(
                self.player_x + PLAYER_WIDTH - 10, self.player_y + 15,
                self.player_x + PLAYER_WIDTH - 10 + eye_size, self.player_y + 15 + eye_size,
                fill="white"
            )
        else:
            self.canvas.create_oval(
                self.player_x + 5, self.player_y + 15,
                self.player_x + 5 + eye_size, self.player_y + 15 + eye_size,
                fill="white"
            )
        
        # Draw score and level
        self.canvas.create_text(70, 30, text=f"Score: {self.score}", font=("Arial", 14), fill="black")
        self.canvas.create_text(70, 60, text=f"Level: {self.level}", font=("Arial", 14), fill="black")
    
    def check_platform_collision(self):
        self.on_ground = False
        player_bottom = self.player_y + PLAYER_HEIGHT
        
        for platform in self.platforms:
            # Check if player is above platform and falling
            if (self.velocity_y >= 0 and
                self.player_x + PLAYER_WIDTH > platform['x'] and
                self.player_x < platform['x'] + platform['width']):
                
                # Check if player's bottom is at or slightly below platform top
                platform_top = platform['y']
                if player_bottom >= platform_top and player_bottom <= platform_top + 10:
                    self.player_y = platform_top - PLAYER_HEIGHT
                    self.velocity_y = 0
                    self.on_ground = True
                    
                    # Check if this is the goal platform
                    if platform == self.goal_platform:
                        self.next_level()
    
    def next_level(self):
        self.level += 1
        self.score += 100
        self.player_x = 100
        self.player_y = 300
        self.velocity_y = 0
        self.create_platforms()
    
    def update(self):
        if not self.game_running:
            return
        
        # Apply horizontal movement based on key presses
        if self.left_pressed:
            self.velocity_x = -MOVE_SPEED
            self.facing_right = False
        elif self.right_pressed:
            self.velocity_x = MOVE_SPEED
            self.facing_right = True
        else:
            self.velocity_x = 0
        
        # Apply gravity
        self.velocity_y += GRAVITY
        
        # Update position
        self.player_x += self.velocity_x
        self.player_y += self.velocity_y
        
        # Check boundaries
        if self.player_x < 0:
            self.player_x = 0
        elif self.player_x + PLAYER_WIDTH > WINDOW_WIDTH:
            self.player_x = WINDOW_WIDTH - PLAYER_WIDTH
        
        # Check if player fell off the bottom
        if self.player_y > WINDOW_HEIGHT:
            self.game_over()
            return
        
        # Check platform collisions
        self.check_platform_collision()
        
        # Draw everything
        self.draw_game()
        
        # Continue game loop
        self.master.after(16, self.update)  # ~60 FPS
    
    def game_over(self):
        self.game_running = False
        self.canvas.delete("all")
        self.canvas.create_rectangle(0, 0, WINDOW_WIDTH, WINDOW_HEIGHT, fill="skyblue")
        self.canvas.create_text(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 3, 
                               text="GAME OVER", font=("Arial", 30, "bold"), fill="red")
        self.canvas.create_text(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2, 
                               text=f"Final Score: {self.score}", font=("Arial", 20), fill="white")
        self.canvas.create_text(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 50, 
                               text="Press SPACE to play again", font=("Arial", 16), fill="white")
    
    def key_press(self, event):
        key = event.keysym
        
        if not self.game_running:
            if key == "space":
                self.start_game()
            return
        
        if key == "Left":
            self.left_pressed = True
        elif key == "Right":
            self.right_pressed = True
        elif key == "Up" and self.on_ground:
            self.velocity_y = JUMP_FORCE
            self.on_ground = False
    
    def key_release(self, event):
        key = event.keysym
        
        if key == "Left":
            self.left_pressed = False
        elif key == "Right":
            self.right_pressed = False

# Main function to run the game
def main():
    root = tk.Tk()
    game = PlatformerGame(root)
    root.mainloop()

if __name__ == "__main__":
    main()
