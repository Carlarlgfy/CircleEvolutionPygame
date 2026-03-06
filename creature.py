import pygame
import random
import math
class Creature:
    def __init__(self, pos, genes=None):
        self.x, self.y = pos

        #base genetic traits
        #either inherited genes or random initialization
        if genes:
            self.mature_size = genes["mature_size"]
            self.color = genes["color"]
            self.speed = genes["speed"]
            self.awareness_radius = genes["awareness"]
            self.lifespan = genes["lifespan"]
            self.maturation_time = genes["maturation_time"]
            self.hunger_limit = genes["hunger_limit"]
            self.adam_line = genes.get("adam_line", False)
        else:
            self.mature_size = random.randint(12, 25)

            #color constraint
            #avoid overly green creatures since food is green
            r = random.randint(0, 255)
            g = random.randint(0, 180)
            b = random.randint(0, 255)
            self.color = (r, g, b)

            #speed penalty scales with size
            #larger creatures are slower, small creatures are faster
            size_speed_penalty = (self.mature_size - 12) * 0.08
            base_speed = random.uniform(2.0, 3.8)
            self.speed = max(0.6, base_speed - size_speed_penalty)

            self.awareness_radius = random.randint(80, 200)

            #longevity scales with size (~20 percent effect)
            base_life = random.randint(900, 1400)
            size_life_bonus = int(self.mature_size * 0.2 * 10)
            self.lifespan = base_life + size_life_bonus

            #maturation time weighted more heavily by size
            #bigger creatures require more time to mature
            base_time = 180 + self.mature_size * 10
            self.maturation_time = int(base_time + random.randint(-40, 40))

            #genetic hunger capacity
            #range 100–200 but fast creatures trend lower to balance energy cost
            base_hunger = random.randint(130, 200)
            speed_penalty = int(self.speed * 10)
            self.hunger_limit = max(100, base_hunger - speed_penalty)

            #lineage marker
            #used to track descendants of the first creature (Adam)
            self.adam_line = False

        #juvenile phase initialization
        #start between 1/4 and 1/2 of mature size
        self.size = random.uniform(self.mature_size * 0.25, self.mature_size * 0.5)
        self.juvenile = True

        #juvenile nutrition tracking
        self.juvenile_satiated = False
        self.juvenile_starved = False

        self.age = 0
        self.food_need = self.hunger_limit * 0.10
        self.food_eaten = 0
        self.direction = random.uniform(0, 360)
        self.alive = True
        self.mature = False
        self.reproduction_cooldown = 0

        #reproductive drive system
        #when low hunger and well fed, creature enters mating pursuit mode
        self.reproduction_drive = 0

        #refractory period after reproduction
        #prevents immediate repeated mating
        self.refractory_timer = 0

        #tracks the world day this creature was born
        #will be set by main when creature is created
        self.birth_day = 0

        #satiation system
        #when hunger reaches zero creature becomes temporarily satiated
        self.satiated_timer = 0
        self.base_awareness = self.awareness_radius

        #cooldown preventing immediate re-satiation after breeding
        self.satiated_cooldown = 0

    def update(self, foods, creatures):
        if not self.alive:
            return None

        #slower aging and metabolism
        #extends lifecycle and prevents rapid death
        self.age += 0.5
        #hunger system
        #if satiated hunger does not rise
        if self.satiated_timer > 0:
            self.satiated_timer -= 1
        else:
            self.food_need += 0.05 + (self.mature_size * 0.006)

        #satiated cooldown countdown
        if self.satiated_cooldown > 0:
            self.satiated_cooldown -= 1

        #juvenile starvation pressure tracking
        if self.juvenile and self.food_need > self.hunger_limit * 0.75:
            self.juvenile_starved = True

        if self.food_need >= self.hunger_limit or self.age >= self.lifespan:
            self.die()
            return None

        #================ BEHAVIOR STATE SYSTEM =================
        #reproduction drive increases when well fed and not in refractory period
        if self.refractory_timer == 0 and self.food_need < 25 and not self.juvenile:
            self.reproduction_drive += 1
        else:
            self.reproduction_drive = max(0, self.reproduction_drive - 2)

        #satiated state uses dedicated behavior
        if self.satiated_timer > 0:
            self.satiated(creatures)
        else:
            if self.reproduction_drive > 30 and self.mature:
                self.seek_mate(creatures)
            else:
                self.seek_food(foods)

        self.move()

        self.eat(foods)

        #juvenile growth system
        #requires both time and food consumption
        if self.juvenile:
            required_food = int(3 + self.mature_size * 0.3)
            if self.age >= self.maturation_time and self.food_eaten >= required_food:

                #apply developmental effects from juvenile nutrition
                if self.juvenile_satiated:
                    self.mature_size *= 1.08
                elif self.juvenile_starved:
                    self.mature_size *= 0.92

                self.size = self.mature_size
                self.juvenile = False
                self.mature = True
            elif self.food_eaten > 0 and self.age >= self.maturation_time * 0.5:
                growth_step = (self.mature_size - self.size) * 0.2
                self.size += growth_step

        #reproduction cooldown
        #prevents rapid self cloning loops
        if self.reproduction_cooldown > 0:
            self.reproduction_cooldown -= 1

        #refractory timer countdown
        if self.refractory_timer > 0:
            self.refractory_timer -= 1

        #restore awareness when satiation ends
        if self.satiated_timer == 0:
            self.awareness_radius = self.base_awareness

        # attempt reproduction
        if self.mature and self.food_need < 40 and self.reproduction_cooldown == 0:
            for other in creatures:
                if other is self:
                    continue
                if not other.alive or not other.mature:
                    continue

                dx = self.x - other.x
                dy = self.y - other.y
                distance = (dx*dx + dy*dy) ** 0.5

                if distance < 30:
                    child = self.reproduce(other)

                    #apply reproduction metabolic cost
                    #larger creatures pay higher energy cost
                    self.food_need += self.mature_size * 0.7

                    #end satiation immediately after reproduction
                    #creature returns to normal hunger mode
                    self.satiated_timer = 0
                    self.awareness_radius = self.base_awareness

                    #start cooldown preventing instant re-satiation
                    self.satiated_cooldown = 180

                    #enter refractory period (approx 10 seconds scaled by frame rate logic)
                    self.refractory_timer = 600

                    #reset reproduction drive after mating
                    self.reproduction_drive = 0

                    #standard cooldown scaling with size
                    self.reproduction_cooldown = int(40 + self.mature_size * 3)

                    return child

        return None

    def move(self):
        #movement update
        #creature moves smoothly every frame
        self.x += self.speed * math.cos(math.radians(self.direction))
        self.y += self.speed * math.sin(math.radians(self.direction))

        #wall collision handling
        #if creature hits boundary it rotates away instead of sticking
        hit_wall = False

        if self.x <= self.size:
            self.x = self.size
            hit_wall = True
        elif self.x >= 800 - self.size:
            self.x = 800 - self.size
            hit_wall = True

        if self.y <= self.size:
            self.y = self.size
            hit_wall = True
        elif self.y >= 600 - self.size:
            self.y = 600 - self.size
            hit_wall = True

        if hit_wall:
            #bounce style turn
            #forces strong direction change to prevent wall hugging
            self.direction += random.uniform(120, 240)

        #random wandering adjustment
        #small directional drift for natural motion
        if random.random() < 0.01:
            self.direction += random.uniform(-30, 30)

    #food seeking behavior
    def seek_food(self, foods):
        for food in foods:
            distance = math.hypot(self.x - food.x, self.y - food.y)
            if distance < self.awareness_radius:
                self.direction = math.degrees(math.atan2(food.y - self.y, food.x - self.x))
                break

    #mate seeking behavior
    def seek_mate(self, creatures):
        for other in creatures:
            if other is self:
                continue
            if not other.alive or not other.mature:
                continue

            distance = math.hypot(self.x - other.x, self.y - other.y)
            if distance < self.awareness_radius:
                self.direction = math.degrees(math.atan2(other.y - self.y, other.x - self.x))
                break

    #satiated behavior
    #creature actively hunts for the closest mate within awareness
    def satiated(self, creatures):
        if not self.mature:
            return

        closest = None
        closest_dist = float("inf")

        for other in creatures:
            if other is self:
                continue
            if not other.alive or not other.mature:
                continue

            dist = math.hypot(self.x - other.x, self.y - other.y)

            if dist < self.awareness_radius and dist < closest_dist:
                closest = other
                closest_dist = dist

        if closest:
            #lock direction toward closest mate
            self.direction = math.degrees(math.atan2(closest.y - self.y, closest.x - self.x))

        #if no mate detected creature just keeps moving

    def eat(self, foods):
        for food in foods:
            if math.hypot(self.x - food.x, self.y - food.y) < self.awareness_radius:
                if math.hypot(self.x - food.x, self.y - food.y) < self.size + food.size:
                    #store hunger before eating
                    before = self.food_need

                    #apply hunger reduction
                    self.food_need -= 20

                    #check if eating pushed hunger below zero
                    if before > 0 and self.food_need <= 0:
                        self.food_need = 0

                        #juveniles convert excess nutrition into growth advantage
                        if self.juvenile:
                            self.juvenile_satiated = True
                        else:
                            #only allow satiation if cooldown has expired
                            if self.satiated_cooldown == 0:
                                self.satiated_timer = 420
                                self.awareness_radius = int(self.base_awareness * 1.1)

                    #prevent hunger from going negative
                    if self.food_need < 0:
                        self.food_need = 0

                    self.food_eaten += 1
                    foods.remove(food)

    def die(self):
        self.alive = False

    def is_mature(self):
        if self.age > self.lifespan * 0.3:
            self.mature = True
        return self.mature

    def reproduce(self, partner):
        if not self.mature or not partner.mature:
            return None

        def clamp(value, low, high):
            return max(low, min(value, high))

        #genetic averaging including maturation traits
        new_mature_size = int((self.mature_size + partner.mature_size) / 2 + random.randint(-2, 2))
        new_speed_raw = (self.speed + partner.speed) / 2 + random.uniform(-0.15, 0.15)

        #apply inherited size-speed tradeoff again to prevent big-fast dominance
        size_speed_penalty = (new_mature_size - 12) * 0.08
        new_speed = max(0.5, new_speed_raw - size_speed_penalty)

        new_awareness = int((self.awareness_radius + partner.awareness_radius) / 2 + random.randint(-10, 10))
        new_lifespan = int((self.lifespan + partner.lifespan) / 2 + random.randint(-100, 100))

        base_maturation = (self.maturation_time + partner.maturation_time) / 2
        new_maturation_time = int(base_maturation + random.randint(-50, 50))

        #genetic hunger capacity inheritance
        parent_hunger = (self.hunger_limit + partner.hunger_limit) / 2
        new_hunger = int(parent_hunger + random.randint(-10, 10))

        #speed tradeoff: faster offspring burn energy faster
        speed_energy_penalty = int(new_speed * 8)
        new_hunger -= speed_energy_penalty

        new_hunger = clamp(new_hunger, 100, 200)

        #color averaging with variance but avoid high green bias
        new_color = []
        for c1, c2 in zip(self.color, partner.color):
            median = int((c1 + c2) / 2)
            median += random.randint(-5, 5)
            median = max(0, min(median, 255))
            new_color.append(median)

        genes = {
            "mature_size": max(8, min(new_mature_size, 35)),
            "color": tuple(new_color),
            "speed": max(0.5, min(new_speed, 4)),
            "awareness": max(40, min(new_awareness, 300)),
            "lifespan": max(600, min(new_lifespan, 2000)),
            "maturation_time": max(150, min(new_maturation_time, 800)),
            "hunger_limit": new_hunger,
            "adam_line": self.adam_line or partner.adam_line,
        }

        child = Creature((self.x, self.y), genes)
        return child

    #returns age in world days
    #current_day must be passed in from main
    def get_age_days(self, current_day):
        return current_day - self.birth_day
    def draw(self, screen):
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.size)
