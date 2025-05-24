import random
import time
from enum import Enum, auto
from dataclasses import dataclass
from typing import List, Optional


class TimeOfDay(Enum):
    MORNING = auto()
    DAY = auto()
    EVENING = auto()
    NIGHT = auto()
    
    def next(self):
        members = list(TimeOfDay)
        index = (members.index(self) + 1) % len(members)
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
        self.plant_competition_prob = 0.3
        self.animal_interaction_prob = 0.2
        
    def add_entity(self, entity, position: Position) -> bool:
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
    
    def get_neighbors(self, position: Position, radius: int = 1) -> List[Position]:
        neighbors = []
        for dx in range(-radius, radius + 1):
            for dy in range(-radius, radius + 1):
                if dx == 0 and dy == 0:
                    continue
                nx, ny = position.x + dx, position.y + dy
                if 0 <= nx < self.width and 0 <= ny < self.height:
                    neighbors.append(Position(nx, ny))
        return neighbors
    
    def get_empty_neighbors(self, position: Position) -> List[Position]:
        return [pos for pos in self.get_neighbors(position) 
                if self.grid[pos.y][pos.x] is None]
    
    def get_entities_in_radius(self, position: Position, radius: int, entity_type=None):
        entities = []
        for pos in self.get_neighbors(position, radius):
            entity = self.grid[pos.y][pos.x]
            if entity is not None and (entity_type is None or isinstance(entity, entity_type)):
                entities.append(entity)
        return entities
    
    def update_time(self):
        self.time_ticks += 1
        if self.time_ticks % 6 == 0:
            self.time_of_day = self.time_of_day.next()
            if self.time_of_day == TimeOfDay.MORNING:
                self.day_counter += 1
            self.notify_time_change()
    
    def notify_time_change(self):
        for entity in self.entities:
            if hasattr(entity, 'on_time_change'):
                entity.on_time_change()
    
    def step(self):
        self.update_time()
        
        for entity in self.entities[:]:
            entity.update()

        self.handle_plant_competition()

        self.handle_animal_interactions()

        self.cleanup_entities()

        self.print_state()
    
    def handle_plant_competition(self):
        for entity in [e for e in self.entities if isinstance(e, Plant)]:
            neighbors = self.get_entities_in_radius(entity.position, 1, Plant)
            for neighbor in neighbors:
                if (neighbor != entity and 
                    random.random() < self.plant_competition_prob):
                    entity.compete(neighbor)
    
    def handle_animal_interactions(self):
        for entity in [e for e in self.entities if isinstance(e, Animal)]:
            if not entity.sleeping:
                neighbors = self.get_entities_in_radius(entity.position, 2, Animal)
                for neighbor in neighbors:
                    if (neighbor != entity and 
                        random.random() < self.animal_interaction_prob):
                        entity.interact(neighbor)
    
    def cleanup_entities(self):
        for entity in self.entities[:]:
            if (hasattr(entity, 'energy') and entity.energy <= 0) or \
               (hasattr(entity, 'health') and entity.health <= 0) or \
               (hasattr(entity, 'age') and entity.age > getattr(entity, 'lifespan', 100)):
                self.remove_entity(entity)
    
    def print_state(self):
        print(f"\nDay {self.day_counter}, Time: {self.time_of_day.name}")
        stats = self.collect_statistics()
        
        for y in range(self.height):
            row = []
            for x in range(self.width):
                entity = self.grid[y][x]
                row.append(self.get_entity_symbol(entity))
            print(' '.join(row))
        
        print("\nStatistics:")
        for name, data in stats.items():
            if data['count'] > 0:
                stats_str = [f"{k}: {v/data['count']:.1f}" 
                           for k, v in data.items() if k != 'count']
                print(f"{name}: {data['count']} ({', '.join(stats_str)})")
            else:
                print(f"{name}: 0")
        print("-" * 40)
    
    def get_entity_symbol(self, entity):
        if entity is None:
            return '.'
        elif isinstance(entity, Lumiere):
            return 'L'
        elif isinstance(entity, Obscurite):
            return 'O'
        elif isinstance(entity, Demi):
            return 'D'
        elif isinstance(entity, Pauvre):
            return 'P'
        elif isinstance(entity, Malheureux):
            return 'M'
        return '?'
    
    def collect_statistics(self):
        stats = {
            'Lumiere': {'count': 0, 'health': 0},
            'Obscurite': {'count': 0, 'health': 0},
            'Demi': {'count': 0, 'health': 0},
            'Pauvre': {'count': 0, 'energy': 0, 'hunger': 0, 'aggression': 0},
            'Malheureux': {'count': 0, 'energy': 0, 'hunger': 0, 'aggression': 0}
        }
        
        for entity in self.entities:
            if isinstance(entity, Lumiere):
                stats['Lumiere']['count'] += 1
                stats['Lumiere']['health'] += entity.health
            elif isinstance(entity, Obscurite):
                stats['Obscurite']['count'] += 1
                stats['Obscurite']['health'] += entity.health
            elif isinstance(entity, Demi):
                stats['Demi']['count'] += 1
                stats['Demi']['health'] += entity.health
            elif isinstance(entity, Pauvre):
                stats['Pauvre']['count'] += 1
                stats['Pauvre']['energy'] += entity.energy
                stats['Pauvre']['hunger'] += entity.hunger
                stats['Pauvre']['aggression'] += entity.aggression
            elif isinstance(entity, Malheureux):
                stats['Malheureux']['count'] += 1
                stats['Malheureux']['energy'] += entity.energy
                stats['Malheureux']['hunger'] += entity.hunger
                stats['Malheureux']['aggression'] += entity.aggression
        
        return stats


class Plant:
    def __init__(self):
        self.position = Position(0, 0)
        self.world = None
        self.growth_rate = 0.8
        self.spread_rate = 0.7
        self.active = False
        self.health = 100
        self.max_health = 100
    
    def update(self):
        self.update_activity()
        if self.active:
            self.grow()
            self.spread()
        self.check_health()
    
    def update_activity(self):
        pass
    
    def grow(self):
        self.health = min(self.max_health, self.health + 5)
    
    def spread(self):
        if random.random() < self.spread_rate:
            empty_neighbors = self.world.get_empty_neighbors(self.position)
            if empty_neighbors:
                new_pos = random.choice(empty_neighbors)
                new_plant = self.__class__()
                self.world.add_entity(new_plant, new_pos)
    
    def compete(self, other: 'Plant'):
        if not other.active:
            if random.random() < 0.7:
                self.world.remove_entity(other)
        elif self.active and other.active:
            if self.growth_rate > other.growth_rate:
                if random.random() < 0.6:
                    self.world.remove_entity(other)
            elif self.growth_rate < other.growth_rate:
                if random.random() < 0.6:
                    self.world.remove_entity(self)
            else:
                self.health -= 10
                other.health -= 10
    
    def check_health(self):
        if not self.active:
            self.health -= 2
        if self.health <= 0:
            self.world.remove_entity(self)
    
    def on_time_change(self):
        pass


class Lumiere(Plant):
    def __init__(self):
        super().__init__()
        self.growth_rate = 0.15
        self.spread_rate = 0.07
    
    def update_activity(self):
        self.active = (self.world.time_of_day == TimeOfDay.DAY)
    
    def on_time_change(self):
        self.spread_rate = 0.1 if self.world.time_of_day == TimeOfDay.DAY else 0.03


class Obscurite(Plant):
    def __init__(self):
        super().__init__()
        self.growth_rate = 0.15
        self.spread_rate = 0.07
    
    def update_activity(self):
        self.active = (self.world.time_of_day == TimeOfDay.NIGHT)
    
    def on_time_change(self):
        self.spread_rate = 0.1 if self.world.time_of_day == TimeOfDay.NIGHT else 0.03


class Demi(Plant):
    def __init__(self):
        super().__init__()
        self.growth_rate = 0.12
        self.spread_rate = 0.06
    
    def update_activity(self):
        self.active = (self.world.time_of_day in [TimeOfDay.MORNING, TimeOfDay.EVENING])
    
    def on_time_change(self):
        if self.world.time_of_day in [TimeOfDay.MORNING, TimeOfDay.EVENING]:
            self.spread_rate = 0.08
        else:
            self.spread_rate = 0.04


class Animal:
    def __init__(self):
        self.position = Position(0, 0)
        self.world = None
        self.energy = 100
        self.max_energy = 100
        self.hunger = 0
        self.max_hunger = 100
        self.aggression = 0
        self.sleeping = False
        self.age = 0
        self.lifespan = 100
        self.move_cost = 1
        self.reproduction_threshold = 70
        self.reproduction_cost = 20
    
    def update(self):
        self.age += 1
        self.update_behavior()
        
        if not self.sleeping:
            self.move()
            self.eat()
            if self.should_reproduce():
                self.reproduce()
        
        self.update_hunger()
        
        if self.should_die():
            self.world.remove_entity(self)
    
    def update_behavior(self):
        pass
    
    def move(self):
        possible_moves = self.world.get_empty_neighbors(self.position)
        if possible_moves:
            new_pos = random.choice(possible_moves)
            self.world.grid[self.position.y][self.position.x] = None
            self.position = new_pos
            self.world.grid[new_pos.y][new_pos.x] = self
            self.energy -= self.move_cost
    
    def eat(self):
        pass
    
    def interact(self, other: 'Animal'):
        pass
    
    def reproduce(self):
        pass
    
    def update_hunger(self):
        self.hunger = min(self.max_hunger, self.hunger + 1)
        if self.hunger > 50:
            self.energy -= 1
    
    def should_reproduce(self) -> bool:
        return (self.energy > self.reproduction_threshold and 
                random.random() < 0.05)
    
    def should_die(self) -> bool:
        return (self.energy <= 0 or 
                self.age > self.lifespan)
    
    def on_time_change(self):
        pass


class Pauvre(Animal):
    def __init__(self):
        super().__init__()
        self.group = []
        self.group_radius = 2
        self.min_group_size = 1
        self.max_group_size = 20
        self.eat_strategy = self.eat_normal
        self.sleep_time = TimeOfDay.NIGHT
        self.favorite_food = Lumiere
        self.reproduction_threshold = 60
        self.reproduction_cost = 15
    
    def update_behavior(self):
        self.sleeping = (self.world.time_of_day == self.sleep_time)
        self.update_group()
        self.update_aggression()
        self.update_strategy()
    
    def update_group(self):
        self.group = self.world.get_entities_in_radius(
            self.position, self.group_radius, Pauvre)
        self.group = [e for e in self.group if e != self]
        
        if len(self.group) > self.max_group_size and random.random() < 0.3:
            for member in self.group[self.max_group_size:]:
                member.move()
    
    def update_aggression(self):
        self.aggression = min(100, self.hunger + len(self.group) * 10)
    
    def update_strategy(self):
        if self.world.time_of_day == TimeOfDay.MORNING:
            self.eat_strategy = self.eat_aggressive
            self.move_cost = 1
        elif self.world.time_of_day == TimeOfDay.EVENING:
            self.eat_strategy = self.eat_conservative
            self.move_cost = 2
        else:
            self.eat_strategy = self.eat_normal
            self.move_cost = 1
    
    def eat_normal(self):
        for pos in random.sample(self.world.get_neighbors(self.position), 
                               len(self.world.get_neighbors(self.position))):
            entity = self.world.grid[pos.y][pos.x]
            if isinstance(entity, self.favorite_food):
                self.consume_entity(entity, 20, 15)
                return
    
    def eat_aggressive(self):
        for pos in random.sample(self.world.get_neighbors(self.position),
                               len(self.world.get_neighbors(self.position))):
            entity = self.world.grid[pos.y][pos.x]
            if isinstance(entity, self.favorite_food):
                self.consume_entity(entity, 30, 20)
                return
            elif isinstance(entity, Pauvre) and entity != self:
                if random.random() < self.aggression / 100:
                    entity.energy -= 20
                    self.energy -= 5
                    return
    
    def eat_conservative(self):
        if random.random() < 0.3:
            self.eat_normal()
    
    def consume_entity(self, entity, hunger_reduction: int, energy_gain: int):
        self.world.remove_entity(entity)
        self.hunger = max(0, self.hunger - hunger_reduction)
        self.energy = min(self.max_energy, self.energy + energy_gain)
    
    def interact(self, other: 'Animal'):
        if isinstance(other, Pauvre):
            if (len(self.group) < self.min_group_size and 
                len(other.group) < self.min_group_size and
                random.random() < 0.2):
                self.move_toward(other.position)
    
    def move_toward(self, position: Position):
        dx = position.x - self.position.x
        dy = position.y - self.position.y
        new_x = self.position.x + (dx // abs(dx) if dx != 0 else 0)
        new_y = self.position.y + (dy // abs(dy)) if dy != 0 else 0
        
        if (0 <= new_x < self.world.width and 
            0 <= new_y < self.world.height and
            self.world.grid[new_y][new_x] is None):
            self.world.grid[self.position.y][self.position.x] = None
            self.position = Position(new_x, new_y)
            self.world.grid[new_y][new_x] = self
            self.energy -= self.move_cost
    
    def reproduce(self):
        if len(self.group) >= self.min_group_size:
            empty_neighbors = self.world.get_empty_neighbors(self.position)
            if empty_neighbors:
                new_pos = random.choice(empty_neighbors)
                new_pauvre = Pauvre()
                new_pauvre.energy = self.reproduction_cost
                self.world.add_entity(new_pauvre, new_pos)
                self.energy -= self.reproduction_cost
    
    def on_time_change(self):
        self.update_behavior()


class Malheureux(Animal):
    def __init__(self):
        super().__init__()
        self.pack = []
        self.pack_radius = 3
        self.min_pack_size = 2
        self.sleep_times = [TimeOfDay.DAY, TimeOfDay.NIGHT]
        self.prey_types = [Demi, Obscurite, Pauvre]
        self.move_speed = 1
        self.base_move_cost = 1
        self.reproduction_threshold = 70
        self.reproduction_cost = 25
    
    def update_behavior(self):
        self.sleeping = (self.world.time_of_day in self.sleep_times)
        self.update_pack()
        self.update_move_speed()
        self.update_aggression()
    
    def update_pack(self):
        self.pack = self.world.get_entities_in_radius(
            self.position, self.pack_radius, Malheureux)
        self.pack = [e for e in self.pack if e != self]
        
        if len(self.pack) >= self.min_pack_size * 2:
            for other in [e for e in self.world.entities 
                         if isinstance(e, Malheureux) and 
                         e not in self.pack and
                         e != self]:
                if len(other.pack) < len(self.pack) and random.random() < 0.1:
                    self.attack(other)
    
    def update_move_speed(self):
        self.move_speed = 1 if self.hunger > 50 else 2
        self.move_cost = self.base_move_cost / self.move_speed
    
    def update_aggression(self):
        base_aggression = len(self.pack) * 15
        if self.world.time_of_day in [TimeOfDay.MORNING, TimeOfDay.EVENING]:
            self.aggression = min(100, base_aggression + 20)
        else:
            self.aggression = min(100, base_aggression)
    
    def attack(self, other: 'Animal'):
        other.energy -= 30
        self.energy -= 10
        if other.energy <= 0:
            self.hunger = max(0, self.hunger - 20)
            self.energy = min(self.max_energy, self.energy + 15)
    
    def move(self):
        if random.random() < 0.7 / self.move_speed:
            super().move()
    
    def eat(self):
        for pos in random.sample(self.world.get_neighbors(self.position),
                               len(self.world.get_neighbors(self.position))):
            entity = self.world.grid[pos.y][pos.x]
            for prey_type in self.prey_types:
                if isinstance(entity, prey_type):
                    nutrition = 20 if prey_type == Pauvre else 15
                    self.world.remove_entity(entity)
                    self.hunger = max(0, self.hunger - nutrition)
                    self.energy = min(self.max_energy, self.energy + nutrition)
                    return
    
    def interact(self, other: 'Animal'):
        if isinstance(other, Malheureux):
            if (len(self.pack) < self.min_pack_size and 
                len(other.pack) < self.min_pack_size and
                random.random() < 0.3):
                self.move_toward(other.position)
        elif isinstance(other, Pauvre):
            if random.random() < self.aggression / 100:
                self.attack(other)
    
    def move_toward(self, position: Position):
        dx = position.x - self.position.x
        dy = position.y - self.position.y
        new_x = self.position.x + (dx // abs(dx) if dx != 0 else 0)
        new_y = self.position.y + (dy // abs(dy)) if dy != 0 else 0
        
        if (0 <= new_x < self.world.width and 
            0 <= new_y < self.world.height):
            if self.world.grid[new_y][new_x] is None:
                self.world.grid[self.position.y][self.position.x] = None
                self.position = Position(new_x, new_y)
                self.world.grid[new_y][new_x] = self
                self.energy -= self.move_cost
    
    def reproduce(self):
        if len(self.pack) >= self.min_pack_size:
            empty_neighbors = self.world.get_empty_neighbors(self.position)
            if empty_neighbors:
                new_pos = random.choice(empty_neighbors)
                new_malheureux = Malheureux()
                new_malheureux.energy = self.reproduction_cost
                self.world.add_entity(new_malheureux, new_pos)
                self.energy -= self.reproduction_cost
    
    def on_time_change(self):
        self.update_behavior()


def initialize_world(world: World, plant_density: float, animal_density: float):
    plant_types = [Lumiere, Obscurite, Demi]
    animal_types = [Pauvre, Malheureux]
    
    for y in range(world.height):
        for x in range(world.width):
            if random.random() < plant_density:
                plant = random.choice(plant_types)()
                plant.health = random.randint(50, 100)
                world.add_entity(plant, Position(x, y))
            
            if random.random() < animal_density:
                animal = random.choice(animal_types)()
                animal.energy = random.randint(40, 80)
                animal.hunger = random.randint(0, 50)
                world.add_entity(animal, Position(x, y))


def simulate(world_size=20, steps=100, plant_density=0.3, animal_density=0.05):
    world = World(world_size, world_size)
    initialize_world(world, plant_density, animal_density)
    
    try:
        for _ in range(steps):
            world.step()
            time.sleep(0.5)
    except KeyboardInterrupt:
        print("\nSimulation stopped by user.")
    
    print("\nSimulation completed!")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description='Ecosystem Simulation')
    parser.add_argument('--size', type=int, default=15, help='World size (15-30)')
    parser.add_argument('--steps', type=int, default=50, help='Number of steps')
    parser.add_argument('--plants', type=float, default=0.2, 
                       help='Initial plant density (0.1-0.5)')
    parser.add_argument('--animals', type=float, default=0.03, 
                       help='Initial animal density (0.01-0.1)')
    args = parser.parse_args()
    
    simulate(
        world_size=max(15, min(30, args.size)),
        steps=max(10, args.steps),
        plant_density=max(0.1, min(0.5, args.plants)),
        animal_density=max(0.01, min(0.1, args.animals))
    )