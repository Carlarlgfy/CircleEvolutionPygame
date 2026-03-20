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

paused = False  # global simulation pause state

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
pause_button_rect = pygame.Rect(slow_button_rect.x - 10 - 80, 20, 80, 30)

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
panel_rect = pygame.Rect(10, 380, 240, 180)
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

# Swap positions of New Game and How to Play
menu_new_rect = pygame.Rect(310, 360, 200, 50)
menu_load_rect = pygame.Rect(310, 290, 200, 50)
menu_info_rect = pygame.Rect(310, 220, 200, 50)
menu_quit_rect = pygame.Rect(310, 440, 200, 50)

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
manual_food_used = False
game_won = False
clean_days = 0

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

delete_button_rect = pygame.Rect(540, 430, 120, 40)
delete_mode = False

#================ SAVE SYSTEM =================
SAVE_FILES = ["save_slot1.json", "save_slot2.json", "save_slot3.json"]
current_save_slot = None  # tracks which slot the current world belongs to

def get_empty_slot():
    for i, f in enumerate(SAVE_FILES):
        if not os.path.exists(f):
            return i
    return None

def save_world():
    global current_save_slot

    # If this world already belongs to a slot, overwrite it
    if current_save_slot is not None:
        slot = current_save_slot
    else:
        slot = get_empty_slot()
        if slot is None:
            return
        # remember the slot for future saves
        current_save_slot = slot

    data = {
        "world_name": world_name,
        "game_mode": game_mode,
        "day": day,
        "adam_initialized": adam_initialized,
        "autofeed": autofeed,
        "autofeed_level": autofeed_level,
        "creatures": [
            {
                "x": c.x,
                "y": c.y,
                "size": getattr(c, "size", c.mature_size),
                "genes": {
                    "mature_size": c.mature_size,
                    "color": c.color,
                    "speed": c.speed,
                    "awareness": c.awareness_radius,
                    "maturation_time": c.maturation_time,
                    "hunger_limit": getattr(c, "hunger_limit", c.food_need),
                    "energy": c.energy,
                    "lifespan": getattr(c, "lifespan", None),
                    "adam_line": getattr(c, "adam_line", False)
                },
                "generation": getattr(c, "generation", 1),
                "is_adam": getattr(c, "is_adam", False),
                "birth_day": getattr(c, "birth_day", 1),
                "has_reproduced": getattr(c, "has_reproduced", False)
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
    global creatures, foods, world_name, day, game_mode, adam_initialized, autofeed, autofeed_level, game_over, selected_creature, current_save_slot

    file = SAVE_FILES[slot_index]

    if not os.path.exists(file):
        return

    with open(file, "r") as f:
        data = json.load(f)
    current_save_slot = slot_index  # remember which slot this world came from

    world_name = data.get("world_name", "World")
    game_mode = data.get("game_mode", "free")
    adam_initialized = data.get("adam_initialized", False)
    autofeed = data.get("autofeed", False)
    autofeed_level = data.get("autofeed_level", 5)
    day = data.get("day", 1)

    #reset runtime state when loading
    game_over = False
    selected_creature = None

    creatures = []
    foods = []

    for c in data.get("creatures", []):
        genes = c.get("genes", {})
        creature = Creature((c["x"], c["y"]), genes)
        creature.generation = c.get("generation", 1)
        creature.is_adam = c.get("is_adam", False)
        creature.birth_day = c.get("birth_day", day)
        creature.has_reproduced = c.get("has_reproduced", False)
        # restore current growth stage
        if "size" in c:
            creature.size = c["size"]
        creatures.append(creature)

    #ensure Adam lineage state is consistent after loading
    if game_mode == "adam":
        adam_initialized = any(c.adam_line for c in creatures)

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
                    current_save_slot = None  # ensure a new world does not reuse an old save slot
                    clean_days = 0
                    game_state = "mode_select"
                    continue
            elif menu_info_rect.collidepoint(event.pos):
                game_state = "instructions"
                continue
            elif menu_load_rect.collidepoint(event.pos):
                game_state = "load_menu"
            elif menu_quit_rect.collidepoint(event.pos):
                running = False

        # Instructions screen click handling
        if event.type == pygame.MOUSEBUTTONDOWN and game_state == "instructions":
            game_state = "menu"

        #mode selection click handling
        if event.type == pygame.MOUSEBUTTONDOWN and game_state == "mode_select":
            if mode_select_adam_rect.collidepoint(event.pos):
                game_mode = "adam"
                game_state = "new_game"
                continue
            elif mode_select_free_rect.collidepoint(event.pos):
                game_mode = "free"
                game_state = "new_game"
                continue
            elif back_mode_rect.collidepoint(event.pos):
                game_state = "menu"
                continue

        #load menu click handling
        if event.type == pygame.MOUSEBUTTONDOWN and game_state == "load_menu":

            if back_button_rect.collidepoint(event.pos):
                paused = False
                game_state = "menu"

            elif delete_button_rect.collidepoint(event.pos):
                delete_mode = not delete_mode

            elif slot1_rect.collidepoint(event.pos):
                if delete_mode:
                    if os.path.exists(SAVE_FILES[0]):
                        os.remove(SAVE_FILES[0])
                else:
                    if os.path.exists(SAVE_FILES[0]):
                        load_world(0)
                        paused = True
                        game_state = "simulation"

            elif slot2_rect.collidepoint(event.pos):
                if delete_mode:
                    if os.path.exists(SAVE_FILES[1]):
                        os.remove(SAVE_FILES[1])
                else:
                    if os.path.exists(SAVE_FILES[1]):
                        load_world(1)
                        paused = True
                        game_state = "simulation"

            elif slot3_rect.collidepoint(event.pos):
                if delete_mode:
                    if os.path.exists(SAVE_FILES[2]):
                        os.remove(SAVE_FILES[2])
                else:
                    if os.path.exists(SAVE_FILES[2]):
                        load_world(2)
                        paused = True
                        game_state = "simulation"

        #adam game over click handling
        if event.type == pygame.MOUSEBUTTONDOWN and game_state == "adam_game_over":

            if back_button_rect.collidepoint(event.pos):
                creatures.clear()
                foods.clear()

                game_over = False
                game_won = False

                adam_initialized = False
                manual_food_used = False
                clean_days = 0

                day = 1
                selected_creature = None

                current_save_slot = None

                paused = False
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
                    # Reset world state for a brand new game
                    creatures.clear()
                    foods.clear()

                    day = 1
                    adam_initialized = False
                    game_over = False

                    selected_creature = None

                    # reset save slot tracking for new world
                    current_save_slot = None

                    # Reset runtime state for new game
                    manual_food_used = False
                    game_won = False
                    clean_days = 0
                    autofeed = False
                    autofeed_level = 5

                    paused = False
                    game_state = "simulation"

            if back_newgame_rect.collidepoint(event.pos):
                game_state = "menu"
        if event.type == pygame.MOUSEBUTTONDOWN and game_state == "simulation":
            #save and exit button
            if save_exit_rect.collidepoint(event.pos) and game_state == "simulation":
                paused = True
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
            elif pause_button_rect.collidepoint(event.pos):
                paused = not paused
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
                    manual_food_used = True
                    clean_days = 0
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
            elif len(world_name) < 10:
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
        pygame.draw.rect(screen, (200,200,200), menu_info_rect)
        pygame.draw.rect(screen, (200,200,200), menu_quit_rect)

        new_text = font.render("New Game", True, (0,0,0))
        load_text = font.render("Load Game", True, (0,0,0))
        info_text = font.render("How to Play", True, (0,0,0))
        quit_text = font.render("Quit", True, (0,0,0))

        screen.blit(new_text, (menu_new_rect.x + 55, menu_new_rect.y + 15))
        screen.blit(load_text, (menu_load_rect.x + 55, menu_load_rect.y + 15))
        screen.blit(info_text, (menu_info_rect.x + 50, menu_info_rect.y + 15))
        screen.blit(quit_text, (menu_quit_rect.x + 80, menu_quit_rect.y + 15))

        pygame.display.flip()
        continue

    #================ INSTRUCTIONS SCREEN =================
    if game_state == "instructions":

        screen.fill((255,255,255))

        lines = [
            "Welcome to the Circle Evolution Game. This game simulates the genetics",
            "of organisms in a small environment. Each creature has 9 genetic traits:",
            "mature_size, color, speed, awareness_radius, lifespan,",
            "maturation_time, hunger_limit, energy, adam_line.",
            "Each of these affect the creatures ability to survive.",
            "",
            "Some are cosmetic like color and adam_line, but they still affect how",
            "the player views and interacts with creatures using food and kill tools.",
            "",
            "In freeplay you can create as many creatures as you want and experiment.",
            "There are no win or lose conditions.",
            "",
            "In Adam mode you must keep the adam_line alive.",
            "Win: survive 25 days without placing food.",
            "Lose: adam_line goes extinct.",
            "",
            "The goal is to experiment with breeding and behavior.",
            "I hope you enjoy."
        ]

        for i, line in enumerate(lines):
            text = font.render(line, True, (0,0,0))
            screen.blit(text, (40, 80 + i*25))

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

        #border changes color when active
        border_color = (60,60,60) if name_input_active else (0,0,0)
        pygame.draw.rect(screen, border_color, name_input_rect, 2)

        name_surface = font.render(world_name, True, (0,0,0))
        screen.blit(name_surface, (name_input_rect.x + 8, name_input_rect.y + 10))

        #blinking caret (text cursor)
        if name_input_active:
            if (pygame.time.get_ticks() // 500) % 2 == 0:
                caret_x = name_input_rect.x + 8 + name_surface.get_width() + 2
                caret_y = name_input_rect.y + 8
                pygame.draw.line(screen, (120,120,120), (caret_x, caret_y), (caret_x, caret_y + 22), 2)

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

        if delete_mode:
            pygame.draw.rect(screen, (180,60,60), delete_button_rect)
        else:
            pygame.draw.rect(screen, (200,200,200), delete_button_rect)

        def get_slot_label(i):
            file = SAVE_FILES[i]
            if not os.path.exists(file):
                return ("Empty", "")

            try:
                with open(file, "r") as f:
                    data = json.load(f)

                name = data.get("world_name", "Saved World")
                mode = data.get("game_mode", "free")

                if mode == "adam":
                    mode_text = "Adam Mode"
                else:
                    mode_text = "Free Play"

                return (name[:10], mode_text)
            except:
                return ("Saved", "")

        name1, mode1 = get_slot_label(0)
        name2, mode2 = get_slot_label(1)
        name3, mode3 = get_slot_label(2)

        slot1_text = font.render(name1, True, (0,0,0))
        slot2_text = font.render(name2, True, (0,0,0))
        slot3_text = font.render(name3, True, (0,0,0))

        slot1_mode = font.render(mode1, True, (80,80,80))
        slot2_mode = font.render(mode2, True, (80,80,80))
        slot3_mode = font.render(mode3, True, (80,80,80))

        back_text = font.render("Back", True, (0,0,0))

        screen.blit(slot1_text, (slot1_rect.x + 60, slot1_rect.y + 8))
        screen.blit(slot1_mode, (slot1_rect.x + 60, slot1_rect.y + 28))

        screen.blit(slot2_text, (slot2_rect.x + 60, slot2_rect.y + 8))
        screen.blit(slot2_mode, (slot2_rect.x + 60, slot2_rect.y + 28))

        screen.blit(slot3_text, (slot3_rect.x + 60, slot3_rect.y + 8))
        screen.blit(slot3_mode, (slot3_rect.x + 60, slot3_rect.y + 28))

        screen.blit(back_text, (back_button_rect.x + 45, back_button_rect.y + 10))

        delete_text = font.render("Delete", True, (255,255,255) if delete_mode else (0,0,0))
        screen.blit(delete_text, (delete_button_rect.x + 25, delete_button_rect.y + 10))

        pygame.display.flip()
        continue

    #================ ADAM MODE GAME OVER =================
    if game_state == "adam_game_over":

        screen.fill((255,255,255))

        big_font = pygame.font.SysFont(None,60)

        if game_won:
            line1 = big_font.render("ADAM LINE SURVIVED",True,(0,0,0))
            line2 = big_font.render("25 DAYS COMPLETED",True,(0,0,0))
            line3 = big_font.render("YOU WIN",True,(0,120,0))
        else:
            line1 = big_font.render("Adam and Adam's descendants",True,(0,0,0))
            line2 = big_font.render("have died.",True,(0,0,0))
            line3 = big_font.render("GAME OVER",True,(0,0,0))

        screen.blit(line1,(180,200))
        screen.blit(line2,(300,270))
        screen.blit(line3,(320,340))

        pygame.draw.rect(screen,(200,200,200),back_button_rect)
        back_text = font.render("Main Menu",True,(0,0,0))
        screen.blit(back_text,(back_button_rect.x+25,back_button_rect.y+10))

        pygame.display.flip()
        continue

    #continuous mouse placement
    #allows holding mouse button to place multiple objects while dragging
    mouse_buttons = pygame.mouse.get_pressed()

    if game_state == "simulation" and mouse_buttons[0]:  # left mouse button held
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
                manual_food_used = True
                clean_days = 0

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

    if game_state == "simulation" and not paused:
        day_timer += dt
        if day_timer >= effective_day_length:
            day += 1
            day_timer = 0

            clean_days += 1

            #reset daily auto-feed counter
            food_spawned_today = 0

            #spawn food for the new day according to level
            if autofeed:
                for _ in range(autofeed_level):
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

    if not paused and step_timer >= step_interval:
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

        # Adam mode win condition (25 clean days, Adam lineage alive)
        if game_mode == "adam" and adam_initialized and not game_over:
            if clean_days >= 25:
                adam_alive = any(c.adam_line and c.alive for c in creatures)
                if adam_alive:
                    game_won = True
                    game_over = True
                    game_state = "adam_game_over"

        step_timer = 0

    for creature in creatures:
        creature.draw(screen)

    #highlight selected creature (halo only)
    if selected_creature and selected_creature in creatures:
        pygame.draw.circle(
            screen,
            (0, 0, 0),
            (int(selected_creature.x), int(selected_creature.y)),
            int(selected_creature.size) + 6,
            2
        )

    #================ UI LAYER (drawn last so it appears on top) ================

    #day counter display (top left)
    day_text = font.render(f"Day {day}", True, (0, 0, 0))
    screen.blit(day_text, (20, 20))
    # Clean days display for Adam mode only
    if game_mode == "adam":
        clean_text = font.render(f"Clean: {clean_days}", True, (180,140,0))
        screen.blit(clean_text, (140, 20))

    creature_count_text = font.render(f"# of creatures: {len(creatures)}", True, (0, 0, 0))
    screen.blit(creature_count_text, (20, 45))

    #save and exit button
    pygame.draw.rect(screen, (200,200,200), save_exit_rect)
    pygame.draw.rect(screen, (0,0,0), save_exit_rect, 1)

    save_text = font.render("Save & Exit", True, (0,0,0))
    screen.blit(save_text, (save_exit_rect.x + 10, save_exit_rect.y + 5))

    #selected creature info panel
    if selected_creature and selected_creature in creatures:

        def draw_normal_panel(creature):
            panel = pygame.Rect(10, 360, 240, 210)

            pygame.draw.rect(screen, (220, 220, 220), panel)
            pygame.draw.rect(screen, (0, 0, 0), panel, 2)

            close_rect = pygame.Rect(panel.right - 25, panel.y + 5, 20, 20)
            global close_button_rect
            close_button_rect = close_rect
            pygame.draw.rect(screen, (180, 50, 50), close_rect)
            x_text = font.render("X", True, (255,255,255))
            screen.blit(x_text, (close_rect.x + 5, close_rect.y + 2))

            age_days = creature.get_age_days(day)
            bred_status = "Yes" if getattr(creature, "has_reproduced", False) else "No"

            stats = [
                f"Size: {round(creature.mature_size,1)}",
                f"Generation: {creature.generation}",
                f"Speed: {round(creature.speed,2)}",
                f"Awareness: {round(creature.awareness_radius,1)}",
                f"Maturation: {creature.maturation_time}",
                f"Age (days): {age_days}",
                f"Reproduced: {bred_status}"
            ]

            for i, line in enumerate(stats):
                stat_text = font.render(line, True, (0,0,0))
                screen.blit(stat_text, (panel.x + 10, panel.y + 12 + i * 20))

            # hunger bar
            bar_x = panel.x + 80
            bar_y = panel.y + panel.height - 25
            bar_width = 120
            bar_height = 12

            hunger_label = font.render("Hunger", True, (0,0,0))
            screen.blit(hunger_label, (panel.x + 10, bar_y - 2))

            # background
            pygame.draw.rect(screen, (180,180,180), (bar_x, bar_y, bar_width, bar_height))

            # satiated check
            if hasattr(creature, "satiated_timer") and creature.satiated_timer > 0:
                pygame.draw.rect(screen, (20,70,180), (bar_x, bar_y, bar_width, bar_height))

                small_font = pygame.font.SysFont(None, 18)
                satiated_text = small_font.render("SATIATED", True, (255,255,255))
                text_rect = satiated_text.get_rect(center=(bar_x + bar_width/2, bar_y + bar_height/2))
                screen.blit(satiated_text, text_rect)
            else:
                hunger_limit = max(getattr(creature, "hunger_limit", 100), 1)
                hunger_ratio = min(max(creature.food_need / hunger_limit, 0), 1)

                r = int(255 * hunger_ratio)
                g = int(255 * (1 - hunger_ratio))

                pygame.draw.rect(
                    screen,
                    (r, g, 0),
                    (bar_x, bar_y, int(bar_width * hunger_ratio), bar_height)
                )

        def draw_adam_panel(creature):
            panel = pygame.Rect(10, 340, 240, 210)

            pygame.draw.rect(screen, (220, 220, 220), panel)
            pygame.draw.rect(screen, (0, 0, 0), panel, 2)

            close_rect = pygame.Rect(panel.right - 25, panel.y + 5, 20, 20)
            global close_button_rect
            close_button_rect = close_rect
            pygame.draw.rect(screen, (180, 50, 50), close_rect)
            x_text = font.render("X", True, (255,255,255))
            screen.blit(x_text, (close_rect.x + 5, close_rect.y + 2))

            if getattr(creature, "is_adam", False):
                label = "ADAM"
            else:
                label = "Descendant of Adam"

            header_text = font.render(label, True, (0,0,0))
            screen.blit(header_text, (panel.x + 28, panel.y + 8))
            pygame.draw.circle(screen, (180,0,0), (panel.x + 15, panel.y + 16), 5)

            age_days = creature.get_age_days(day)
            bred_status = "Yes" if getattr(creature, "has_reproduced", False) else "No"

            stats = [
                f"Size: {round(creature.mature_size,1)}",
                f"Generation: {creature.generation}",
                f"Speed: {round(creature.speed,2)}",
                f"Awareness: {round(creature.awareness_radius,1)}",
                f"Maturation: {creature.maturation_time}",
                f"Age (days): {age_days}",
                f"Reproduced: {bred_status}"
            ]

            for i, line in enumerate(stats):
                stat_text = font.render(line, True, (0,0,0))
                screen.blit(stat_text, (panel.x + 10, panel.y + 45 + i * 20))

            # hunger bar
            bar_x = panel.x + 80
            bar_y = panel.y + panel.height - 25
            bar_width = 120
            bar_height = 12

            hunger_label = font.render("Hunger", True, (0,0,0))
            screen.blit(hunger_label, (panel.x + 10, bar_y - 2))

            # background
            pygame.draw.rect(screen, (180,180,180), (bar_x, bar_y, bar_width, bar_height))

            # satiated check
            if hasattr(creature, "satiated_timer") and creature.satiated_timer > 0:
                pygame.draw.rect(screen, (20,70,180), (bar_x, bar_y, bar_width, bar_height))

                small_font = pygame.font.SysFont(None, 18)
                satiated_text = small_font.render("SATIATED", True, (255,255,255))
                text_rect = satiated_text.get_rect(center=(bar_x + bar_width/2, bar_y + bar_height/2))
                screen.blit(satiated_text, text_rect)
            else:
                hunger_limit = max(getattr(creature, "hunger_limit", 100), 1)
                hunger_ratio = min(max(creature.food_need / hunger_limit, 0), 1)

                r = int(255 * hunger_ratio)
                g = int(255 * (1 - hunger_ratio))

                pygame.draw.rect(
                    screen,
                    (r, g, 0),
                    (bar_x, bar_y, int(bar_width * hunger_ratio), bar_height)
                )

        if getattr(selected_creature, "adam_line", False):
            draw_adam_panel(selected_creature)
        else:
            draw_normal_panel(selected_creature)

    # Pause button
    if paused:
        pygame.draw.rect(screen, (120,40,40), pause_button_rect)
        pause_text = font.render("Paused", True, (255,255,255))
    else:
        pygame.draw.rect(screen, (200,200,200), pause_button_rect)
        pause_text = font.render("Pause", True, (0,0,0))
    screen.blit(pause_text, (pause_button_rect.x + 15, pause_button_rect.y + 5))

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
    if paused and game_state == "simulation":
        overlay = pygame.Surface((820, 620))
        overlay.set_alpha(100)
        overlay.fill((0, 0, 0))
        screen.blit(overlay, (0, 0))

        big_font = pygame.font.SysFont(None, 72)
        pause_text = big_font.render("PAUSED", True, (255, 255, 255))
        screen.blit(pause_text, (310, 260))

    pygame.display.flip()

#quit pygame
pygame.quit()