#this will run the main game logic and import the creture and food classes
#first lets initialize everything
import pygame
import random
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
while running:
    dt = clock.tick(60)
    step_timer += dt



    mouse_pos = pygame.mouse.get_pos()
    #handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN:
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

    #selected creature info panel
    if selected_creature and selected_creature in creatures:
        pygame.draw.rect(screen, (220, 220, 220), panel_rect)
        pygame.draw.rect(screen, (0, 0, 0), panel_rect, 2)

        #close button
        pygame.draw.rect(screen, (180, 50, 50), close_button_rect)
        x_text = font.render("X", True, (255,255,255))
        screen.blit(x_text, (close_button_rect.x + 5, close_button_rect.y + 2))

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
            screen.blit(stat_text, (panel_rect.x + 10, panel_rect.y + 10 + i*18))

        #hunger bar visualization
        bar_x = panel_rect.x + 80
        bar_y = panel_rect.y + panel_rect.height - 25
        bar_width = 120
        bar_height = 12

        hunger_label = font.render("Hunger", True, (0,0,0))
        screen.blit(hunger_label, (panel_rect.x + 10, bar_y - 2))

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

    #updating screen
    pygame.display.flip()

#quit pygame
pygame.quit()