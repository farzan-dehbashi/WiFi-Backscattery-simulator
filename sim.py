import sys
import numpy as np
#import matplotlib.pyplot as plt
import math
import random
from operator import attrgetter
import matplotlib.pyplot as plt
class jitter:

    mean =0
    standard_deviation = 10

    def get_normal_jitter(self):
        normal_jitter = np.random.normal(self.mean, self.standard_deviation, 1)
        return normal_jitter

class Packet:
    id =0
    start_time = 0
    length = 0
    end_time = 0
    owner = 0
    is_corrupted = False
    sent = False

    def __init__(self, id, start_time, length, owner):
        self.id = id
        self.start_time = start_time
        self.length = length
        self.owner = owner
        self.end_time = self.start_time + self.length

class Tag:

    id = 0
    start_time = 0
    end_time = 0
    every_n = 0
    sent_packets = list()
    unsent_packet = 0
    packet_length = 0
    jitter_maker = jitter()
    accumulated_jitter = 0
    current_packet_send_time = 0

    def __init__(self, id, start_time, end_time, sends_packet_every_n, sends_packet_by_length_of):
        self.id = id
        self.start_time = start_time
        self.end_time = end_time
        self.every_n = sends_packet_every_n
        self.packet_length = sends_packet_by_length_of
        self.sent_packets = []
        self.unsent_packet = 0
        self.current_packet_send_time = self.start_time

    def make_packet(self, is_first_packet_of_this_tag):
        if is_first_packet_of_this_tag == True: #this is the first packet of this tag so we should not start the next send +every_ anfter start time
            self.current_packet_send_time = self.current_packet_send_time + math.floor(self.accumulated_jitter)
        else:
            self.current_packet_send_time = self.current_packet_send_time + math.floor(self.accumulated_jitter) + self.every_n # calculating this send time


        if (self.current_packet_send_time + self.packet_length < self.end_time or self.current_packet_send_time + self.packet_length == self.end_time) and (self.current_packet_send_time > self.start_time or self.current_packet_send_time == self.start_time):
            sending_packet = Packet(len(self.sent_packets), self.current_packet_send_time, self.packet_length, self.id)
            self.unsent_packet = sending_packet
            self.accumulated_jitter = self.accumulated_jitter + self.jitter_maker.get_normal_jitter()

    def send(self): #sending is actually done in simulator
        sending_packet = self.unsent_packet
        self.sent_packets.append(sending_packet)
        self.unsent_packet = 0
        return sending_packet


class simulator:

    time = 0 #simulator's current time
    start_time = 0
    simulation_time = 0 # the whole simulation's time
    events = [] #is the queue of events that are going to be executed
    occured_events = []
    tags = []
    n_sensors = 0
    is_random_start = True
    every_n = 0
    packet_length = 0
    timeline = []
    total_error_rate = 0
    number_of_total_errors = 0

    def __init__(self, n_sensors, simulation_time, random_start, every_n, packet_length):
        self.n_sensors = n_sensors
        self.tags = []
        self.occured_events = []
        self.simulation_time = simulation_time
        self.is_random_start = random_start
        self.every_n = every_n
        self.packet_length = packet_length
        self.total_error_rate = 0
        self.number_of_total_errors = 0
        for i in range(0, self.simulation_time):
            self.timeline.append(0)


    def initiate(self):#creating tags
        #creating tags
        i = 1
        while i < self.n_sensors or i == self.n_sensors:# creating n tags with random start time between 0 and simulator.every_n
                        #id, start_time,                      end_time,            sends_packet_every_n, sends_packet_by_length_of
            new_tag = Tag(i, random.randint(1, self.every_n - self.packet_length), self.simulation_time, self.every_n, self.packet_length)
            if isinstance(new_tag, Tag):
                self.tags.append(new_tag)
            i = i +1


        #initiating first packets of all the tags
        for i in range (0, len(self.tags)):
            tag = self.tags[i]
            is_first_packet_of_this_tag = 1; # it is the first packet of this tag
            tag.make_packet(is_first_packet_of_this_tag)
            self.events.append(self.tags[i])

        #sorting the events in the event que due to their start time
        #here, each event is a TAG! not a PACKET!
        self.events.sort(key=attrgetter('start_time'), reverse=False)

    def simulate(self):
        self.time = 0
        while self.time < self.simulation_time:
        #######################################simulation starts##################
            if len(self.events) > 0:
                self.events.sort(key=attrgetter('current_packet_send_time'), reverse=False) #sorts the tags due to their first packet to send event's start time
                self.time = self.events[0].current_packet_send_time  # update time to the first event of the first tag's start time
                running_tag = self.events.pop(0) #pops the first event/tag
                sending_packet = running_tag.send()

                self.occured_events.append(sending_packet)
                running_tag.make_packet(False)
                self.events.append(running_tag)
        ##########################################################################
            else:
                break

    def mark_corrupted_packets(self):
        # updating error rate
        for event in self.occured_events:
            if isinstance(event, Packet):
                for event2 in self.occured_events:
                    if isinstance(event2, Packet):
                        if not (event is event2):

                            if abs(event.start_time - event2.start_time) < event2.length:
                                event.is_corrupted = True
                                event2.is_corrupted = True

    def calculate_error_rate(self):
        for event in self.occured_events: #calculates number of total errors
            if isinstance(event, Packet):
                if event.is_corrupted == True:
                    self.number_of_total_errors = self.number_of_total_errors + 1
            else:
                self.occured_events.remove(event)
        error_percentage = self.number_of_total_errors / len(self.occured_events)
        self.total_error_rate = error_percentage * 100
        return (len(self.occured_events),self.total_error_rate, self.number_of_total_errors)

    def calculate_timeline_used_duration(self): #counts the number of time slots when no packet has been sent over that time
        white_space_counter = 0
        for i in range(len(self.timeline)):
            if self.timeline[i] == 0:
                white_space_counter = white_space_counter + 1
        return (white_space_counter, white_space_counter / len(self.timeline)) #number of whit slots, ratio of the white slots to the total slots

##########################################################main################################################################33

if __name__ == "__main__":
    #everything is in ms
    random_start = True # every tag start at 0 or at random seconds
    packet_length = 1 #10 #int(sys.argv[1])  # length of the each packet sent by any tag
    every_n = 30#2 * 10 * 1000 #int(sys.argv[2]) # every n seconds each tag sends data
    n_sensors = 2#int(sys.argv[3])
    simulation_time =  1000#24 * 60 * 60 * 1000  #int(sys.argv[4])
    #random.seed(4)

    #starting execution
    simulator = simulator(n_sensors, simulation_time, random_start, every_n, packet_length)
    simulator.initiate()
    simulator.simulate()
    simulator.mark_corrupted_packets()
    (total_sends, error_rate, number_of_errors) = simulator.calculate_error_rate()
    print("total error rate is "+str(error_rate)+"%")
    print("total number of sent packets is "+str(total_sends))
    print("average number of packets sent per second: "+str((total_sends/n_sensors)/(simulation_time/1000))+" packets per second")
    print(number_of_errors)
    #end execution


    #update timeline
    #for event in simulator.occured_events:
    #    if isinstance(event, Packet):
    #        #update timeline
    #        i = event.start_time
    #        while i < event.start_time + packet_length:
    #            simulator.timeline[i] = simulator.timeline[i] + 1
    #            i = i + 1
            #end of updating timeline

    #calculate the time period which is used by all the tags
    (number_of_white_spaces, occupancy_rate) = simulator.calculate_timeline_used_duration()
    print("The timeline is occupied by "+str(occupancy_rate)*10+"% as the tags have occupied "+str(number_of_white_spaces)+" slots in total")

    #pringint the resutls
    #plt.plot(simulator.timeline)
    #plt.axis()
    #plt.show()

