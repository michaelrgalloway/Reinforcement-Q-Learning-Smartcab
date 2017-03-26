import random
from environment import Agent, Environment
from planner import RoutePlanner
from simulator import Simulator



class LearningAgent(Agent):
    """An agent that learns to drive in the smartcab world."""
   
    def __init__(self, env):
        super(LearningAgent, self).__init__(env)  # sets self.env = env, state = None, next_waypoint = None, and a default color
        self.color = 'red'  # override color
        self.planner = RoutePlanner(self.env, self)  # simple route planner to get next_waypoint
        # TODO: Initialize any additional variables here
        self.Q = {}
        self.alpha = 0.1
        self.epsilon = 0.1
        self.gamma = 0.8
        self.action = None
        self.reward = 0
        self.reachedCount = 0
    def reset(self, destination=None):
        self.planner.route_to(destination)
        # TODO: Prepare for a new trip; reset any variables here, if required
        
    # this function will get the action in the Q table that has a highest score. This function is called when 
    # the action is needed to update the car. Since the learner is trying to get to a waypoint, that waypoint will
    # be attemped first for any given state if no entries are yet in the Q table. Otherwise, the value with the highest 
    # score is used. If there does yet exist a value for an action for a state, then 0 is used. These values will
    # eventually get updated by the Q learner at the end of the update function
    def getActionToAttempt(self,actions, preferredAction):
        R = {}
        R['left'] = 0
        R['right'] = 0
        R['forward'] = 0
        R['none'] = 0
        preferred= 0
        if 'left' in actions:
            R['left'] = actions['left']
        if 'right' in actions:
            R['right'] = actions['right']
        if 'forward' in actions:
            R['forward'] = actions['forward']
        if preferredAction in actions:
            preferred = actions[preferredAction]
        if None in actions:
            R['none'] = actions[None]
            
        if preferred >= 0:
            return preferredAction
        else:
            m = max(R, key=R.get)
            if m == 'none':
                return None
            else:
                return m
            
        
       
                
    def update(self, t):
        
        # Gather inputs
        self.next_waypoint = self.planner.next_waypoint()  # from route planner, also displayed by simulator
        inputs = self.env.sense(self)
        deadline = self.env.get_deadline(self)
        #print(self.next_waypoint)
        # TODO: Update state
        #save the value of the last state so we can update the Qtable with the current values at the end of the function
        prevState = self.state
        self.state = (inputs['light'],inputs['oncoming'],inputs['right'],inputs['left'],self.next_waypoint)

        #save the value of last action so we can update Qtable with current values at end of function
        prevAction = self.action
        # TODO: Select action according to your policy
        # Here we are either assigning an action from our Q table or assigning a random action via our epsilon
        # value. .      
        if random.uniform(0, 1) < self.epsilon:
            print 'Going Random'    
            self.action = random.choice([None,'left','right','forward'])
        else:
            if not self.state in self.Q:
                self.Q[self.state] = {}    
            self.action = self.getActionToAttempt(self.Q[self.state],self.next_waypoint)
                    
        # Execute action and get reward
        reward = self.reward
        self.reward = self.env.act(self, self.action)
        
        #to evaluate performance, we are going to keep a count of how many  trials reach the destination and 
        #compare to how many trials were held
        if self.reward == 12.0:
            self.reachedCount = self.reachedCount + 1
        # TODO: Learn policy based on state, action, reward
        
        
        # Here we are update the Q table. If the state does not yet exist in the Q table then we create it.
        # Note Here: We are updating the values for last iterations state/action pair during this iteration. We 
        # are doing this because we needed access to the 'next' states max reward in order to update a given
        # state
        if not prevState in self.Q.keys():
            self.Q[prevState] = {}
        if not prevAction in self.Q[prevState].keys():
            self.Q[prevState][prevAction] = reward
        else:
            r =  self.Q[prevState][prevAction]
            maxr =  0.0
            if self.state in self.Q:
                x = self.Q[self.state]
                if len(x) > 0:
                    maxr = max(x.values())
            if maxr == None:
                maxr = 0.0   
            self.Q[prevState][prevAction] = ((1 - self.alpha) * r) + (self.alpha * (self.gamma * maxr))
        
        print "LearningAgent.update():next_waypoint={}, deadline = {}, inputs = {}, action = {}, reward = {}".format(self.next_waypoint,deadline, inputs, self.action, self.reward)  # [debug]
        print self.reachedCount
def run():
    """Run the agent for a finite number of trials."""

    # Set up environment and agent
    e = Environment()  # create environment (also adds some dummy traffic)
    a = e.create_agent(LearningAgent)  # create agent
    e.set_primary_agent(a, enforce_deadline=True)  # specify agent to track
    # NOTE: You can set enforce_deadline=False while debugging to allow longer trials

    # Now simulate it
    sim = Simulator(e, update_delay=0.001, display=False)  # create simulator (uses pygame when display=True, if available)
    # NOTE: To speed up simulation, reduce update_delay and/or set display=False

    sim.run(n_trials=100)  # run for a specified number of trials
    # NOTE: To quit midway, press Esc or close pygame window, or hit Ctrl+C on the command-line


if __name__ == '__main__':
    run()
