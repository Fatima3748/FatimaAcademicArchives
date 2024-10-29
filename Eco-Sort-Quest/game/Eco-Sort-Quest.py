import pygame
import random
import os
import time

# Initialize Pygame
pygame.init()

# Constants
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 600
PLAYER_SIZE = 100
GARBAGE_SIZE = 50
DOG_SIZE = 50
ENERGY_ITEM_SIZE = 50
SNAKE_SIZE = 50
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BUTTON_COLOR = (173, 216, 230)
BUTTON_HOVER_COLOR = (135, 206, 250)
character_speed = 20
player_speed = 20
boosted_speed = player_speed * 3  # Boost speed when shift key is pressed
item_stack = [] # we will collect all item in this list
item_index = 0

# Global variables for the item throwing process
is_throwing = False
target_bin_index = None
throw_speed = 15

# Score tracking
score = 0
sorting_score = 0

button_sound = pygame.mixer.Sound('button.wav')
collect_sound = pygame.mixer.Sound('collect.wav')

def draw_button(text, x, y, width, height, active=False):
    color = BUTTON_HOVER_COLOR if active else BUTTON_COLOR
    pygame.draw.rect(screen, color, (x, y, width, height))
    text_surface = font.render(text, True, BLACK)
    screen.blit(text_surface, (x + (width - text_surface.get_width()) // 2, y + (height - text_surface.get_height()) // 2))
    return pygame.Rect(x, y, width, height)

# Create the screen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Eco Sort Quest Game")

# Load player GIF frames
player_frames = [pygame.image.load(f"frame_{i}_delay-0.07s_{i}.png") for i in range(4)]
for i in range(len(player_frames)):
    player_frames[i] = pygame.transform.scale(player_frames[i], (PLAYER_SIZE, PLAYER_SIZE))

# Load garbage images (plastic, paper, metal)
garbage_images = {
    "plastic": pygame.image.load("plastic-bottle.png"),
    "paper": pygame.image.load("paper.png"),
    "metal": pygame.image.load("tin-can.png"),
    "food": pygame.image.load("food.png"),
    "organic": pygame.image.load("organic.png")
}
for key in garbage_images:
    garbage_images[key] = pygame.transform.scale(garbage_images[key], (GARBAGE_SIZE, GARBAGE_SIZE))

# Load dog and snake images
dog_image = pygame.image.load("dog.png")
dog_image = pygame.transform.scale(dog_image, (DOG_SIZE, DOG_SIZE))

snake_image = pygame.image.load("snake.png")
snake_image = pygame.transform.scale(snake_image, (SNAKE_SIZE, SNAKE_SIZE))

# Load food.png for energy boost
food_image = pygame.image.load("food.png")
food_image = pygame.transform.scale(food_image, (ENERGY_ITEM_SIZE, ENERGY_ITEM_SIZE))

# Variables for player
player_x = SCREEN_WIDTH // 2 - PLAYER_SIZE // 2
player_y = SCREEN_HEIGHT - PLAYER_SIZE - 10

# Variables
garbage_speed = 5
dog_speed = 5
energy_speed = 5
snake_speed = 5
spawn_timer = 0
spawn_interval = 2000
score = 0
health = 25
energy_gained = 0  # Track energy gained from the energy item
plastic_collected = 0
paper_collected = 0
organic_collected = 0
metal_collected = 0
animals_killed = 0  # Track number of dogs killed
font = pygame.font.Font(None, 36)
frame_index = 0
animation_speed = 3
frame_counter = 0

# Load or create max score file
max_score_file = "max_score.txt"
if os.path.exists(max_score_file):
    with open(max_score_file, "r") as file:
        max_score = int(file.read())
else:
    max_score = 0

# Perspective street properties
road_top_width = 250
road_bottom_width = 800
road_color = (220, 220, 220)  # Light gray

# Gradient background colors
background_color_top = (135, 206, 250)
background_color_bottom = (34, 139, 34)

# Initialize empty lists for garbage, dogs, snakes, and energy items
garbage_list = []
dog_list = []
snake_list = []
energy_item_list = []

# Function to draw gradient background
def draw_gradient_background():
    for y in range(SCREEN_HEIGHT):
        color = (
            background_color_top[0] + (background_color_bottom[0] - background_color_top[0]) * y // SCREEN_HEIGHT,
            background_color_top[1] + (background_color_bottom[1] - background_color_top[1]) * y // SCREEN_HEIGHT,
            background_color_top[2] + (background_color_bottom[2] - background_color_top[2]) * y // SCREEN_HEIGHT
        )
        pygame.draw.line(screen, color, (0, y), (SCREEN_WIDTH, y))

# Function to prompt level selection with buttons
def select_level():
    screen.fill(WHITE)
    title_text = font.render("Select Game Level", True, BLACK)
    screen.blit(title_text, (SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2 - 150))

    # Draw buttons for level selection
    basic_button = draw_button("Basic", SCREEN_WIDTH // 2 - 75, SCREEN_HEIGHT // 2 - 50, 150, 50)
    intermediate_button = draw_button("Intermediate", SCREEN_WIDTH // 2 - 75, SCREEN_HEIGHT // 2 + 20, 150, 50)
    pro_button = draw_button("Pro", SCREEN_WIDTH // 2 - 75, SCREEN_HEIGHT // 2 + 90, 150, 50)

    pygame.display.flip()

    level_selected = None
    while level_selected is None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                if basic_button.collidepoint(event.pos):
                    level_selected = "basic"
                elif intermediate_button.collidepoint(event.pos):
                    level_selected = "intermediate"
                elif pro_button.collidepoint(event.pos):
                    level_selected = "pro"

        # Button hover effect
        mouse_pos = pygame.mouse.get_pos()
        draw_button("Basic", SCREEN_WIDTH // 2 - 75, SCREEN_HEIGHT // 2 - 50, 150, 50, basic_button.collidepoint(mouse_pos))
        draw_button("Intermediate", SCREEN_WIDTH // 2 - 75, SCREEN_HEIGHT // 2 + 20, 150, 50, intermediate_button.collidepoint(mouse_pos))
        draw_button("Pro", SCREEN_WIDTH // 2 - 75, SCREEN_HEIGHT // 2 + 90, 150, 50, pro_button.collidepoint(mouse_pos))

        pygame.display.flip()

    return level_selected

# Function to reset the game
def reset_game(level):
    global player_x, score, health, plastic_collected, paper_collected, metal_collected, animals_killed, energy_gained, garbage_list, dog_list, snake_list, energy_item_list, spawn_timer, garbage_speed, dog_speed, energy_speed, snake_speed
    player_x = SCREEN_WIDTH // 2 - PLAYER_SIZE // 2
    score = 0
    health = 25
    plastic_collected = 0
    paper_collected = 0
    metal_collected = 0
    animals_killed = 0
    energy_gained = 0
    garbage_list.clear()
    dog_list.clear()
    snake_list.clear()
    energy_item_list.clear()
    spawn_timer = pygame.time.get_ticks()

    # Adjust speeds based on level
    if level == "basic":
        garbage_speed = 5
        dog_speed = 5
        energy_speed = 5
        snake_speed = 5
    elif level == "intermediate":
        garbage_speed = 7
        dog_speed = 8
        energy_speed = 7
    elif level == "pro":
        garbage_speed = 9
        dog_speed = 10
        energy_speed = 9
        snake_speed = 9  # Snake only appears in Pro level

# Function to display the game over screen with statistics
def game_over_screen():
    global running

    screen.fill(WHITE)

    # Display final stats
    title_text = font.render("Game Over Statistics", True, RED)
    screen.blit(title_text, (SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 - 180))

    # Environmental savings based on collected garbage
    paper_weight = paper_collected * 1  # 1 kg per paper
    plastic_weight = plastic_collected * 0.1  # 0.1 kg per plastic bottle
    metal_weight = metal_collected * 0.1  # 0.1 kg per metal tin
    organic_weight = organic_collected * 0.1

    electricity_saved = (plastic_weight * 1.5) + (paper_weight * 2) + (metal_weight * 3)
    water_saved = (plastic_weight * 2.5) + (paper_weight * 3) + (metal_weight * 4)
    pollution_reduced = (plastic_weight * 1) + (paper_weight * 1.5) + (metal_weight * 2)

    # Add current score and max score to the stats
    stats_text = [
        f"Your Score: {score + sorting_score}",
        f"Max Score: {max_score}",
        f"Plastic Collected: {plastic_collected} (0.1 kg each)",
        f"Organic: {organic_collected} (0.1 kg each)",
        f"Paper Collected: {paper_collected} (1 kg each)",
        f"Metal Collected: {metal_collected} (0.1 kg each)",
        f"Animals Killed: {animals_killed}",
        f"Water Saved: {water_saved:.2f} liters",
        f"Pollution Reduced: {pollution_reduced:.2f} kg of CO2"
    ]

    # Display the stats in a well-aligned manner
    for i, line in enumerate(stats_text):
        stats_line = font.render(line, True, BLACK)
        screen.blit(stats_line, (SCREEN_WIDTH // 2 - 300, SCREEN_HEIGHT // 2 - 150 + i * 40))

    # Draw buttons for replay and quit in the top-right corner
    replay_button = draw_button("Replay", SCREEN_WIDTH - 200, 20, 150, 50)  # Adjust x, y to top-right corner
    quit_button = draw_button("Quit", SCREEN_WIDTH - 200, 90, 150, 50)      # Below the replay button

    pygame.display.flip()

    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                if replay_button.collidepoint(event.pos):
                    reset_game(level)  # Reset with the selected level
                    waiting = False
                elif quit_button.collidepoint(event.pos):
                    pygame.quit()
                    quit()

        # Button hover effect for replay and quit buttons
        mouse_pos = pygame.mouse.get_pos()
        draw_button("Replay", SCREEN_WIDTH - 200, 20, 150, 50, replay_button.collidepoint(mouse_pos))
        draw_button("Quit", SCREEN_WIDTH - 200, 90, 150, 50, quit_button.collidepoint(mouse_pos))

        pygame.display.flip()

def sortItem():
    import sys
    import pygame

    # Initialize Pygame
    pygame.init()

    # Screen dimensions
    SCREEN_WIDTH = 800
    SCREEN_HEIGHT = 600
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Eco Sort Quest Game")
    global item_stack 
    global item_index
    # Colors
    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)

    # Font for labels
    font = pygame.font.SysFont(None, 36)

    # Load images and scale them down
    image_paths = ["plastic-bin.png", "plastic-bin.png", "plastic-bin.png", "plastic-bin.png"]
    original_item_stack = item_stack
    item_stack = [img for img in item_stack]
    item_stack = [pygame.image.load(path) for path in item_stack]
    images = [pygame.image.load(path) for path in image_paths]
    
    # Define fixed dimensions for each image
    image_width = 100
    image_height = 100
    images = [pygame.transform.scale(img, (image_width, image_height)) for img in images]

    top_padding = 100

    # Calculate even spacing between images
    total_images = 4
    total_image_width = total_images * image_width
    remaining_space = SCREEN_WIDTH - total_image_width
    spacing = remaining_space // (total_images + 1)  # Even spacing between images

    # Labels for each image
    labels = ["plastic", "Organic", "Paper", "Metal"]

    # Load player image
    player_image = pygame.image.load("player.png")
    player_image = pygame.transform.scale(player_image, (100, 100))  # Scale player image
    player_rect = player_image.get_rect()

    # Set initial position for the player
    player_rect.x = SCREEN_WIDTH // 2 - player_rect.width // 2
    player_rect.y = SCREEN_HEIGHT - player_rect.height - 20  # Position at the bottom of the screen
    player_speed = 5
    max_speed = 15

    # Function to display the images and labels
    def display_images():
        x_pos = spacing  # Start from the left with spacing

        for i in range(4):
            # Display image
            screen.blit(images[i], (x_pos, top_padding))

            # Display label centered on the image
            label_text = font.render(labels[i], True, BLACK)
            label_x = x_pos + (image_width - label_text.get_width()) // 2  # Center label over the image
            label_y = top_padding + image_height + 10  # Position label just below the image
            screen.blit(label_text, (label_x, label_y))

            # Move x position for the next image
            x_pos += image_width + spacing

    # Main game loop
    def game_loop():
        global player_speed
        global item_index
        global sorting_score
        x_position = 0
        space_pressed = False
        clock = pygame.time.Clock()

        while item_index < len(item_stack):
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

            # Get key presses
            keys = pygame.key.get_pressed()

            # Move player left or right
            if keys[pygame.K_LEFT]:
                player_rect.x -= player_speed
                if player_rect.x < 0:
                    player_rect.x = 0
            if keys[pygame.K_RIGHT]:
                if player_rect.x > SCREEN_WIDTH-100:
                    player_rect.x = SCREEN_WIDTH-100
                player_rect.x += player_speed
            if keys[pygame.K_SPACE] and item_stack:  # Ensure stack is not empty
                if item_index < len(item_stack):
                    # Scale and display the current item
                    # stack_item = pygame.transform.scale(item_stack[item_index], (100, 100))
                    # screen.blit(stack_item, (SCREEN_WIDTH - 100, 0))
                    # Move to the next item in stack after displaying
                    
                    # pygame.display.flip()
                    stack_item = pygame.transform.scale(item_stack[item_index], (100, 100))
                    # screen.blit(stack_item, (SCREEN_WIDTH - 100, 0))
                    # Initial position for the animation
                    x_position = (player_rect.left + player_rect.right) / 2 -50
            
                    y_position = 400
                    space_pressed = True

                    for i in range(10):
                        # Clear the previous frame by drawing a small rectangle over it
                        # Update the y position to move the item upward
                        y_position = 400 - (25 * i)
       
                        pygame.draw.rect(screen, WHITE, (x_position, y_position, stack_item.get_width(), stack_item.get_height()))
                        #pygame.draw.rect(screen, WHITE, (SCREEN_WIDTH/2-300, 50, 300, 50))
                        # Draw the item at the new position
                        screen.blit(stack_item, (x_position, y_position))
                        #screen.blit(font.render("Sorting Score: "+str(sorting_score), True, BLACK), (SCREEN_WIDTH/2-300, 20))
                        pygame.display.flip()
                        # Delay for smooth animation
                        time.sleep(0.1)

            # # Update display after changes
            

            # Update the display
            if space_pressed and item_index < len(original_item_stack):
                print(original_item_stack[item_index])                        
                if x_position < 150 and original_item_stack[item_index] == "plastic-bottle.png":
                    print("=========================================")
                    sorting_score += 5
                elif x_position > 150 and  x_position < 300 and original_item_stack[item_index] == "organic.png":
                    sorting_score += 5
                elif x_position > 300 and  x_position < 450 and original_item_stack[item_index] == "paper.png":
                    sorting_score += 5
                elif x_position > 450 and original_item_stack[item_index] == "tin-can.png":
                    sorting_score += 5
                item_index += 1
            # Ensure player stays within screen boundaries
            if player_rect.left < 0:
                player_rect.left = 0
            if player_rect.right > SCREEN_WIDTH:
                player_rect.right = SCREEN_WIDTH
            space_pressed= False
            # Increase speed if Shift is pressed
            if keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]:
                player_speed = max_speed
            else:
                player_speed = 5

            # Clear the screen
            screen.fill(WHITE)
            # screen.blit(font.render("Sorting Score: ", True, BLACK), (SCREEN_WIDTH/2-200, 20))
            # screen.blit(font.render(str(sorting_score), True, BLACK), (SCREEN_WIDTH/2, 20))
            if item_index < len(original_item_stack):
                stack_item = pygame.transform.scale(item_stack[item_index], (100, 100))
            
            screen.blit(stack_item, (SCREEN_WIDTH - 100, 0))
            
            # Draw the images and labels
            display_images()

            # # Draw the player at the bottom
            screen.blit(player_image, player_rect)
            pygame.draw.rect(screen, WHITE, (SCREEN_WIDTH/2-300, 50, 300, 50))
            # Draw the item at the new position
            #screen.blit(stack_item, (x_position, y_position))
            screen.blit(font.render("sorting Score: "+str(sorting_score), True, BLACK), (SCREEN_WIDTH/2-300, 20))
            # Update the screen
            pygame.display.flip()

            # Frame rate
            clock.tick(60)

    # Start the game loop
    game_loop()
    
# Function to spawn hazards like snakes in pro level
def spawn_hazards(level):
    if level == "pro":
        if random.random() < 0.15:  # 15% chance of spawning a snake
            snake_list.append(pygame.Rect(random.randint(SCREEN_WIDTH // 2 - 300, SCREEN_WIDTH // 2 + 300), random.randint(-600, -30), SNAKE_SIZE, SNAKE_SIZE))

# Function to save the max score to a file
def save_max_score(new_score):
    global max_score
    if new_score > max_score:
        max_score = new_score
        with open(max_score_file, "w") as file:
            file.write(str(max_score))

# Function to handle collisions with snakes in pro level
def handle_snake_collision():
    global health
    for snake in snake_list[:]:
        snake.y += snake_speed  # Snake moves like a dog
        if snake.y > SCREEN_HEIGHT:
            snake_list.remove(snake)
        
        player_rect = pygame.Rect(player_x, player_y, PLAYER_SIZE, PLAYER_SIZE)
        if player_rect.colliderect(snake):
            health -= 15  # Snake causes 15 health reduction
            snake_list.remove(snake)
            if health <= 0:
                save_max_score(score+sorting_score)  # Save max score before ending the game
                print(item_stack)
                sortItem()
                game_over_screen()  # End game

# Main Game Loop
level = select_level()  # Get the selected level
reset_game(level)  # Initialize the game with the selected level settings

running = True
while running:
    # Draw the gradient background
    draw_gradient_background()

    # Handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Movement Controls
    keys = pygame.key.get_pressed()
    moving = False
    speed = boosted_speed if keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT] else player_speed
    if keys[pygame.K_LEFT] and player_x > (SCREEN_WIDTH // 2 - road_bottom_width // 2):
        player_x -= speed
        moving = True
    if keys[pygame.K_RIGHT] and player_x < (SCREEN_WIDTH // 2 + road_bottom_width // 2 - PLAYER_SIZE):
        player_x += speed
        moving = True

    # Update frame index if player is moving
    frame_counter += 1
    if frame_counter >= animation_speed:
        frame_counter = 0
        frame_index = (frame_index + 1) % len(player_frames)

    # Draw the road polygon
    road_top_left = (SCREEN_WIDTH // 2 - road_top_width // 2, 0)
    road_top_right = (SCREEN_WIDTH // 2 + road_top_width // 2, 0)
    road_bottom_left = (SCREEN_WIDTH // 2 - road_bottom_width // 2, SCREEN_HEIGHT)
    road_bottom_right = (SCREEN_WIDTH // 2 + road_bottom_width // 2, SCREEN_HEIGHT)
    pygame.draw.polygon(screen, road_color, [road_top_left, road_top_right, road_bottom_right, road_bottom_left])

    # Move garbage, dogs, and energy items down
    for garbage in garbage_list[:]:
        garbage[0].y += garbage_speed
        if garbage[0].y > SCREEN_HEIGHT:
            garbage_list.remove(garbage)

    # Move energy item down
    for eitem in energy_item_list[:]:
        eitem[0].y += energy_speed
        if eitem[0].y > SCREEN_HEIGHT:
            energy_item_list.remove(eitem)

    for dog in dog_list[:]:
        dog.y += dog_speed
        if dog.y > SCREEN_HEIGHT:
            dog_list.remove(dog)

        player_rect = pygame.Rect(player_x, player_y, PLAYER_SIZE, PLAYER_SIZE)
        if player_rect.colliderect(dog):
            health -= 5
            animals_killed += 1  # Track animals killed
            dog_list.remove(dog)
            if health <= 0:
                save_max_score(score+sorting_score)

                print(item_stack)
                sortItem()
                game_over_screen()  # Show game over screen with stats

    for garbage in garbage_list[:]:
        player_rect = pygame.Rect(player_x, player_y, PLAYER_SIZE, PLAYER_SIZE)
        
        # Get the garbage's rectangle
        garbage_rect = garbage[0]

        # Check if the player and garbage collide
        if player_rect.colliderect(garbage_rect):
            # Calculate the overlapping area using the clip method
            overlap_rect = player_rect.clip(garbage_rect)

            # Calculate the area of the overlap
            overlap_area = overlap_rect.width * overlap_rect.height

            # Calculate 90% of the area of the garbage object
            garbage_area = garbage_rect.width * garbage_rect.height
            required_overlap_area = (1 / 10) * garbage_area

            # Debugging: print when a collision is detected and when an item is collected
            print(f"Collision detected! Overlap area: {overlap_area} / {garbage_area} (required: {required_overlap_area})")

            # If the overlap area is greater than or equal to 2/3 of the garbage area, collect the garbage
            if overlap_area >= required_overlap_area:
                garbage_list.remove(garbage)

                # Handle different types of garbage
                if garbage[1] == "food":  # If the garbage is 'food', increase health
                    health += 2
                    pygame.mixer.Sound.play(button_sound)
                else:
                    pygame.mixer.Sound.play(collect_sound)
                    score += 10  # Only increase score for other types of garbage
                    if garbage[1] == "plastic":
                        plastic_collected += 1
                        item_stack.append("plastic-bottle.png")
                        print("Added 'plastic' to the item stack:", item_stack)  # Debugging
                    elif garbage[1] == "paper":
                        paper_collected += 1
                        item_stack.append("paper.png")
                        print("Added 'paper' to the item stack:", item_stack)  # Debugging
                    elif garbage[1] == "metal":
                        metal_collected += 1
                        item_stack.append("tin-can.png")
                        print("Added 'metal' to the item stack:", item_stack)  # Debugging
                    elif garbage[1] == "organic":
                        organic_collected += 1
                        item_stack.append("organic.png")
                        print("Added 'organic' to the item stack:", item_stack)  # Debugging


    # Move energy items down the screen and detect collection
    for energy_item in energy_item_list[:]:
        energy_item.y += energy_speed
        if energy_item.y > SCREEN_HEIGHT:
            energy_item_list.remove(energy_item)

        # Check for collision with the player
        if player_rect.colliderect(energy_item):
            health += 5  # Gain energy when collected
            energy_gained += 5  # Track total energy gained
            energy_item_list.remove(energy_item)

    # Consistent spawning of garbage, dogs, and energy items
    current_time = pygame.time.get_ticks()
    if current_time - spawn_timer > spawn_interval:
        garbage_type = random.choice(["plastic", "paper", "metal", "food", "organic"])  # Add 'food' as a garbage type
        garbage_rect = pygame.Rect(random.randint(SCREEN_WIDTH // 2 - 300, SCREEN_WIDTH // 2 + 300), random.randint(-600, -30), GARBAGE_SIZE, GARBAGE_SIZE)

        # Adjust flow based on selected level
        if level == "basic":
            # Normal flow
            garbage_list.append([garbage_rect, garbage_type])  # Append food type as well
            if len(dog_list) < 2:
                dog_list.append(pygame.Rect(random.randint(SCREEN_WIDTH // 2 - 300, SCREEN_WIDTH // 2 + 300), random.randint(-800, -100), DOG_SIZE, DOG_SIZE))
        elif level == "intermediate":
            # Increased dog flow
            garbage_list.append([garbage_rect, garbage_type])
            if len(dog_list) < 4:  # More dogs
                dog_list.append(pygame.Rect(random.randint(SCREEN_WIDTH // 2 - 300, SCREEN_WIDTH // 2 + 300), random.randint(-800, -100), DOG_SIZE, DOG_SIZE))
        elif level == "pro":
            # Pro level flow (dogs + snakes)
            garbage_list.append([garbage_rect, garbage_type])
            if len(dog_list) < 3:
                dog_list.append(pygame.Rect(random.randint(SCREEN_WIDTH // 2 - 300, SCREEN_WIDTH // 2 + 300), random.randint(-800, -100), DOG_SIZE, DOG_SIZE))
            spawn_hazards(level)  # Spawn snakes

        spawn_timer = current_time

    # Handle collisions (snakes in pro level)
    if level == "pro":
        handle_snake_collision()

    # Draw player, garbage, dogs, and energy items
    screen.blit(player_frames[frame_index], (player_x, player_y))
    for garbage in garbage_list:
        garbage_image = garbage_images[garbage[1]]
        screen.blit(garbage_image, (garbage[0].x, garbage[0].y))
    for dog in dog_list:
        screen.blit(dog_image, (dog.x, dog.y))

    # Draw snakes in pro level
    if level == "pro":
        for snake in snake_list:
            screen.blit(snake_image, (snake.x, snake.y))

    # Draw energy items (food.png for energy boost)
    for energy_item in energy_item_list:
        screen.blit(food_image, (energy_item.x, energy_item.y))  # Display food.png for energy boost

    # Display Score and Health
    score_text = font.render(f"Score: {score}", True, BLACK)
    screen.blit(score_text, (10, 10))
    health_text = font.render(f"Health: {health}", True, BLACK)
    screen.blit(health_text, (10, 50))

    # Update the display
    pygame.display.flip()
    pygame.time.Clock().tick(30)

# Quit Pygame

pygame.quit()