import random
from enum import Enum, auto
from dataclasses import dataclass

class TimeOfDay(Enum):
    MORNING = auto()
    DAY = auto()
    EVENING = auto()
    NIGHT = auto()

@dataclass
class Position:
    x: int
    y: int

class EcosystemMeta(type):
    registry = {'plants': [], 'animals': []}

    def __new__(mcs, name, bases, namespace, **kwargs):
        cls = super().__new__(mcs, name, bases, namespace)

        if any(base.__name__ == 'Plant' for base in bases):
            EcosystemMeta.registry['plants'].append(cls)
        elif any(base.__name__ == 'Animal' for base in bases):
            EcosystemMeta.registry['animals'].append(cls)

        if 'spread_rate' in namespace:
            def spread(self):
                if self.active and random.random() < self.spread_rate:
                    empty_neighbors = self.world.get_empty_neighbors(self.position)
                    if empty_neighbors:
                        new_pos = random.choice(empty_neighbors)
                        new_plant = self.__class__()
                        self.world.add_entity(new_plant, new_pos)
            cls.spread = spread

        if 'favorite_food' in namespace:
            def eat(self):
                neighbors = self.world.get_neighbors(self.position)
                for pos in neighbors:
                    entity = self.world.grid[pos.y][pos.x]
                    if isinstance(entity, self.favorite_food):
                        self.world.remove_entity(entity)
                        self.hunger = max(0, self.hunger - 20)
                        self.energy = min(self.max_energy, self.energy + 20)
                        return
            cls.eat = eat

            def reproduce(self):
                if hasattr(self, 'reproduction_threshold') and self.energy > self.reproduction_threshold:
                    empty_neighbors = self.world.get_empty_neighbors(self.position)
                    if empty_neighbors:
                        new_pos = random.choice(empty_neighbors)
                        new_animal = self.__class__()
                        new_animal.energy = getattr(self, 'reproduction_cost', 20)
                        self.world.add_entity(new_animal, new_pos)
                        self.energy -= new_animal.energy
            cls.reproduce = reproduce

        return cls

class World:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.grid = [[None for _ in range(width)] for _ in range(height)]
        self.entities = []
        self.time_hour = 12
        self.last_time_hour = self.time_hour
        self.time_of_day = self.calculate_time_of_day()
        self.day_counter = 0

    def calculate_time_of_day(self):
        h = self.time_hour
        if 6 <= h < 12:
            return TimeOfDay.MORNING
        elif 12 <= h < 18:
            return TimeOfDay.DAY
        elif 18 <= h < 22:
            return TimeOfDay.EVENING
        else:
            return TimeOfDay.NIGHT

    def add_entity(self, entity, position: Position):
        if 0 <= position.x < self.width and 0 <= position.y < self.height:
            if self.grid[position.y][position.x] is None:
                self.grid[position.y][position.x] = entity
                entity.position = position
                entity.world = self
                self.entities.append(entity)
                return True
        return False

    def remove_entity(self, entity):
        if entity in self.entities:
            self.entities.remove(entity)
        if (0 <= entity.position.x < self.width and 
            0 <= entity.position.y < self.height and
            self.grid[entity.position.y][entity.position.x] == entity):
            self.grid[entity.position.y][entity.position.x] = None

    def get_neighbors(self, position, radius=1):
        neighbors = []
        for dx in range(-radius, radius + 1):
            for dy in range(-radius, radius + 1):
                if dx == 0 and dy == 0:
                    continue
                nx, ny = position.x + dx, position.y + dy
                if 0 <= nx < self.width and 0 <= ny < self.height:
                    neighbors.append(Position(nx, ny))
        return neighbors

    def get_empty_neighbors(self, position):
        return [pos for pos in self.get_neighbors(position) if self.grid[pos.y][pos.x] is None]

    def step(self):
        self.time_of_day = self.calculate_time_of_day()
        if self.time_hour < self.last_time_hour:
            self.day_counter += 1
        self.last_time_hour = self.time_hour

        for entity in self.entities[:]:
            entity.update()

class Plant(metaclass=EcosystemMeta):
    def __init__(self):
        self.position = Position(0, 0)
        self.world = None
        self.active = False
        self.health = 100
        self.max_health = 100

    def update(self):
        self.update_activity()
        if self.active:
            self.grow()
            self.spread()
        if self.health <= 0:
            self.world.remove_entity(self)

    def update_activity(self):
        self.active = True

    def grow(self):
        self.health = min(self.max_health, self.health + 5)

class Animal(metaclass=EcosystemMeta):
    def __init__(self):
        self.position = Position(0, 0)
        self.world = None
        self.energy = 100
        self.hunger = 0
        self.max_energy = 100

    def update(self):
        self.move()
        self.eat()
        self.energy -= 1
        if self.energy <= 0:
            self.world.remove_entity(self)

    def move(self):
        possible_moves = self.world.get_empty_neighbors(self.position)
        if possible_moves:
            new_pos = random.choice(possible_moves)
            self.world.grid[self.position.y][self.position.x] = None
            self.position = new_pos
            self.world.grid[new_pos.y][new_pos.x] = self

class Lumiere(Plant):
    spread_rate = 0.1
    def update_activity(self):
        self.active = self.world.time_of_day == TimeOfDay.DAY

class Obscurite(Plant):
    spread_rate = 0.1
    def update_activity(self):
        self.active = self.world.time_of_day == TimeOfDay.NIGHT

class Pauvre(Animal):
    favorite_food = Lumiere

def initialize_world(world, plant_density, animal_density):
    plant_types = EcosystemMeta.registry['plants']
    animal_types = EcosystemMeta.registry['animals']

    for y in range(world.height):
        for x in range(world.width):
            if random.random() < plant_density:
                plant = random.choice(plant_types)()
                world.add_entity(plant, Position(x, y))
            if random.random() < animal_density:
                animal = random.choice(animal_types)()
                world.add_entity(animal, Position(x, y))
