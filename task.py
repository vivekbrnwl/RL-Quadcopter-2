import numpy as np
from physics_sim import PhysicsSim

class Task():
    """Task (environment) that defines the goal and provides feedback to the agent."""
    def __init__(self, init_pose=None, init_velocities=None, 
        init_angle_velocities=None, runtime=5., target_pos=None):
        """Initialize a Task object.
        Params
        ======
            init_pose: initial position of the quadcopter in (x,y,z) dimensions and the Euler angles
            init_velocities: initial velocity of the quadcopter in (x,y,z) dimensions
            init_angle_velocities: initial radians/second for each of the three Euler angles
            runtime: time limit for each episode
            target_pos: target/goal (x,y,z) position for the agent
        """
        # Simulation
        self.sim = PhysicsSim(init_pose, init_velocities, init_angle_velocities, runtime) 
        self.action_repeat = 3

        self.state_size = self.action_repeat * 12
        #self.state_size = self.action_repeat * 6
        self.action_low = 0
        self.action_high = 900
        self.action_size = 4

        # Goal
        self.target_pos = target_pos if target_pos is not None else np.array([0., 0., 10.]) 

    def get_reward(self):
        """Uses current pose of sim to return reward."""
        time_term = 1 / (1 + 10 * self.sim.time)
        height_term = np.sqrt(self.sim.pose[2] / self.target_pos[2])
        vertical_vel_term = 0.2*self.sim.v[2]
        accel_term = self.sim.linear_accel[2]
        vertical_angle_term = np.cos(self.sim.pose[4])*(np.cos(self.sim.pose[4]) + 1) - 1
        horiz_vel_term = 0.2*np.linalg.norm(self.sim.v[0:2])
        ang_vel_term = 0.04*np.linalg.norm(self.sim.angular_v)
        ang_vel_z_term = 0.04*abs(self.sim.angular_v[1])
        
        #reward = 1 * time_term + 10 * height_term + 10 * vertical_vel_term + 0.5 * accel_term +\
        #        0.1 * vertical_angle_term - 0.2 * horiz_vel_term - \
        #        0.1 * ang_vel_term - 0.1 * ang_vel_z_term
        reward = 1 * time_term + 10 * height_term + 10 * vertical_vel_term + 2 * vertical_angle_term
        #reward = 10 * (self.sim.pose[2] / self.target_pos[2])
        return reward

    def step(self, rotor_speeds):
        """Uses action to obtain next state, reward, done."""
        reward = 0
        pose_all = []
        for _ in range(self.action_repeat):
            done = self.sim.next_timestep(rotor_speeds) or self.sim.pose[2] >= self.target_pos[2] # update the sim pose and velocities
            reward += self.get_reward() 
            pose_all.append(np.concatenate((self.sim.pose,self.sim.v,self.sim.angular_v)))
            #pose_all.append(self.sim.pose)
        next_state = np.concatenate(pose_all)
        return next_state, reward, done

    def reset(self):
        """Reset the sim to start a new episode."""
        self.sim.reset()
        state = np.concatenate((self.sim.pose, self.sim.v, self.sim.angular_v) * self.action_repeat) 
        #state = np.concatenate([self.sim.pose] * self.action_repeat) 
        return state