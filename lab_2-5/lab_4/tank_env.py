import pygame
import numpy as np
import math
import random

class TankEnv:
    def __init__(self, width=400, height=400, grid_size=40):
        pygame.init()
        self.width = width
        self.height = height
        self.grid_size = grid_size
        self.cols = width // grid_size
        self.rows = height // grid_size
        self.screen = pygame.display.set_mode((width, height))
        self.clock = pygame.time.Clock()
        self.tank_size = 20
        self.goal_size = 10
        self.create_map()
        self.reset()

    def create_map(self):
        self.map = np.zeros((self.rows, self.cols), dtype=int)
        for _ in range(30):
            r, c = random.randint(0, self.rows - 1), random.randint(0, self.cols - 1)
            self.map[r, c] = 1

    def reset(self):
        self.tank_pos = np.array([50, 50], dtype=np.float32)
        self.tank_angle = 0
        while True:
            x, y = random.randint(0, self.cols - 1), random.randint(0, self.rows - 1)
            if self.map[y, x] == 0:
                self.goal_pos = np.array([x * self.grid_size + self.grid_size // 2,
                                          y * self.grid_size + self.grid_size // 2])
                break
        self.done = False
        return self.get_state()

    def raycast_distance(self, direction_vector):
        max_dist = 100.0
        step = 5
        position = self.tank_pos.copy()
        for i in range(int(max_dist / step)):
            position += direction_vector * step
            if not (0 <= position[0] < self.width and 0 <= position[1] < self.height):
                return i * step / max_dist
            grid_x, grid_y = int(position[0] // self.grid_size), int(position[1] // self.grid_size)
            if self.map[grid_y, grid_x] == 1:
                return i * step / max_dist
        return 1.0

    def get_state(self):
        dist_to_goal = np.linalg.norm(self.tank_pos - self.goal_pos)
        angle_to_goal = math.atan2(
            self.goal_pos[1] - self.tank_pos[1],
            self.goal_pos[0] - self.tank_pos[0]
        ) - math.radians(self.tank_angle)

        # Направления: вперед, назад, влево, вправо
        angle_rad = math.radians(self.tank_angle)
        forward = np.array([math.cos(angle_rad), math.sin(angle_rad)])
        backward = -forward
        left = np.array([math.cos(angle_rad - math.pi / 2), math.sin(angle_rad - math.pi / 2)])
        right = -left

        sensors = [
            self.raycast_distance(forward),
            self.raycast_distance(backward),
            self.raycast_distance(left),
            self.raycast_distance(right),
        ]

        return np.array([
            *self.tank_pos / self.width,
            self.tank_angle / 360,
            dist_to_goal / self.width,
            math.sin(angle_to_goal),
            math.cos(angle_to_goal),
            *sensors
        ], dtype=np.float32)

    def step(self, action):
        reward = -1
        old_dist = np.linalg.norm(self.tank_pos - self.goal_pos)
        new_pos = self.tank_pos.copy()

        if action == 0:
            dx = 5 * math.cos(math.radians(self.tank_angle))
            dy = 5 * math.sin(math.radians(self.tank_angle))
            new_pos += np.array([dx, dy])
        elif action == 1:
            dx = -5 * math.cos(math.radians(self.tank_angle))
            dy = -5 * math.sin(math.radians(self.tank_angle))
            new_pos += np.array([dx, dy])
        elif action == 2:
            self.tank_angle = (self.tank_angle - 10) % 360
        elif action == 3:
            self.tank_angle = (self.tank_angle + 10) % 360
        elif action == 4:
            if old_dist < 20:
                reward = 100
                self.done = True

        if 0 <= new_pos[0] < self.width and 0 <= new_pos[1] < self.height:
            grid_x, grid_y = int(new_pos[0] // self.grid_size), int(new_pos[1] // self.grid_size)
            if self.map[grid_y, grid_x] == 0:
                self.tank_pos = new_pos
            else:
                reward = -10
                self.done = True
        else:
            reward = -10
            self.done = True

        if not self.done:
            new_dist = np.linalg.norm(self.tank_pos - self.goal_pos)
            if new_dist < old_dist:
                reward += 10
            else:
                reward -= 5

        return self.get_state(), reward, self.done, {}

    def render(self):
        self.screen.fill((255, 255, 255))

        for y in range(self.rows):
            for x in range(self.cols):
                if self.map[y, x] == 1:
                    pygame.draw.rect(
                        self.screen,
                        (100, 100, 100),
                        (x * self.grid_size, y * self.grid_size, self.grid_size, self.grid_size)
                    )

        pygame.draw.circle(self.screen, (0, 255, 0), self.goal_pos.astype(int), self.goal_size)
        pygame.draw.rect(
            self.screen,
            (0, 0, 255),
            (*self.tank_pos - self.tank_size // 2, self.tank_size, self.tank_size),
        )
        pygame.display.flip()
        self.clock.tick(30)

    def close(self):
        pygame.quit()

if __name__ == "__main__":
    env = TankEnv()
    state = env.reset()

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        keys = pygame.key.get_pressed()
        action = None
        if keys[pygame.K_w]:
            action = 0  # Вперёд
        elif keys[pygame.K_s]:
            action = 1  # Назад
        elif keys[pygame.K_a]:
            action = 2  # Поворот влево
        elif keys[pygame.K_d]:
            action = 3  # Поворот вправо
        elif keys[pygame.K_SPACE]:
            action = 4  # Попытка взять цель

        if action is not None:
            state, reward, done, _ = env.step(action)
            print(f"Action: {action}, Reward: {reward:.2f}, Done: {done}")

            if done:
                print("Episode finished, resetting...")
                state = env.reset()

        env.render()

    env.close()
