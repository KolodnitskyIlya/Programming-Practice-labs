import pygame
from ecosystem import World, Position, initialize_world, Lumiere, Obscurite, Pauvre, TimeOfDay

WORLD_WIDTH = 30
WORLD_HEIGHT = 20
CELL_SIZE = 20

WINDOW_WIDTH = WORLD_WIDTH * CELL_SIZE
WINDOW_HEIGHT = WORLD_HEIGHT * CELL_SIZE + 80

COLORS = {
    'bg': (255, 255, 255),
    'Lumiere': (255, 255, 0),
    'Obscurite': (0, 0, 255),
    'pauvre': (255, 165, 0),
    'malheureux': (128, 0, 128),
    'autre': (128, 128, 128),
    'text': (0, 0, 0),
    'slider': (180, 180, 180),
    'handle': (100, 100, 100),
}

pygame.init()
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Ecosystem Simulator")
font = pygame.font.SysFont(None, 24)

world = World(WORLD_WIDTH, WORLD_HEIGHT)
initialize_world(world, plant_density=0.1, animal_density=0.05)

clock = pygame.time.Clock()


slider_rect = pygame.Rect(50, WINDOW_HEIGHT - 60, 400, 10)
handle_radius = 8


pause_button = pygame.Rect(slider_rect.right + 30, slider_rect.top - 10, 80, 30)
paused = False

def draw_slider(surface, time_hour):
    pygame.draw.rect(surface, COLORS['slider'], slider_rect)
    pos_x = slider_rect.x + int((time_hour / 23) * slider_rect.width)
    pygame.draw.circle(surface, COLORS['handle'], (pos_x, slider_rect.centery), handle_radius)

def draw_pause_button(surface, paused):
    color = (200, 200, 200)
    pygame.draw.rect(surface, color, pause_button)
    text = "Pause" if not paused else "Play"
    text_surf = font.render(text, True, (0, 0, 0))
    surface.blit(text_surf, (pause_button.x + 10, pause_button.y + 5))

def draw_world(surface, world):
    surface.fill(COLORS['bg'])
    for entity in world.entities:
        x, y = entity.position.x * CELL_SIZE, entity.position.y * CELL_SIZE

        if isinstance(entity, Lumiere):
            color = COLORS['Lumiere']
            pygame.draw.rect(surface, color, (x, y, CELL_SIZE, CELL_SIZE))
        elif isinstance(entity, Obscurite):
            color = COLORS['Obscurite']
            pygame.draw.rect(surface, color, (x, y, CELL_SIZE, CELL_SIZE))
        elif isinstance(entity, Pauvre):
            class_name = entity.__class__.__name__
            if class_name == "Malheureux":
                color = COLORS['malheureux']
            else:
                color = COLORS.get(class_name.lower(), COLORS['pauvre'])
            pygame.draw.circle(surface, color, (x + CELL_SIZE // 2, y + CELL_SIZE // 2), 5)
        else:
            pygame.draw.rect(surface, COLORS['autre'], (x, y, CELL_SIZE, CELL_SIZE))

 
    stats = f"Entities: {len(world.entities)} | Time: {world.time_of_day.name} ({world.time_hour}) | Day: {world.day_counter}"
    text_surface = font.render(stats, True, COLORS['text'])
    surface.blit(text_surface, (10, WINDOW_HEIGHT - 30))

    draw_slider(surface, world.time_hour)
    draw_pause_button(surface, paused)

def handle_slider_mouse(pos):
    if slider_rect.collidepoint(pos):
        rel_x = pos[0] - slider_rect.x
        percent = min(max(rel_x / slider_rect.width, 0), 1)
        return int(percent * 23)
    return None

def update_time_of_day(world):
    hour = world.time_hour
    if 6 <= hour < 12:
        world.time_of_day = TimeOfDay.MORNING
    elif 12 <= hour < 18:
        world.time_of_day = TimeOfDay.DAY
    elif 18 <= hour < 22:
        world.time_of_day = TimeOfDay.EVENING
    else:
        world.time_of_day = TimeOfDay.NIGHT

running = True
while running:
    clock.tick(10)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.MOUSEBUTTONDOWN:
            if pause_button.collidepoint(event.pos):
                paused = not paused
            else:
                new_hour = handle_slider_mouse(event.pos)
                if new_hour is not None:
                    world.time_hour = new_hour
                    update_time_of_day(world)

        elif event.type == pygame.MOUSEMOTION and pygame.mouse.get_pressed()[0]:
            new_hour = handle_slider_mouse(event.pos)
            if new_hour is not None:
                world.time_hour = new_hour
                update_time_of_day(world)

    if not paused:
        world.step()

    draw_world(screen, world)
    pygame.display.flip()

pygame.quit()