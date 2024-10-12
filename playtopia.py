import pygame
import random
import spacy

# Initialize Pygame
pygame.init()

# Set up some constants
WIDTH, HEIGHT = 640, 480
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
BLACK = (0, 0, 0)
YELLOW = (255, 255, 0)
SKY_BLUE = (135, 206, 235)
ORANGE = (255, 165, 0)
GRAVITY = 1
JUMP_HEIGHT = -20  # Increased jump height
JUMP_ANIMATION_FRAMES = 30  # Increased number of frames for smoother animation

# Set up the display
screen = pygame.display.set_mode((WIDTH, HEIGHT))

# Set up the character
character_color = ORANGE
character_x, character_y = (WIDTH - 300) // 2 + 150, HEIGHT - 70 - 10  # Position the circle on top of the bar
character_radius = 20
character_speed = 2  # pixels per frame
bar_length = 300
bar_height = 10  # Reduced bar height
bar_x, bar_y = (WIDTH - bar_length) // 2, HEIGHT - bar_height - 50
is_jumping = False
initial_y = character_y  # Store the initial y-position at the center
velocity_x = 0
velocity_y = 0
move_count = 0  # count to slow down movement
afterimage_x, afterimage_y = character_x, character_y
jump_cooldown = 0
jump_peak = False
jump_animation_frame = 0
on_bar = True
jump_animation = []
jump_start_x = 0
jumping_while_moving = False

# Load the Spacy model
nlp = spacy.load("en_core_web_sm")

def process_command(command):
    try:
        doc = nlp(command)
        for token in doc:
            if token.text.lower() == "jump":
                if token.pos_ == "VERB":
                    return "jump"
            elif token.text.lower() == "move":
                if token.pos_ == "VERB":
                    if token.dep_ == "ROOT":
                        for child in token.children:
                            if child.text.lower() == "left":
                                return "move left"
                            elif child.text.lower() == "right":
                                return "move right"
            elif token.text.lower() == "change":
                if token.pos_ == "VERB":
                    for child in token.children:
                        if child.text.lower() == "color":
                            return "change color"
        return None
    except Exception as e:
        print(f"Error processing command: {e}")
        return None

def main():
    global character_x, character_y, character_color, is_jumping, initial_y, velocity_x, velocity_y, move_count, afterimage_x, afterimage_y, jump_cooldown, jump_peak, jump_animation_frame, on_bar, jump_animation, jump_start_x, jumping_while_moving
    clock = pygame.time.Clock()
    running = True
    colors = [RED, GREEN, BLUE, YELLOW, ORANGE]
    current_color_index = 0
    command = ""
    font = pygame.font.Font(None, 24)
    input_rect = pygame.Rect(10, HEIGHT - 40, WIDTH - 20, 30)

    # Display the title screen
    title_font = pygame.font.SysFont('Arial', 72)
    title_text = title_font.render("PLAYTOPIA", True, RED)
    title_rect = title_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 20))
    loading_font = pygame.font.SysFont('Arial', 36)
    loading_text = loading_font.render("Loading...", True, BLACK)
    loading_rect = loading_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 40))
    screen.fill(SKY_BLUE)
    screen.blit(title_text, title_rect)
    screen.blit(loading_text, loading_rect)
    dots = 0
    start_time = pygame.time.get_ticks()
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                return
        dots = (dots + 1) % 4
        loading_text = loading_font.render("Loading" + "." * dots, True, BLACK)
        screen.fill(SKY_BLUE)
        screen.blit(title_text, title_rect)
        screen.blit(loading_text, loading_rect)
        pygame.display.flip()
        clock.tick(10)
        if pygame.time.get_ticks() - start_time >= 5000:
            break

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:  # If the user presses a key
                if event.key == pygame.K_RETURN:  # If the user presses the return key
                    action = process_command(command)
                    if action == "move left":
                        velocity_x = -character_speed
                    elif action == "move right":
                        velocity_x = character_speed
                    elif action == "jump":
                        if not is_jumping and jump_cooldown == 0:
                            is_jumping = True
                            initial_y = character_y
                            jump_peak = False
                            jump_cooldown = 30
                            velocity_y = JUMP_HEIGHT
                            jump_animation_frame = 0
                            jump_start_x = character_x
                            on_bar = False
                            jumping_while_moving = True
                    elif action == "change color":
                        current_color_index = (current_color_index + 1) % len(colors)
                        character_color = colors[current_color_index]
                    command = ""
                elif event.key == pygame.K_BACKSPACE:
                    command = command[:-1]
                else:
                    command += event.unicode

        # Update character position based on jump animation
        if is_jumping:
            character_y += velocity_y
            velocity_y += GRAVITY
            jump_animation_frame += 1
            jump_animation.append((character_x, character_y))
            if jump_animation_frame >= JUMP_ANIMATION_FRAMES:
                # Bounce the character once
                velocity_y = -velocity_y * 0.8  # Reduce the velocity to make the bounce more realistic
                jump_animation_frame = 0
                is_jumping = False  # Reset the is_jumping flag
                jump_peak = False
                character_y = initial_y  # Return to the initial y-position
                character_x = jump_start_x  # Return to the initial x-position
                jump_animation = []
                jumping_while_moving = False

        # Update character position based on horizontal movement
        if velocity_x != 0 and not is_jumping:
            move_count += 1
            if move_count >= 5:
                afterimage_x, afterimage_y = character_x, character_y
                character_x += velocity_x
                move_count = 0
                if character_x < bar_x + character_radius:
                    character_x = bar_x + character_radius
                    velocity_x = 0
                elif character_x > bar_x + bar_length - character_radius:
                    character_x = bar_x + bar_length - character_radius
                    velocity_x = 0

        if jump_cooldown > 0:
            jump_cooldown -= 1

        if jump_peak:
            character_y += 5
            if character_y > bar_y - character_radius - 10:
                character_y = bar_y - character_radius - 10
                on_bar = True
                jump_peak = False

        # Update the character's position based on the velocity
        screen.fill(SKY_BLUE)
        pygame.draw.rect(screen, BLACK, (0, 0, WIDTH, 20))
        font = pygame.font.Font(None, 24)
        pygame.draw.rect(screen, (139, 69, 19), (bar_x, bar_y, bar_length, bar_height))  # brown color
        # Draw afterimage
        pygame.draw.circle(screen, (character_color[0] // 2, character_color[1] // 2, character_color[2] // 2),
                          (afterimage_x, afterimage_y), character_radius)
        # Draw jump animation
        for x, y in jump_animation:
            pygame.draw.circle(screen, (character_color[0] // 2, character_color[1] // 2, character_color[2] // 2),
                              (x, y), character_radius)
        if is_jumping:
            # Draw a shadow under the character to indicate jumping
            pygame.draw.circle(screen, (128, 128, 128), (character_x, character_y + 10), character_radius + 5, 2)
            if jumping_while_moving:
                pygame.draw.circle(screen, (character_color[0] // 2, character_color[1] // 2, character_color[2] // 2),
                                   (character_x, character_y), character_radius)
        pygame.draw.circle(screen, character_color, (character_x, character_y), character_radius)
        pygame.draw.rect(screen, BLACK, input_rect)
        if not command:
            text_surface = font.render("Type your command here...", True, WHITE)
            screen.blit(text_surface, (input_rect.x + 5, input_rect.y + 5))
        else:
            text_surface = font.render(command, True, WHITE)
            screen.blit(text_surface, (input_rect.x + 5, input_rect.y + 5))
        font = pygame.font.Font(None, 24)
        text_surface = font.render("Type 'move left', 'move right', 'jump', or 'change color' to control the circle!", True, WHITE)
        screen.blit(text_surface, (10, 5))
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    main()