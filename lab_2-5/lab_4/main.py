from agent import DQNAgent
from tank_env import TankEnv
import torch
import numpy as np

if __name__ == "__main__":
    env = TankEnv()
    state_size = len(env.get_state())
    action_size = 5
    agent = DQNAgent(state_size, action_size)

    episodes = 500
    rewards_per_episode = []

    for e in range(episodes):
        state = env.reset()
        total_reward = 0
        for time in range(200):
            env.render()  # Раскомментируйте для визуализации во время обучения
            action = agent.act(state)
            next_state, reward, done, _ = env.step(action)
            agent.remember(state, action, reward, next_state, done)
            state = next_state
            total_reward += reward
            if done:
                break
        agent.replay()
        rewards_per_episode.append(total_reward)
        print(f"Episode {e+1}/{episodes} — Reward: {total_reward} — Epsilon: {agent.epsilon:.2f}")

    # Сохраняем историю наград и модель
    np.save("rewards.npy", rewards_per_episode)
    torch.save(agent.model.state_dict(), "dqn_model.pth")
    env.close()