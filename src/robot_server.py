'''
Created on Apr 27, 2013

@author: shook

This python script runs on the lunabot.
'''

import time
import socket

import serial

class ServerControl(object):
    HOST = ''
    PORT = 1337
    BACKLOG = 2
    SIZE = 2
    
    #SERIAL_PORT = '/dev/ttyUSB1'
    #SERIAL_PORT2 = '/dev/ttyUSB0'
    SERIAL_PORT = 'COM8'
    #SERIAL_PORT2 = 'COM4'
    SERIAL_RATE = 9600
    
    MAX_MOTOR = 35
    MAX_MOTOR_BACK = 0
    # Motor 0: FL
    # Motor 1: FR
    # Motor 2: BL
    # Motor 3: BR
    channel_dict = {0:'A', 1:'B', 2:'C', 3:'D'}
    motor_delta = 2
    update_rate = 0.1
    
    def __init__(self):
        self.robot_state = 0
        self.robot_states = {0:'no movement', 1:'move forward',
                             2:'reverse', 3:'clockwise',
                             4:'counter-clockwise'}
        
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.bind((self.HOST, self.PORT))
        self.sock.listen(self.BACKLOG)
        
        self._running = True
        self.client = None
        self.ser = None
        self.ser2 = None
        
        self.motor_targets = [50, 50, 50, 50]
        self.motor_states = [50, 50, 50, 50]

        self.arm_state = 0
        self.arm_current = 50
        self.arm_target = 50
        self.bucket_state = 0
        self.bucket_current = 50
        self.bucket_target = 50
        
    def _make_serial_connection(self):
        print 'Opening motor board serial connection...'
        try:
            self.ser = serial.Serial(self.SERIAL_PORT, self.SERIAL_RATE, timeout=1)
            #self.ser2 = serial.Serial(self.SERIAL_PORT2, self.SERIAL_RATE, timeout=1)
            print 'Serial Connection created!'
        except:
            print 'Failed connecting to motorboards, check serial port address.'
            self.ser = None
            self.ser2 = None
    
    def run(self):
        self._make_serial_connection()
        
        while self._running:
            print 'Listening for connections...'
            self.client, address = self.sock.accept()
            print 'Client Connected:', address
            self._message_loop()
            
    def _message_loop(self):
        connected = True
        while connected:
            self.client.setblocking(0)
            try:
                data = self.client.recv(self.SIZE)
                if data:
                    state = int(data[1])
                    if data.count('M') > 0:
                        self._set_robot_state(state)
                    elif data.count('A') > 0:
                        self._set_arm_state(state)
                    elif data.count('B') > 0:
                        self._set_bucket_state(state)
                else:
                    print 'Controller Disconnected'
                    connected = False
                    self.client.close()
                    self._all_motors_off()
            except:
                # We read nothing, update control loop
                # self.ser = serial.Serial(self.SERIAL_PORT, self.SERIAL_RATE, timeout=1)
                self._update_motors()
                # self.ser.close()
                
                # time.sleep(0.005)
                # self.ser2 = serial.Serial(self.SERIAL_PORT2, self.SERIAL_RATE, timeout=1)
                self._update_arm()
                self._update_bucket()
                # self.ser2.close()
                
    def _update_arm(self):
        if self.arm_current < self.arm_target:
            self.arm_current += 2
        elif self.arm_current > self.arm_target:
            self.arm_current -= 2
        if self.ser2 is not None:
            self.ser2.write('A'+str(self.arm_current))
            print 'A'+str(self.arm_current)
            time.sleep(0.005)
        
    def _update_bucket(self):
        if self.bucket_current < self.bucket_target:
            self.bucket_current += 2
        elif self.bucket_current > self.bucket_target:
            self.bucket_current -= 2
        if self.ser2 is not None:
            self.ser2.write('D'+str(self.bucket_current))
            print 'D'+str(self.bucket_current)
            time.sleep(0.005)
                
    def _update_motors(self):
        for i in xrange(4):
            if self.motor_states[i] < self.motor_targets[i]:
                self.motor_states[i] += self.motor_delta
            elif self.motor_states[i] > self.motor_targets[i]:
                self.motor_states[i] -= self.motor_delta
            
            channel = self.channel_dict[i]
            if self.ser is not None:
                self.ser.write(channel+str(self.motor_states[i]))
                print channel+str(self.motor_states[i])
                time.sleep(0.01)
            else:
                print '*'+channel+str(self.motor_states[i])
                
    def _set_arm_state(self, state):
        self.arm_state = state
        if self.arm_state == 0:
            self.arm_target = 50
        elif self.arm_state == 1:
            self.arm_target = 95
        elif self.arm_state == 2:
            self.arm_target = 5
    
    def _set_bucket_state(self, state):
        self.bucket_state = state
        if self.bucket_state == 0:
            self.bucket_target = 50
        elif self.bucket_state == 1:
            self.bucket_target = 95
        elif self.bucket_state == 2:
            self.bucket_target = 5
        
    def _set_robot_state(self, state):
        if self.robot_state != state:
            self.robot_state = state
            if self.robot_state == 0:
                # All motors off
                self.motor_targets[0] = 50
                self.motor_targets[1] = 50
                self.motor_targets[2] = 50
                self.motor_targets[3] = 50
            elif self.robot_state == 1:
                self.motor_targets[0] = 50+self.MAX_MOTOR
                self.motor_targets[1] = 50+self.MAX_MOTOR
                self.motor_targets[2] = 50+self.MAX_MOTOR
                self.motor_targets[3] = 50+self.MAX_MOTOR
            elif self.robot_state == 2:
                self.motor_targets[0] = 50-self.MAX_MOTOR
                self.motor_targets[1] = 50-self.MAX_MOTOR
                self.motor_targets[2] = 50-self.MAX_MOTOR
                self.motor_targets[3] = 50-self.MAX_MOTOR
            elif self.robot_state == 3:
                self.motor_targets[0] = 50+self.MAX_MOTOR
                self.motor_targets[1] = 50-(self.MAX_MOTOR)
                self.motor_targets[2] = 50+self.MAX_MOTOR
                self.motor_targets[3] = 50-(self.MAX_MOTOR)
            elif self.robot_state == 4:
                self.motor_targets[0] = 50-(self.MAX_MOTOR)
                self.motor_targets[1] = 50+self.MAX_MOTOR
                self.motor_targets[2] = 50-(self.MAX_MOTOR)
                self.motor_targets[3] = 50+self.MAX_MOTOR
                
    def _all_motors_off(self):
        if self.ser is not None:
            self.ser.write(' ')
            self.robot_state = 0
            self.motor_targets[0] = 50
            self.motor_targets[1] = 50
            self.motor_targets[2] = 50
            self.motor_targets[3] = 50
            self.motor_states[0] = 50
            self.motor_states[1] = 50
            self.motor_states[2] = 50
            self.motor_states[3] = 50
        if self.ser2 is not None:
            self.ser2.write(' ')
            self.arm_target = 50
            self.arm_current = 50
            self.bucket_current = 50
            self.bucket_target = 50

if __name__ == '__main__':
    control = ServerControl()
    control.run()