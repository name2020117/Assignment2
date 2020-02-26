#!/usr/bin/python
# encoding: utf-8
import os              # OS level utilities
import sys
import argparse   # for command line parsing

import random
import time
import threading
import zmq
from kazoo.client import *
#from multiprocessing import Process

class Pub_Info:

    # we define the publisher with borker_address, port and the topic it has
    
    def __init__(self, zookeeper, port, topic):

        self.address = zookeeper
        server_address = zookeeper + ':2181'
        self.zk = KazooClient(hosts=server_address)
        
        self.port = port
        self.topic = topic
        self.Connected = False
        self.Broker_IP = None
        self.socket = None
        # we randomly select the id for this publisher
        self.ID = str(random.randint(1, 10))
        self.path = None
        self.file = None
        self.list = []
        self.init()
        #self.Thread() = None
        
    
    def init(self):
        if self.zk.state != KazooState.CONNECTED:
            self.zk.start()
    
        while self.zk.state != KazooState.CONNECTED:
            pass
        print('Pub %s connected to local ZooKeeper Server.' % self.ID)

        znode_path = '/Publishers/' + self.ID
        self.zk.create(path=znode_path, value=str(self.ID).encode('utf-8'), ephemeral=True, makepath=True)
                
        while self.zk.exists(znode_path) is None:
            pass
        
        # we find the file from path
        
        leader_path = '/Leader'
        data, state = self.zk.get(leader_path)
        self.file = './Output/' + self.ID + '-publisher.log'
        print(self.file)

        self.path = './Input/'+ self.topic + '.txt'
        self.list = get_publications(self.path)
        self.Broker_IP = data.decode("utf-8")
        
        if self.register_pub():
            print('Pub %s connected with leader' % self.ID)
            self.Connected = True

    

        
    

        print('PUB ID:', self.ID)

        

        @self.zk.DataWatch(path=leader_path)
        def watch_leader(data, state):
            print('Broker in Leader Znode is: %s' % data)
            if state is None:
                self.Connected = False
                print('Pub %s loses connection with old leader' % self.ID)
            elif self.Connected is False:
                self.Broker_IP = data.decode("utf-8")
                # self.socket = None
                # print('pub %s try to reconnect with leader' % pub.ID)
                if self.register_pub():
                    print('pub %s connected with new leader' % self.ID)
                    #self.socket = None
                    self.Connected = True
                    time.sleep(5)
                    threading.Thread(target=self.publish1(), args=()).start()
        
        
    
    
    def register_pub(self):

        print('Publisher NO. %s with %s.' % (self.ID, self.topic))

        # publisher to broker socket establish
        connection = "tcp://" + self.Broker_IP + ":5555"
        context = zmq.Context()
        self.socket = context.socket(zmq.REQ)
        current = time.time()
        
        while (time.time() - current < 5):
            self.socket.connect(connection)

        if self.socket is None:
            print('Connection failed.')
            return False
        else:
            print('Connection succeed!')
            message = 'init' + '#' + self.ID + '#' + self.topic + '#'
            # send the message
            self.socket.send_string( message )

            

            recv_msg = self.socket.recv_string()

            print(recv_msg)
            
            return True
                
    def publish1(self):
        try:
            with open(self.file, 'a') as logfile:
                for p in self.list:
                    logfile.write('*************************************************\n')
                    
                    logfile.write('Publish Info: %s \n'% self.topic)
                    logfile.write('Publish: %s\n' % p)
                    logfile.write('Time: %s\n' % str(time.time()))
                    sending = 'publish' + '#' + self.ID + '#' + self.topic + '#' + p

                    self.socket.send_string(sending)
                    #print(sending)

                    rcv_msg = self.socket.recv_string()
                    print(rcv_msg)
                    time.sleep(1)
                self.socket.close()
        except IOError:
            print('Open or write file error.')
    
    


def parseCmdLineArgs ():
    # parse the command line
    parser = argparse.ArgumentParser ()

    # add optional arguments
    parser.add_argument('-i', '--ip', type=str, help='current publisher ip address')
    parser.add_argument('-z', '--zk', type=str, help='ZooKeeper address')
    # parse the args
    args = parser.parse_args ()

    return args




	# registation finished
    #the_socket.close()
    
def publish(pub):
        try:
            with open(pub.file, 'a') as logfile:
                for p in pub.list:
                    logfile.write('*************************************************\n')
                    
                    logfile.write('Publish Info: %s \n'% pub.topic)
                    logfile.write('Publish: %s\n' % p)
                    logfile.write('Time: %s\n' % str(time.time()))
                    sending = 'publish' + '#' + pub.ID + '#' + pub.topic + '#' + p
                    pub.socket.send_string(sending)
                    rcv_msg = pub.socket.recv_string()
                    print(rcv_msg)
                    time.sleep(1)
                pub.socket.close()
        except IOError:
            print('Open or write file error.')


def get_publications(file_path):
	try:
		with open(file_path, 'r') as file:
			pubs = file.readlines()
		for i in range(len(pubs)):
			pubs[i] = pubs[i][:-1]
		return pubs
	except IOError:
		print('Open or write file error.')
		return []

def main():
    
    args = parseCmdLineArgs()
    
    zoo_address = args.zk

    # we define all the topics we have in this section
    topics = {1:'animals', 2:'countries', 3:'foods', 4:'countries', 5:'phones', 6:'universities'}
    
    # select the topic randomly
    #topic = topics[random.randint(1, 6)]
    topic = topics[1]

    # we first init the publish server and connect with the zookeeper
    pub = Pub_Info(zoo_address,'5555',topic)

    
    
    ''' # we register the publisher to the broker with port_number, topic, the broker address and its id
    socket = pub.socket
    '''
    # wait for the registation complete
    time.sleep(5)
    
    # we find the path for the topic
    '''pub.path = './Input/'+ topic + '.txt'
    

    pub.list = get_publications(pub.path)
    

    print('PUB ID:', pub.ID)

    # we find the file from path
    pub.file = './Output/' + pub.ID + '-publisher.log'
    '''
    '''context = zmq.Context()
    
    pubsocket = context.socket(zmq.REQ)
    
    current = time.time()
    
    pubsocket.connect("tcp://" + baddress + ":5555")'''
    pub.file = './Output/' + pub.ID + '-publisher.log'
    threading.Thread(target=publish(pub), args=()).start()
    #wait()




if __name__ == '__main__':

    main()
    
    
    