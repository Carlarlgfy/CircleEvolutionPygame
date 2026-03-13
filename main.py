#this will run the main game logic and import the creture and food classes
#first lets initialize everything
import pygame
import random
import json
import os
#initialize pygame
pygame.init()
#initialize the screen
screen = pygame.display.set_mode((820, 620))
#initialize the clock
clock = pygame.time.Clock()
step_timer = 0

step_interval = 1000  # milliseconds (1 second world step)

#day counter system
#tracks passing simulation days
day = 1
day_timer = 0
#base day length (normal speed reference)
#this will scale dynamically with simulation speed
base_day_length = 20000  # slower overall day progression

speed_mode = "normal"

#speed buttons positioned upper right
#aligned with margin from right edge
margin = 20
fast_button_rect = pygame.Rect(800 - margin - 70, 20, 70, 30)
normal_button_rect = pygame.Rect(fast_button_rect.x - 10 - 80, 20, 80, 30)
slow_button_rect = pygame.Rect(normal_button_rect.x - 10 - 60, 20, 60, 30)

#need to figure out how to intiialize time and how that
#will impact the creatures needs and food creation as well

#create a kill function 
#the kill function will should a show of the creatures that will die in an area if clicked
#and the creatures that are in the area will die and be removed from the screen
#the kill function will be a button at the bottom right of the screen and when clicked 
# it will change the mode to "kill" and then when t
# he player clicks on the screen it will kill, and it will show a 
# red circle where the player clicked to 
# indicate the area of effect of the kill function for 2 seconds
#the kill function will have a cooldown of 10 seconds and it will be indicated 
# by the button changing color to gray and then back to normal when the cooldown is over

from food import Food
foods = []

from creature import Creature
creatures = []

selected_creature = None
panel_rect = pygame.Rect(20, 480, 250, 130)
close_button_rect = pygame.Rect(panel_rect.right - 25, panel_rect.y + 5, 20, 20)

mode = "food"
font = pygame.font.SysFont(None, 24)

food_button_rect = pygame.Rect(620, 570, 80, 30)
creature_button_rect = pygame.Rect(710, 570, 100, 30)
kill_button_rect = pygame.Rect(540, 570, 70, 30)

 #selector button positioned above creature button
selector_button_rect = pygame.Rect(creature_button_rect.x, creature_button_rect.y - 35, 100, 30)

#save and exit button (top left under counters)
save_exit_rect = pygame.Rect(20, 70, 110, 28)

#
#auto feed toggle button system
#main toggle + adjustable feed intensity (1-10)
#auto feed main button
autofeed_button_rect = pygame.Rect(360, 570, 150, 30)
autofeed = False
autofeed_level = 5  # range 1-15
autofeed_timer = 0

#tracks how many auto-foods were spawned today
food_spawned_today = 0

running = True
#game state system
#menu or simulation
game_state = "menu"

#menu buttons

menu_new_rect = pygame.Rect(310, 220, 200, 50)
menu_load_rect = pygame.Rect(310, 290, 200, 50)
menu_quit_rect = pygame.Rect(310, 360, 200, 50)

#mode select buttons
mode_select_adam_rect = pygame.Rect(300, 230, 220, 50)
mode_select_free_rect = pygame.Rect(300, 300, 220, 50)
back_mode_rect = pygame.Rect(340, 380, 140, 40)

#new game setup UI
name_input_rect = pygame.Rect(300, 260, 220, 40)
start_game_rect = pygame.Rect(300, 320, 220, 45)
back_newgame_rect = pygame.Rect(340, 390, 140, 40)


world_name = ""
name_input_active = False

#game mode system
#determines special rule behavior

game_mode = None  # "adam" or "free"
adam_initialized = False
game_over = False

#notification popup system
notification_text = ""
notification_timer = 0


def world_name_exists(name):
    for f in SAVE_FILES:
        if os.path.exists(f):
            try:
                with open(f, "r") as file:
                    data = json.load(file)
                    if data.get("world_name", "") == name:
                        return True
            except:
                pass
    return False

#load menu buttons
slot1_rect = pygame.Rect(300, 200, 220, 50)
slot2_rect = pygame.Rect(300, 270, 220, 50)
slot3_rect = pygame.Rect(300, 340, 220, 50)
back_button_rect = pygame.Rect(340, 430, 140, 40)

#================ SAVE SYSTEM =================
SAVE_FILES = ["save_slot1.json", "save_slot2.json", "save_slot3.json"]

def get_empty_slot():
    for i, f in enumerate(SAVE_FILES):
        if not os.path.exists(f):
            return i
    return None

def save_world():
    slot = get_empty_slot()
    if slot is None:
        return

    data = {
        "world_name": world_name,
        "day": day,
        "creatures": [
            {
                "x": c.x,
                "y": c.y,
                "size": c.mature_size,
                "speed": c.speed,
                "awareness": c.awareness_radius,
                "maturation": c.maturation_time,
                "food_need": c.food_need
            }
            for c in creatures
        ],
        "foods": [
            {"x": f.x, "y": f.y}
            for f in foods
        ]
    }

    with open(SAVE_FILES[slot], "w") as f:
        json.dump(data, f)


# Load world from slot
def load_world(slot_index):
    global creatures, foods, world_name, day

    file = SAVE_FILES[slot_index]

    if not os.path.exists(file):
        return

    with open(file, "r") as f:
        data = json.load(f)

    world_name = data.get("world_name", "World")
    day = data.get("day", 1)

    creatures = []
    foods = []

    for c in data.get("creatures", []):
        creature = Creature((c["x"], c["y"]))
        creature.mature_size = c.get("size", creature.mature_size)
        creature.speed = c.get("speed", creature.speed)
        creature.awareness_radius = c.get("awareness", creature.awareness_radius)
        creature.maturation_time = c.get("maturation", creature.maturation_time)
        creature.food_need = c.get("food_need", creature.food_need)
        creatures.append(creature)

    for fdata in data.get("foods", []):
        foods.append(Food((fdata["x"], fdata["y"])))
while running:
    dt = clock.tick(60)
    step_timer += dt



    mouse_pos = pygame.mouse.get_pos()
    #handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # Menu click handling
        if event.type == pygame.MOUSEBUTTONDOWN and game_state == "menu":
            if menu_new_rect.collidepoint(event.pos):
                if get_empty_slot() is None:
                    notification_text = "No empty save slots"
                    notification_timer = 3000
                else:
                    game_state = "mode_select"
            elif menu_load_rect.collidepoint(event.pos):
                game_state = "load_menu"
            elif menu_quit_rect.collidepoint(event.pos):
                running = False

        #mode selection click handling
        if event.type == pygame.MOUSEBUTTONDOWN and game_state == "mode_select":
            if mode_select_adam_rect.collidepoint(event.pos):
                game_mode = "adam"
                game_state = "new_game"
            elif mode_select_free_rect.collidepoint(event.pos):
                game_mode = "free"
                game_state = "new_game"
            elif back_mode_rect.collidepoint(event.pos):
                game_state = "menu"

        #load menu click handling
        if event.type == pygame.MOUSEBUTTONDOWN and game_state == "load_menu":

            if back_button_rect.collidepoint(event.pos):
                game_state = "menu"

            elif slot1_rect.collidepoint(event.pos):
                if os.path.exists(SAVE_FILES[0]):
                    load_world(0)
                    game_state = "simulation"

            elif slot2_rect.collidepoint(event.pos):
                if os.path.exists(SAVE_FILES[1]):
                    load_world(1)
                    game_state = "simulation"

            elif slot3_rect.collidepoint(event.pos):
                if os.path.exists(SAVE_FILES[2]):
                    load_world(2)
                    game_state = "simulation"

        #adam game over click handling
        if event.type == pygame.MOUSEBUTTONDOWN and game_state == "adam_game_over":

            if back_button_rect.collidepoint(event.pos):
                creatures.clear()
                foods.clear()
                game_over = False
                adam_initialized = False
                game_state = "menu"

        #new game menu click handling
        if event.type == pygame.MOUSEBUTTONDOWN and game_state == "new_game":
            if name_input_rect.collidepoint(event.pos):
                name_input_active = True
            else:
                name_input_active = False

            if start_game_rect.collidepoint(event.pos):
                if world_name.strip() == "":
                    notification_text = "World must have a name"
                    notification_timer = 3000
                elif world_name_exists(world_name):
                    notification_text = "World name already exists"
                    notification_timer = 3000
                else:
                    game_state = "mode_select"

            if back_newgame_rect.collidepoint(event.pos):
                game_state = "menu"
        if event.type == pygame.MOUSEBUTTONDOWN:
            #save and exit button
            if save_exit_rect.collidepoint(event.pos) and game_state == "simulation":
                save_world()
                game_state = "menu"
            #creature selection logic (only active in select mode)
            if mode == "select":
                if selected_creature and close_button_rect.collidepoint(event.pos):
                    selected_creature = None
                else:
                    for creature in creatures:
                        dx = creature.x - event.pos[0]
                        dy = creature.y - event.pos[1]
                        if (dx*dx + dy*dy) ** 0.5 < creature.size:
                            selected_creature = creature
                            break

            if slow_button_rect.collidepoint(event.pos):
                speed_mode = "slow"
            elif normal_button_rect.collidepoint(event.pos):
                speed_mode = "normal"
            elif fast_button_rect.collidepoint(event.pos):
                speed_mode = "fast"
            elif kill_button_rect.collidepoint(event.pos):
                mode = "kill"
            elif food_button_rect.collidepoint(event.pos):
                mode = "food"
            elif creature_button_rect.collidepoint(event.pos):
                mode = "creature"
            elif selector_button_rect.collidepoint(event.pos):
                mode = "select"
            elif autofeed_button_rect.collidepoint(event.pos):
                #detect click position relative to button
                relative_x = event.pos[0] - autofeed_button_rect.x

                #right side of button handles +/-
                if relative_x > autofeed_button_rect.width - 40:
                    #split rightmost area into + and - halves
                    if event.pos[0] > autofeed_button_rect.right - 20:
                        #plus region
                        if autofeed_level < 15:
                            autofeed_level += 1
                    else:
                        #minus region
                        if autofeed_level > 1:
                            autofeed_level -= 1
                else:
                    #left side toggles autofeed on/off
                    autofeed = not autofeed
            else:
                if mode == "food":
                    foods.append(Food(event.pos))
                elif mode == "creature":
                    new_creature = Creature(event.pos)
                    new_creature.birth_day = day

                    #mark the first creature ever created as Adam
                    if len(creatures) == 0:
                        new_creature.adam_line = True
                        new_creature.is_adam = True
                        adam_initialized = True
                    else:
                        new_creature.is_adam = False

                    creatures.append(new_creature)
                elif mode == "kill":
                    # only kill if NOT clicking on any UI button
                    if not (
                        slow_button_rect.collidepoint(event.pos) or
                        normal_button_rect.collidepoint(event.pos) or
                        fast_button_rect.collidepoint(event.pos) or
                        food_button_rect.collidepoint(event.pos) or
                        creature_button_rect.collidepoint(event.pos) or
                        kill_button_rect.collidepoint(event.pos)
                    ):
                        for creature in creatures[:]:
                            dx = creature.x - event.pos[0]
                            dy = creature.y - event.pos[1]
                            if (dx*dx + dy*dy) ** 0.5 < 50:
                                creatures.remove(creature)

        if event.type == pygame.KEYDOWN and game_state == "new_game" and name_input_active:
            if event.key == pygame.K_BACKSPACE:
                world_name = world_name[:-1]
            elif len(world_name) < 20:
                world_name += event.unicode

    #================ MODE SELECT MENU =================
    if game_state == "mode_select":

        screen.fill((255,255,255))

        title_font = pygame.font.SysFont(None, 48)
        title = title_font.render("Choose Game Mode", True, (0,0,0))
        screen.blit(title, (280,150))

        pygame.draw.rect(screen,(200,200,200),mode_select_adam_rect)
        pygame.draw.rect(screen,(200,200,200),mode_select_free_rect)
        pygame.draw.rect(screen,(180,180,180),back_mode_rect)

        adam_text = font.render("Adam Mode",True,(0,0,0))
        free_text = font.render("Free Play",True,(0,0,0))
        back_text = font.render("Back",True,(0,0,0))

        screen.blit(adam_text,(mode_select_adam_rect.x+70,mode_select_adam_rect.y+15))
        screen.blit(free_text,(mode_select_free_rect.x+75,mode_select_free_rect.y+15))
        screen.blit(back_text,(back_mode_rect.x+45,back_mode_rect.y+10))

        pygame.display.flip()
        continue

    #================ MENU SCREEN =================
    if game_state == "menu":
        screen.fill((255,255,255))

        title_font = pygame.font.SysFont(None, 48)
        title = title_font.render("Circle Evolution", True, (0,0,0))
        screen.blit(title, (300, 150))

        pygame.draw.rect(screen, (200,200,200), menu_new_rect)
        pygame.draw.rect(screen, (200,200,200), menu_load_rect)
        pygame.draw.rect(screen, (200,200,200), menu_quit_rect)

        new_text = font.render("New Game", True, (0,0,0))
        load_text = font.render("Load Game", True, (0,0,0))
        quit_text = font.render("Quit", True, (0,0,0))

        screen.blit(new_text, (menu_new_rect.x + 55, menu_new_rect.y + 15))
        screen.blit(load_text, (menu_load_rect.x + 55, menu_load_rect.y + 15))
        screen.blit(quit_text, (menu_quit_rect.x + 80, menu_quit_rect.y + 15))

        pygame.display.flip()
        continue

    #================ LOAD MENU =================
    #================ NEW GAME MENU =================
    if game_state == "new_game":

        screen.fill((255,255,255))

        title_font = pygame.font.SysFont(None, 48)
        title = title_font.render("Create New World", True, (0,0,0))
        screen.blit(title, (270, 140))

        label = font.render("World Name", True, (0,0,0))
        screen.blit(label, (300, 230))

        pygame.draw.rect(screen, (255,255,255), name_input_rect)
        pygame.draw.rect(screen, (0,0,0), name_input_rect, 2)

        name_surface = font.render(world_name, True, (0,0,0))
        screen.blit(name_surface, (name_input_rect.x + 8, name_input_rect.y + 10))

        pygame.draw.rect(screen, (200,200,200), start_game_rect)
        pygame.draw.rect(screen, (180,180,180), back_newgame_rect)

        start_text = font.render("Start Game", True, (0,0,0))
        back_text = font.render("Back", True, (0,0,0))

        screen.blit(start_text, (start_game_rect.x + 60, start_game_rect.y + 12))
        screen.blit(back_text, (back_newgame_rect.x + 45, back_newgame_rect.y + 10))

        pygame.display.flip()
        continue
    if game_state == "load_menu":

        screen.fill((255,255,255))

        title_font = pygame.font.SysFont(None, 48)
        title = title_font.render("Load Game", True, (0,0,0))
        screen.blit(title, (320, 120))

        pygame.draw.rect(screen, (200,200,200), slot1_rect)
        pygame.draw.rect(screen, (200,200,200), slot2_rect)
        pygame.draw.rect(screen, (200,200,200), slot3_rect)

        pygame.draw.rect(screen, (180,180,180), back_button_rect)

        def get_slot_label(i):
            file = SAVE_FILES[i]
            if not os.path.exists(file):
                return "Empty"
            try:
                with open(file, "r") as f:
                    data = json.load(f)
                    return data.get("world_name", "Saved World")
            except:
                return "Saved"

        slot1_text = font.render(get_slot_label(0), True, (0,0,0))
        slot2_text = font.render(get_slot_label(1), True, (0,0,0))
        slot3_text = font.render(get_slot_label(2), True, (0,0,0))
        back_text = font.render("Back", True, (0,0,0))

        screen.blit(slot1_text, (slot1_rect.x + 60, slot1_rect.y + 15))
        screen.blit(slot2_text, (slot2_rect.x + 60, slot2_rect.y + 15))
        screen.blit(slot3_text, (slot3_rect.x + 60, slot3_rect.y + 15))

        screen.blit(back_text, (back_button_rect.x + 45, back_button_rect.y + 10))

        pygame.display.flip()
        continue

    #================ ADAM MODE GAME OVER =================
    if game_state == "adam_game_over":

        screen.fill((255,255,255))

        big_font = pygame.font.SysFont(None,60)

        line1 = big_font.render("Adam and Adam's descendants",True,(0,0,0))
        line2 = big_font.render("have died.",True,(0,0,0))
        line3 = big_font.render("GAME OVER",True,(0,0,0))

        screen.blit(line1,(180,200))
        screen.blit(line2,(340,270))
        screen.blit(line3,(320,340))

        pygame.draw.rect(screen,(200,200,200),back_button_rect)
        back_text = font.render("Main Menu",True,(0,0,0))
        screen.blit(back_text,(back_button_rect.x+25,back_button_rect.y+10))

        pygame.display.flip()
        continue

    #continuous mouse placement
    #allows holding mouse button to place multiple objects while dragging
    mouse_buttons = pygame.mouse.get_pressed()

    if mouse_buttons[0]:  # left mouse button held
        #prevent action when hovering over UI buttons
        if not (
            slow_button_rect.collidepoint(mouse_pos) or
            normal_button_rect.collidepoint(mouse_pos) or
            fast_button_rect.collidepoint(mouse_pos) or
            food_button_rect.collidepoint(mouse_pos) or
            creature_button_rect.collidepoint(mouse_pos) or
            kill_button_rect.collidepoint(mouse_pos) or
            autofeed_button_rect.collidepoint(mouse_pos)
        ):
            #continuous food placement
            if mode == "food":
                foods.append(Food(mouse_pos))

            #continuous kill while dragging
            elif mode == "kill":
                for creature in creatures[:]:
                    dx = creature.x - mouse_pos[0]
                    dy = creature.y - mouse_pos[1]
                    if (dx*dx + dy*dy) ** 0.5 < 50:
                        creatures.remove(creature)

    if speed_mode == "slow":
        step_interval = 100
    elif speed_mode == "normal":
        step_interval = 50
    elif speed_mode == "fast":
        step_interval = 25

    #scaled day progression logic
    #day speed scales proportionally with simulation speed
    #normal speed uses base_day_length
    speed_scale = step_interval / 50  # 50 is normal reference
    effective_day_length = base_day_length * speed_scale

    day_timer += dt
    if day_timer >= effective_day_length:
        day += 1
        day_timer = 0


        #reset daily auto-feed counter
        food_spawned_today = 0

        #spawn food for the new day according to level
        if autofeed:
            for _ in range(autofeed_level):
                x = random.randint(0, 800)
                y = random.randint(0, 600)
                foods.append(Food((x, y)))
            food_spawned_today = autofeed_level

    #ensure autofeed respects daily quota if toggled mid-day
    if autofeed and food_spawned_today < autofeed_level:
        remaining = autofeed_level - food_spawned_today
        for _ in range(remaining):
            x = random.randint(0, 800)
            y = random.randint(0, 600)
            foods.append(Food((x, y)))
        food_spawned_today = autofeed_level

    #update the game logic
    #draw everything
    screen.fill((255, 255, 255))

    for food in foods:
        food.draw(screen)

    # kill preview radius
    if mode == "kill":
        # do not show preview over UI buttons
        if not (
            slow_button_rect.collidepoint(mouse_pos) or
            normal_button_rect.collidepoint(mouse_pos) or
            fast_button_rect.collidepoint(mouse_pos) or
            food_button_rect.collidepoint(mouse_pos) or
            creature_button_rect.collidepoint(mouse_pos) or
            kill_button_rect.collidepoint(mouse_pos)
        ):
            pygame.draw.circle(screen, (200, 0, 0), mouse_pos, 50, 2)

    if step_timer >= step_interval:
        new_creatures = []

        for creature in creatures:
            child = creature.update(foods, creatures)
            if child:
                new_creatures.append(child)

        # remove dead creatures
        creatures = [c for c in creatures if c.alive]

        # add newborns
        for child in new_creatures:
            child.birth_day = day
            creatures.append(child)

        #adam mode extinction rule
        if game_mode == "adam" and adam_initialized and not game_over:
            adam_alive = any(c.adam_line and c.alive for c in creatures)
            if not adam_alive:
                game_over = True
                game_state = "adam_game_over"

        step_timer = 0

    for creature in creatures:
        creature.draw(screen)

    #highlight selected creature
    if selected_creature and selected_creature in creatures:
        pygame.draw.circle(screen, (255, 0, 0), (int(selected_creature.x), int(selected_creature.y)), selected_creature.size + 6, 2)
        pygame.draw.circle(screen, (255, 255, 0), (int(selected_creature.x), int(selected_creature.y)), selected_creature.size + 10, 2)

    #================ UI LAYER (drawn last so it appears on top) ================

    #day counter display (top left)
    day_text = font.render(f"Day {day}", True, (0, 0, 0))
    screen.blit(day_text, (20, 20))

    creature_count_text = font.render(f"# of creatures: {len(creatures)}", True, (0, 0, 0))
    screen.blit(creature_count_text, (20, 45))

    #save and exit button
    pygame.draw.rect(screen, (200,200,200), save_exit_rect)
    pygame.draw.rect(screen, (0,0,0), save_exit_rect, 1)

    save_text = font.render("Save & Exit", True, (0,0,0))
    screen.blit(save_text, (save_exit_rect.x + 10, save_exit_rect.y + 5))

    #selected creature info panel
    if selected_creature and selected_creature in creatures:

        #create a working panel rectangle so we can modify size for Adam lineage
        active_panel = panel_rect.copy()

        if hasattr(selected_creature, "adam_line") and selected_creature.adam_line:
            active_panel.height += 20
            active_panel.y -= 2

        pygame.draw.rect(screen, (220, 220, 220), active_panel)
        pygame.draw.rect(screen, (0, 0, 0), active_panel, 2)

        #close button
        close_rect = pygame.Rect(active_panel.right - 25, active_panel.y + 5, 20, 20)
        pygame.draw.rect(screen, (180, 50, 50), close_rect)
        x_text = font.render("X", True, (255,255,255))
        screen.blit(x_text, (close_rect.x + 5, close_rect.y + 2))

        # Adam lineage header
        header_offset = 0

        if hasattr(selected_creature, "adam_line") and selected_creature.adam_line:

            #only the first initialized creature is Adam
            if hasattr(selected_creature, "is_adam") and selected_creature.is_adam:
                label = "ADAM"
            else:
                label = "Descendant of Adam"
            header_text = font.render(label, True, (0,0,0))
            screen.blit(header_text, (active_panel.x + 28, active_panel.y + 8))
            #draw red blood drop indicator
            pygame.draw.circle(screen, (180,0,0), (active_panel.x + 15, active_panel.y + 16), 5)
            header_offset = 20

        #stat lines
        age_days = selected_creature.get_age_days(day)

        stats = [
            f"Size: {round(selected_creature.mature_size,1)}",
            f"Speed: {round(selected_creature.speed,2)}",
            f"Awareness: {round(selected_creature.awareness_radius,1)}",
            f"Maturation: {selected_creature.maturation_time}",
            f"Age (days): {age_days}"
        ]

        for i, line in enumerate(stats):
            stat_text = font.render(line, True, (0,0,0))
            screen.blit(stat_text, (active_panel.x + 10, active_panel.y + 10 + header_offset + i*18))

        #hunger bar visualization
        bar_x = active_panel.x + 80
        bar_y = active_panel.y + active_panel.height - 25
        bar_width = 120
        bar_height = 12

        hunger_label = font.render("Hunger", True, (0,0,0))
        screen.blit(hunger_label, (active_panel.x + 10, bar_y - 2))

        #draw background bar
        pygame.draw.rect(screen, (180,180,180), (bar_x, bar_y, bar_width, bar_height))

        #if creature is satiated show blue bar and SATIATED text
        if hasattr(selected_creature, "satiated_timer") and selected_creature.satiated_timer > 0:
            pygame.draw.rect(screen, (20,70,180), (bar_x, bar_y, bar_width, bar_height))

            small_font = pygame.font.SysFont(None, 18)
            satiated_text = small_font.render("SATIATED", True, (255,255,255))
            text_rect = satiated_text.get_rect(center=(bar_x + bar_width/2, bar_y + bar_height/2))
            screen.blit(satiated_text, text_rect)

        else:
            #0 = full, 200 = starvation
            hunger_ratio = min(max(selected_creature.food_need / 200, 0), 1)

            #calculate gradient color
            r = int(255 * hunger_ratio)
            g = int(255 * (1 - hunger_ratio))
            bar_color = (r, g, 0)

            #draw filled portion
            pygame.draw.rect(screen, bar_color, (bar_x, bar_y, int(bar_width * hunger_ratio), bar_height))

    #speed buttons
    if speed_mode == "slow":
        pygame.draw.rect(screen, (40, 60, 120), slow_button_rect)
    else:
        pygame.draw.rect(screen, (200, 200, 200), slow_button_rect)

    if speed_mode == "normal":
        pygame.draw.rect(screen, (40, 60, 120), normal_button_rect)
    else:
        pygame.draw.rect(screen, (200, 200, 200), normal_button_rect)

    if speed_mode == "fast":
        pygame.draw.rect(screen, (40, 60, 120), fast_button_rect)
    else:
        pygame.draw.rect(screen, (200, 200, 200), fast_button_rect)

    slow_text = font.render(">", True, (255,255,255) if speed_mode == "slow" else (0,0,0))
    normal_text = font.render(">>", True, (255,255,255) if speed_mode == "normal" else (0,0,0))
    fast_text = font.render(">>>", True, (255,255,255) if speed_mode == "fast" else (0,0,0))

    screen.blit(slow_text, (slow_button_rect.x + 20, slow_button_rect.y + 5))
    screen.blit(normal_text, (normal_button_rect.x + 25, normal_button_rect.y + 5))
    screen.blit(fast_text, (fast_button_rect.x + 20, fast_button_rect.y + 5))

    #autofeed button rendering with inline +/- controls
    if autofeed:
        pygame.draw.rect(screen, (40, 120, 40), autofeed_button_rect)
        text_color = (255, 255, 255)
    else:
        pygame.draw.rect(screen, (200, 200, 200), autofeed_button_rect)
        text_color = (0, 0, 0)

    autofeed_text = font.render(f"Auto-Feed {autofeed_level}", True, text_color)
    screen.blit(autofeed_text, (autofeed_button_rect.x + 10, autofeed_button_rect.y + 5))

    minus_text = font.render("-", True, text_color)
    plus_text = font.render("+", True, text_color)

    screen.blit(minus_text, (autofeed_button_rect.right - 35, autofeed_button_rect.y + 5))
    screen.blit(plus_text, (autofeed_button_rect.right - 18, autofeed_button_rect.y + 5))

    #bottom right buttons
    if mode == "kill":
        pygame.draw.rect(screen, (120, 40, 40), kill_button_rect)
        kill_text = font.render("Kill", True, (255, 255, 255))
    else:
        pygame.draw.rect(screen, (200, 200, 200), kill_button_rect)
        kill_text = font.render("Kill", True, (0, 0, 0))
    screen.blit(kill_text, (kill_button_rect.x + 15, kill_button_rect.y + 5))

    if mode == "food":
        pygame.draw.rect(screen, (40, 60, 120), food_button_rect)
        pygame.draw.rect(screen, (200, 200, 200), creature_button_rect)
        pygame.draw.rect(screen, (200, 200, 200), selector_button_rect)
    elif mode == "creature":
        pygame.draw.rect(screen, (200, 200, 200), food_button_rect)
        pygame.draw.rect(screen, (40, 60, 120), creature_button_rect)
        pygame.draw.rect(screen, (200, 200, 200), selector_button_rect)
    elif mode == "select":
        pygame.draw.rect(screen, (200, 200, 200), food_button_rect)
        pygame.draw.rect(screen, (200, 200, 200), creature_button_rect)
        pygame.draw.rect(screen, (40, 60, 120), selector_button_rect)
    else:
        pygame.draw.rect(screen, (200, 200, 200), food_button_rect)
        pygame.draw.rect(screen, (200, 200, 200), creature_button_rect)
        pygame.draw.rect(screen, (200, 200, 200), selector_button_rect)

    if mode == "food":
        food_text = font.render("Food", True, (255, 255, 255))
        creature_text = font.render("Creature", True, (0, 0, 0))
    elif mode == "creature":
        food_text = font.render("Food", True, (0, 0, 0))
        creature_text = font.render("Creature", True, (255, 255, 255))
    else:
        food_text = font.render("Food", True, (0, 0, 0))
        creature_text = font.render("Creature", True, (0, 0, 0))

    screen.blit(food_text, (food_button_rect.x + 15, food_button_rect.y + 5))
    screen.blit(creature_text, (creature_button_rect.x + 10, creature_button_rect.y + 5))

    selector_text = font.render("Select", True, (255,255,255) if mode == "select" else (0,0,0))
    screen.blit(selector_text, (selector_button_rect.x + 15, selector_button_rect.y + 5))

    #notification popup (top right)
    if notification_timer > 0:
        notification_timer -= dt

        popup_rect = pygame.Rect(560, 10, 240, 40)
        pygame.draw.rect(screen, (220,220,220), popup_rect)
        pygame.draw.rect(screen, (0,0,0), popup_rect, 2)

        note_text = font.render(notification_text, True, (0,0,0))
        screen.blit(note_text, (popup_rect.x + 10, popup_rect.y + 10))

    #updating screen
    pygame.display.flip()

#quit pygame
pygame.quit()