from graphics import *
import random
import time

WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
PLAYER_WIDTH = 30
PLAYER_HEIGHT = 50
PLATFORM_HEIGHT = 20
GRAVITY = 0.5
JUMP_FORCE = -12
MOVE_SPEED = 5

class PlatformerGame:
    def __init__(self):
        self.win = GraphWin("Simple Platformer", WINDOW_WIDTH, WINDOW_HEIGHT)
        self.win.setBackground("skyblue")
        
        self.game_running = False
        self.score = 0
        self.level = 1
        
        self.player_x = 100
        self.player_y = 300
        self.velocity_y = 0
        self.velocity_x = 0
        self.on_ground = False
        self.facing_right = True
        
        self.left_pressed = False
        self.right_pressed = False
        self.up_pressed = False
        
        self.platforms = []
        self.platform_shapes = []
        self.player_shape = None
        self.player_eye = None
        self.score_text = None
        self.level_text = None
        
        self.show_start_menu()
        self.run_game_loop()
    
    def show_start_menu(self):
        title = Text(Point(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 3), "SIMPLE PLATFORMER")
        title.setSize(30)
        title.setStyle("bold")
        title.setTextColor("white")
        title.draw(self.win)
        
        start_text = Text(Point(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2), "Press SPACE to start")
        start_text.setSize(20)
        start_text.setTextColor("white")
        start_text.draw(self.win)
        
        controls_text = Text(Point(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 50), 
                           "Controls: Arrow keys to move, Up to jump")
        controls_text.setSize(14)
        controls_text.setTextColor("white")
        controls_text.draw(self.win)
        
        self.menu_items = [title, start_text, controls_text]
    
    def clear_menu(self):
        for item in self.menu_items:
            item.undraw()
    
    def start_game(self):
        self.clear_menu()
        self.game_running = True
        self.score = 0
        self.level = 1
        self.player_x = 100
        self.player_y = 300
        self.velocity_y = 0
        self.velocity_x = 0
        
        self.create_platforms()
        self.draw_game()
    
    def create_platforms(self):
        self.platforms = []
        
        self.platforms.append({
            'x': 0,
            'y': WINDOW_HEIGHT - 50,
            'width': WINDOW_WIDTH,
            'height': PLATFORM_HEIGHT,
            'color': 'green'
        })
        
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
        
        self.goal_platform = {
            'x': WINDOW_WIDTH - 100,
            'y': 100,
            'width': 80,
            'height': PLATFORM_HEIGHT,
            'color': 'gold'
        }
        self.platforms.append(self.goal_platform)
    
    def draw_game(self):
        if self.platform_shapes:
            for shape in self.platform_shapes:
                shape.undraw()
        
        self.platform_shapes = []
        
        for platform in self.platforms:
            rect = Rectangle(
                Point(platform['x'], platform['y']),
                Point(platform['x'] + platform['width'], platform['y'] + platform['height'])
            )
            rect.setFill(platform['color'])
            rect.setOutline(platform['color'])
            rect.draw(self.win)
            self.platform_shapes.append(rect)
        
        if self.player_shape:
            self.player_shape.undraw()
        if self.player_eye:
            self.player_eye.undraw()
        
        self.player_shape = Rectangle(
            Point(self.player_x, self.player_y),
            Point(self.player_x + PLAYER_WIDTH, self.player_y + PLAYER_HEIGHT)
        )
        self.player_shape.setFill("blue")
        self.player_shape.setOutline("blue")
        self.player_shape.draw(self.win)
        
        eye_size = 5
        if self.facing_right:
            self.player_eye = Circle(
                Point(self.player_x + PLAYER_WIDTH - 10 + eye_size/2, self.player_y + 15 + eye_size/2),
                eye_size/2
            )
        else:
            self.player_eye = Circle(
                Point(self.player_x + 5 + eye_size/2, self.player_y + 15 + eye_size/2),
                eye_size/2
            )
        self.player_eye.setFill("white")
        self.player_eye.draw(self.win)
        
        if self.score_text:
            self.score_text.undraw()
        if self.level_text:
            self.level_text.undraw()
        
        self.score_text = Text(Point(70, 30), f"Score: {self.score}")
        self.score_text.setSize(14)
        self.score_text.draw(self.win)
        
        self.level_text = Text(Point(70, 60), f"Level: {self.level}")
        self.level_text.setSize(14)
        self.level_text.draw(self.win)
    
    def check_platform_collision(self):
        self.on_ground = False
        player_bottom = self.player_y + PLAYER_HEIGHT
        
        for platform in self.platforms:
            if (self.velocity_y >= 0 and
                self.player_x + PLAYER_WIDTH > platform['x'] and
                self.player_x < platform['x'] + platform['width']):
                
                platform_top = platform['y']
                if player_bottom >= platform_top and player_bottom <= platform_top + 10:
                    self.player_y = platform_top - PLAYER_HEIGHT
                    self.velocity_y = 0
                    self.on_ground = True
                    
                    if platform == self.goal_platform:
                        self.next_level()
    
    def next_level(self):
        self.level += 1
        self.score += 100
        self.player_x = 100
        self.player_y = 300
        self.velocity_y = 0
        self.create_platforms()
        self.draw_game()
    
    def update(self):
        if not self.game_running:
            return
        
        if self.left_pressed:
            self.velocity_x = -MOVE_SPEED
            self.facing_right = False
        elif self.right_pressed:
            self.velocity_x = MOVE_SPEED
            self.facing_right = True
        else:
            self.velocity_x = 0
        
        if self.up_pressed and self.on_ground:
            self.velocity_y = JUMP_FORCE
            self.on_ground = False
            self.up_pressed = False
        
        self.velocity_y += GRAVITY
        
        self.player_x += self.velocity_x
        self.player_y += self.velocity_y
        
        if self.player_x < 0:
            self.player_x = 0
        elif self.player_x + PLAYER_WIDTH > WINDOW_WIDTH:
            self.player_x = WINDOW_WIDTH - PLAYER_WIDTH
        
        if self.player_y > WINDOW_HEIGHT:
            self.game_over()
            return
        
        self.check_platform_collision()
        self.draw_game()
    
    def game_over(self):
        self.game_running = False
        
        for shape in self.platform_shapes:
            shape.undraw()
        self.platform_shapes = []
        
        if self.player_shape:
            self.player_shape.undraw()
        if self.player_eye:
            self.player_eye.undraw()
        if self.score_text:
            self.score_text.undraw()
        if self.level_text:
            self.level_text.undraw()
        
        game_over_text = Text(Point(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 3), "GAME OVER")
        game_over_text.setSize(30)
        game_over_text.setStyle("bold")
        game_over_text.setTextColor("red")
        game_over_text.draw(self.win)
        
        score_text = Text(Point(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2), f"Final Score: {self.score}")
        score_text.setSize(20)
        score_text.setTextColor("white")
        score_text.draw(self.win)
        
        restart_text = Text(Point(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 50), "Press SPACE to play again")
        restart_text.setSize(16)
        restart_text.setTextColor("white")
        restart_text.draw(self.win)
        
        self.menu_items = [game_over_text, score_text, restart_text]
    
    def check_keys(self):
        key = self.win.checkKey()
        
        if key == "space" and not self.game_running:
            self.start_game()
        
        if not self.game_running:
            return
        
        if key == "Left":
            self.left_pressed = True
        elif key == "Right":
            self.right_pressed = True
        elif key == "Up":
            self.up_pressed = True
        elif key == "":
            self.left_pressed = False
            self.right_pressed = False
    
    def run_game_loop(self):
        while True:
            self.check_keys()
            self.update()
            time.sleep(0.016)  # ~60 FPS
            
            if self.win.isClosed():
                break

def main():
    game = PlatformerGame()

if __name__ == "__main__":
    main()
