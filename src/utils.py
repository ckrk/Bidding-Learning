import numpy as np
import random
from collections import deque

#np.random.seed(100)

# Ornstein-Ulhenbeck Process
# Taken from #https://github.com/vitchyr/rlkit/blob/master/rlkit/exploration_strategies/ou_strategy.py
# starting max_sigma = 0.3

class UniformNoise(object):
    def __init__(self, action_space, initial_exploration = 0.99, final_exploration = 0.05, decay_rate = 0.999):
        
        self.action_dim      = action_space.shape[0] # Requires Space with (10,) shape!
        self.low             = action_space.low
        self.high            = action_space.high
        self.distance        = abs(self.low - self.high)
        
        self.initial_exploration = initial_exploration
        self.final_exploration   = final_exploration
        self.decay_rate = decay_rate 

    #def reset(self):
    #    self.state = np.ones(self.action_dim)
    

    def get_action(self, action, step = 0):
        
        decay = self.decay_rate ** step
        exploration_probabilty = decay*self.initial_exploration + (1-decay)*self.final_exploration
        
        # Exploration Probability
        explore_yes = np.random.binomial(1,exploration_probabilty)
         
        # Unnormalized Uniform Numbers
        noise_list = np.random.uniform(self.low,self.high,size=self.action_dim)
        
        #Renormalize
        sum_noise = noise_list.sum()
        noisy_action = explore_yes * noise_list/sum_noise + (1 - explore_yes) * action
        
        return noisy_action 
    
    

class OUNoise(object):
    def __init__(self, action_space, mu=0.0, theta=0.15, max_sigma=0.3, min_sigma=0.3, decay_period=100000):
        self.mu           = mu
        self.theta        = theta
        self.sigma        = max_sigma
        self.max_sigma    = max_sigma
        self.min_sigma    = min_sigma
        self.decay_period = decay_period

        #BiddingMarket_energy_Environment Params
        self.action_dim   = action_space.shape[0]
        self.low          = action_space.low
        self.high         = action_space.high
        # only relevant for Discrete action_space
        if len(self.low) > 3:
            self.low = 0
            self.high = 1
 
        self.reset()
        
    def reset(self):
        self.state = np.ones(self.action_dim) * self.mu
        
    def evolve_state(self):
        x  = self.state
        dx = self.theta * (self.mu - x) + self.sigma * np.random.randn(self.action_dim) 
        # np.random.randn(0)
        #dx = self.theta * (self.mu - x) + self.sigma * (np.random.randn(self.action_dim) * 7)
        self.state = x + dx
        return self.state
    
    def get_action(self, action, t=0):
        ou_state = self.evolve_state()
        self.sigma = self.max_sigma - (self.max_sigma - self.min_sigma) * min(1.0, t / self.decay_period)
        return np.clip(action + ou_state, self.low, self.high)

        

class Memory:
    def __init__(self, max_size):
        self.max_size = max_size
        self.buffer = deque(maxlen=max_size)
    
    def push(self, state, action, reward, next_state, done):
        
        experience = (state, action, reward, next_state, done)
        self.buffer.append(experience)

    def sample(self, batch_size):
        state_batch = []
        action_batch = []
        reward_batch = []
        next_state_batch = []
        done_batch = []

        batch = random.sample(self.buffer, batch_size)

        for experience in batch:
            state, action, reward, next_state, done = experience
            state_batch.append(state)
            action_batch.append(action)
            reward_batch.append(reward)
            next_state_batch.append(next_state)
            done_batch.append(done)
        
        return state_batch, action_batch, reward_batch, next_state_batch, done_batch

    def __len__(self):
        return len(self.buffer)




class GaussianNoise(object):
    def __init__(self, action_space, mu = 0.0, sigma = 0.1, regulation_coef = 1, decay_rate = 0):
        
        self.action_dim      = action_space.shape[0]
        self.low             = action_space.low
        self.high            = action_space.high
        # only relevant for Discrete action_space
        if len(self.low) > 3:
            self.low = 0
            self.high = 1
            
        self.distance        = abs(self.low - self.high)
        
        self.decay_rate = decay_rate 
        self.regulation_coef = regulation_coef
        self.mu              = mu
        self.sigma           = sigma
        
        self.reset()
        
        
    def reset(self):
        self.state = np.ones(self.action_dim) * self.mu
    

    def get_action(self, action, step = 0):
         
        noise_list = np.random.normal(self.mu, self.sigma, self.action_dim) *self.regulation_coef #(self.distance *self.regulation_coef)
        noise_list = noise_list * max(np.random.normal(0,0.01,1),((1 - self.decay_rate)**step)) 
        
        noisy_action = np.clip(action + noise_list, self.low, self.high)

        return noisy_action 
    
    

      