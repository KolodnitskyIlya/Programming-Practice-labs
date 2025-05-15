import random
import time
from enum import Enum, auto
from typing import List, Dict, Tuple, Optional, Set
from dataclasses import dataclass


class TimeOfDay(Enum):
    MORNING = auto()
    DAY = auto()
    EVENING = auto()
    NIGHT = auto()
    
    def next(self):
        members = list(TimeOfDay)
        index = members.index(self) + 1
        if index >= len(members):
            index = 0
        return members[index]


@dataclass
class Position:
    x: int
    y: int


class World:
    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height
        self.grid = [[None for _ in range(width)] for _ in range(height)]
        self.time_of_day = TimeOfDay.MORNING
        self.time_ticks = 0
        self.entities = []
        self.day_counter = 0
        
    def add_entity(self, entity, position: Position):
        if 0 <= position.x < self.width and 0 <= position.y < self.height:
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
    
    def get_neighbors(self, position: Position) -> List[Position]:
        neighbors = []
        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nx, ny = position.x + dx, position.y + dy
            if 0 <= nx < self.width and 0 <= ny < self.height:
                neighbors.append(Position(nx, ny))
        return neighbors
    
    def get_empty_neighbors(self, position: Position) -> List[Position]:
        return [pos for pos in self.get_neighbors(position) 
                if self.grid[pos.y][pos.x] is None]
    
    def update_time(self):
        self.time_ticks += 1
        if self.time_ticks % 6 == 0:
            self.time_of_day = self.time_of_day.next()
            if self.time_of_day == TimeOfDay.MORNING:
                self.day_counter += 1
    
    def step(self):
        self.update_time()
        
        # Update all entities
        for entity in self.entities[:]:
            entity.update()
        
        # Remove dead entities
        for entity in self.entities[:]:
            if hasattr(entity, 'energy') and entity.energy <= 0:
                self.remove_entity(entity)
        
        # Print world state
        self.print_state()
    
    def print_state(self):
        print(f"\nDay {self.day_counter}, Time: {self.time_of_day.name} (Tick: {self.time_ticks})")
        stats = {
            'Lumiere': 0,
            'Obscurite': 0,
            'Demi': 0,
            'Pauvre': 0,
            'Malheureux': 0
        }
        
        for y in range(self.height):
            row = []
            for x in range(self.width):
                entity = self.grid[y][x]
                if entity is None:
                    row.append('.')
                elif isinstance(entity, Lumiere):
                    row.append('L')
                    stats['Lumiere'] += 1
                elif isinstance(entity, Obscurite):
                    row.append('O')
                    stats['Obscurite'] += 1
                elif isinstance(entity, Demi):
                    row.append('D')
                    stats['Demi'] += 1
                elif isinstance(entity, Pauvre):
                    row.append('P')
                    stats['Pauvre'] += 1
                elif isinstance(entity, Malheureux):
                    row.append('M')
                    stats['Malheureux'] += 1
            print(' '.join(row))
        
        print("\nStatistics:")
        for name, count in stats.items():
            print(f"{name}: {count}")
        print("-" * 30)


class Plant:
    def __init__(self):
        self.position = Position(0, 0)
        self.world = None
        self.growth_rate = 0.1
        self.active = False
        self.health = 100
    
    def update(self):
        self.update_activity()
        if self.active:
            self.grow()
        self.check_health()
    
    def update_activity(self):
        pass
    
    def grow(self):
        if random.random() < self.growth_rate:
            empty_neighbors = self.world.get_empty_neighbors(self.position)
            if empty_neighbors:
                new_pos = random.choice(empty_neighbors)
                new_plant = self.__class__()
                self.world.add_entity(new_plant, new_pos)
    
    def compete(self, other: 'Plant'):
        if self.active and not other.active and random.random() < 0.5:
            self.world.remove_entity(other)
        elif self.active and other.active and random.random() < 0.2:
            if self.growth_rate > other.growth_rate:
                self.world.remove_entity(other)
            elif self.growth_rate < other.growth_rate:
                self.world.remove_entity(self)
    
    def check_health(self):
        if self.health <= 0:
            self.world.remove_entity(self)


class Lumiere(Plant):
    def update_activity(self):
        self.active = (self.world.time_of_day == TimeOfDay.DAY)
        if self.active:
            self.health = min(100, self.health + 5)
        else:
            self.health -= 2


class Obscurite(Plant):
    def update_activity(self):
        self.active = (self.world.time_of_day == TimeOfDay.NIGHT)
        if self.active:
            self.health = min(100, self.health + 5)
        else:
            self.health -= 2


class Demi(Plant):
    def update_activity(self):
        self.active = (self.world.time_of_day in [TimeOfDay.MORNING, TimeOfDay.EVENING])
        if self.active:
            self.health = min(100, self.health + 3)
        else:
            self.health -= 1


class Animal:
    def __init__(self):
        self.position = Position(0, 0)
        self.world = None
        self.energy = 100
        self.hunger = 0
        self.aggression = 0
        self.sleeping = False
        self.age = 0
    
    def update(self):
        self.age += 1
        self.update_behavior()
        
        if not self.sleeping:
            self.move()
            self.eat()
            if self.energy > 70 and random.random() < 0.05:
                self.reproduce()
        
        self.update_hunger()
        
        if self.energy <= 0 or self.age > 100:
            self.world.remove_entity(self)
    
    def move(self):
        possible_moves = self.world.get_empty_neighbors(self.position)
        if possible_moves:
            new_pos = random.choice(possible_moves)
            self.world.grid[self.position.y][self.position.x] = None
            self.position = new_pos
            self.world.grid[new_pos.y][new_pos.x] = self
            self.energy -= 1
    
    def eat(self):
        pass
    
    def reproduce(self):
        pass
    
    def update_hunger(self):
        self.hunger += 1
        if self.hunger > 50:
            self.energy -= 1
    
    def update_behavior(self):
        pass


class Pauvre(Animal):
    def __init__(self):
        super().__init__()
        self.group = []
        self.eat_strategy = self.eat_normal
    
    def update_behavior(self):
        # Update sleeping state
        self.sleeping = (self.world.time_of_day == TimeOfDay.NIGHT)
        
        # Update group
        self.update_group()
        
        # Update aggression based on hunger and group size
        self.aggression = min(100, self.hunger + len(self.group) * 5)
        
        # Change eat strategy based on time of day
        if self.world.time_of_day == TimeOfDay.MORNING:
            self.eat_strategy = self.eat_aggressive
        elif self.world.time_of_day == TimeOfDay.EVENING:
            self.eat_strategy = self.eat_conservative
        else:
            self.eat_strategy = self.eat_normal
    
    def update_group(self):
        neighbors = self.world.get_neighbors(self.position)
        self.group = [
            entity for pos in neighbors
            if (entity := self.world.grid[pos.y][pos.x]) is not None
            and isinstance(entity, Pauvre)
        ]
        
        # Split group if too large
        if len(self.group) > 3 and random.random() < 0.2:
            for member in self.group[3:]:
                member.move()
    
    def eat(self):
        self.eat_strategy()
    
    def eat_normal(self):
        neighbors = self.world.get_neighbors(self.position)
        for pos in neighbors:
            plant = self.world.grid[pos.y][pos.x]
            if isinstance(plant, Lumiere):
                self.world.remove_entity(plant)
                self.hunger = max(0, self.hunger - 20)
                self.energy = min(100, self.energy + 15)
                break
    
    def eat_aggressive(self):
        neighbors = self.world.get_neighbors(self.position)
        for pos in neighbors:
            entity = self.world.grid[pos.y][pos.x]
            if isinstance(entity, Lumiere):
                self.world.remove_entity(entity)
                self.hunger = max(0, self.hunger - 30)
                self.energy = min(100, self.energy + 20)
            elif isinstance(entity, Pauvre) and random.random() < self.aggression / 100:
                entity.energy -= 20
                self.energy -= 5
                break
    
    def eat_conservative(self):
        if random.random() < 0.3:
            self.eat_normal()
    
    def reproduce(self):
        if len(self.group) >= 1:
            empty_neighbors = self.world.get_empty_neighbors(self.position)
            if empty_neighbors:
                new_pos = random.choice(empty_neighbors)
                new_pauvre = Pauvre()
                new_pauvre.energy = 50
                self.world.add_entity(new_pauvre, new_pos)
                self.energy -= 20


class Malheureux(Animal):
    def __init__(self):
        super().__init__()
        self.pack = []
        self.move_speed = 1
    
    def update_behavior(self):
        # Update sleeping state
        self.sleeping = (self.world.time_of_day in [TimeOfDay.DAY, TimeOfDay.NIGHT])
        
        # Update pack
        self.update_pack()
        
        # Update move speed based on hunger
        self.move_speed = 2 if self.hunger < 30 else 1
        
        # Update aggression based on pack size
        self.aggression = min(100, len(self.pack) * 10)
    
    def update_pack(self):
        neighbors = self.world.get_neighbors(self.position)
        self.pack = [
            entity for pos in neighbors
            if (entity := self.world.grid[pos.y][pos.x]) is not None
            and isinstance(entity, Malheureux)
        ]
    
    def move(self):
        if random.random() < 0.7 / self.move_speed:
            super().move()
    
    def eat(self):
        neighbors = self.world.get_neighbors(self.position)
        for pos in neighbors:
            entity = self.world.grid[pos.y][pos.x]
            if isinstance(entity, (Demi, Obscurite)):
                self.world.remove_entity(entity)
                self.hunger = max(0, self.hunger - 15)
                self.energy = min(100, self.energy + 15)
                break
            elif isinstance(entity, Pauvre) and random.random() < self.aggression / 100:
                self.world.remove_entity(entity)
                self.hunger = max(0, self.hunger - 30)
                self.energy = min(100, self.energy + 25)
                break
    
    def reproduce(self):
        if len(self.pack) >= 2:
            empty_neighbors = self.world.get_empty_neighbors(self.position)
            if empty_neighbors:
                new_pos = random.choice(empty_neighbors)
                new_malheureux = Malheureux()
                new_malheureux.energy = 50
                self.world.add_entity(new_malheureux, new_pos)
                self.energy -= 25


def initialize_world(world: World, plant_density: float = 0.3, animal_density: float = 0.05):
    plant_types = [Lumiere, Obscurite, Demi]
    animal_types = [Pauvre, Malheureux]
    
    for y in range(world.height):
        for x in range(world.width):
            if random.random() < plant_density:
                plant_type = random.choice(plant_types)
                world.add_entity(plant_type(), Position(x, y))
    
    for y in range(world.height):
        for x in range(world.width):
            if random.random() < animal_density:
                animal_type = random.choice(animal_types)
                world.add_entity(animal_type(), Position(x, y))


def simulate(world_size=20, steps=100, plant_density=0.3, animal_density=0.05):
    world = World(world_size, world_size)
    initialize_world(world, plant_density, animal_density)
    
    for _ in range(steps):
        world.step()
        time.sleep(0.5)
    
    print("\nSimulation completed!")


if __name__ == "__main__":
    simulate(world_size=15, steps=50, plant_density=0.2, animal_density=0.03)