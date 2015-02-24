'''
Created on Apr 27, 2013

@author: shook

This python script runs on the controlling computer.

'''

import socket

import pygame

class RobotClient(object):
    # Robot Server Info
    #HOST = '192.168.1.3'
    HOST = 'localhost'
    PORT = 1337
    SIZE = 1024
    
    # Display Window Info
    WIN_RES = (640, 480)
    
    keys_held = {pygame.K_UP: False,
                 pygame.K_DOWN: False,
                 pygame.K_RIGHT: False,
                 pygame.K_LEFT: False}
    
    def __init__(self):
        pygame.init()
        pygame.joystick.init()
        
        self.screen = pygame.display.set_mode(self.WIN_RES, pygame.DOUBLEBUF)
        pygame.display.set_caption("Robot Control")
        self.font = pygame.font.Font(None, 20)
        
        self.clock = pygame.time.Clock()
        
        self.robot_connected = False
        self.robot_state = 0
        self.robot_states = {0:'no movement', 1:'move forward',
                             2:'reverse', 3:'clockwise',
                             4:'counter-clockwise'}
        
        self.robot_arm_state = 0
        self.robot_arm_states = {0:'no movement', 1:'move up', 2:'move down'}
        
        self.robot_bucket_state = 0
        self.robot_bucket_states = {0:'no movement', 1:'move up', 2:'move down'}
        
    
    def _connect_robot(self):
        print 'Connecting to robot...'
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((self.HOST, self.PORT))
            self.robot_connected = True
            print 'Connected!'
        except Exception as e:
            print e
       
    def _disconnect_robot(self):
        self.robot_connected = False
        print 'Disconnected!'
        self.socket.close()
        
    def send_cmd(self, cmd):
        if self.robot_connected:
            try:
                self.socket.send(cmd)
            except:
                self._disconnect_robot()
        
    def _set_robot_state(self, state):
        # Only send data to server if there is a change in state
        if self.robot_state != state:
            self.robot_state = state
            self.send_cmd('M'+str(self.robot_state))
                
    def _set_robot_arm_state(self, state):
        if self.robot_arm_state != state:
            self.robot_arm_state = state
            self.send_cmd('A'+str(self.robot_arm_state))
        
    def _set_robot_bucket_state(self, state):
        if self.robot_bucket_state != state:
            self.robot_bucket_state = state
            self.send_cmd('B'+str(self.robot_bucket_state))
        
    def _render(self):
        self.screen.fill((255,255,255))
        
        state = 'Robot State:'+self.robot_states[self.robot_state]
        robot_state = self.font.render(state, True, (0,0,0))
        self.screen.blit(robot_state, [0, 0])
        
        conn_string = 'Robot Connected:'+str(self.robot_connected)
        conn_status = self.font.render(conn_string, True, (0,0,0))
        self.screen.blit(conn_status, [0, 20])
        
        pygame.display.flip()
        
    def _check_events(self):
        events = pygame.event.get()
        
        for e in events:
            if (e.type == pygame.QUIT):
                self._running = False
            elif (e.type == pygame.KEYDOWN):
                self._key_down(e.key)
            elif (e.type == pygame.KEYUP):
                self._key_up(e.key)

    def _key_down(self, key):
        self._check_keys_held(key, True)
        # Quit program if escape is hit
        if (key == pygame.K_ESCAPE):
            self._running = False
        elif (key == pygame.K_RETURN):
            if self.robot_connected:
                self._disconnect_robot()
            else:
                self._connect_robot()
        elif (key == pygame.K_UP):
            self._set_robot_state(1)
        elif (key == pygame.K_DOWN):
            self._set_robot_state(2)
        elif (key == pygame.K_RIGHT):
            self._set_robot_state(3)
        elif (key == pygame.K_LEFT):
            self._set_robot_state(4)
        elif (key == pygame.K_p):
            self._set_robot_arm_state(1)
        elif (key == pygame.K_l):
            self._set_robot_arm_state(2)
        elif (key == pygame.K_o):
            self._set_robot_bucket_state(1)
        elif (key == pygame.K_k):
            self._set_robot_bucket_state(2)

    def _key_up(self, key):
        if (key == pygame.K_UP):
            self._set_robot_state(0)
        elif (key == pygame.K_DOWN):
            self._set_robot_state(0)
        elif (key == pygame.K_RIGHT):
            self._set_robot_state(0)
        elif (key == pygame.K_LEFT):
            self._set_robot_state(0)
        elif (key == pygame.K_p):
            self._set_robot_arm_state(0)
        elif (key == pygame.K_l):
            self._set_robot_arm_state(0)
        elif (key == pygame.K_o):
            self._set_robot_bucket_state(0)
        elif (key == pygame.K_k):
            self._set_robot_bucket_state(0)
            
    def _check_keys_held(self, key, key_down):
        if key_down:
            if key in self.keys_held:
                self.keys_held[key] = True
        else: # Key Up
            if key in self.keys_held:
                self.keys_held[key] = False

    def run(self):
        self.clock = pygame.time.Clock()
        self._running = True
        
        while self._running:
            self._check_events()
            self._render()
            self.clock.tick(20)
            
                
if __name__ == '__main__':
    robot = RobotClient()
    robot.run()
    pygame.quit()