# CSMA Algorithm
import random
import math
import collections
import sys
maxSimulationTime = 100
total_num = 0



class Node:
    def __init__(self, location, A):
        self.queue = collections.deque(self.generate_queue(A))
        self.location = location  # 位置
        self.collisions = 0
        self.wait_collisions = 0
        self.MAX_COLLISIONS = 10

    def collision_occured(self, R):
        self.collisions += 1
        if self.collisions > self.MAX_COLLISIONS:
            # 达到最大退避
            self.pop_packet()
            self.collisions = 0

        # 退避时间设置
        backoff_time = self.queue[0] + self.exponential_backoff_time(R, self.collisions)

        for i in range(len(self.queue)):
            if backoff_time >= self.queue[i]:
                self.queue[i] = backoff_time
            else:
                break

    def successful_transmission(self):
        self.collisions = 0
        self.wait_collisions = 0

    def generate_queue(self, A):
        packets = []
        arrival_time_sum = 0

        while arrival_time_sum <= maxSimulationTime:
            arrival_time_sum += get_exponential_random_variable(A)
            packets.append(arrival_time_sum)
        return sorted(packets)

    def exponential_backoff_time(self, R, general_collisions):
        rand_num = random.random() * (pow(2, general_collisions) - 1)
        return rand_num * 1024/float(R)  # 1024 bit-times
        # return random.expovariate(general_collisions*3)

    def pop_packet(self):
        self.queue.popleft()
        self.collisions = 0
        self.wait_collisions = 0



def get_exponential_random_variable(param):
    # Get random value between 0 (exclusive) and 1 (inclusive)

    # random.expovariate(0.2)
    # uniform_random_value = 1 - random.uniform(0, 1)
    # exponential_random_value = (-math.log(1 - uniform_random_value) / float(param))

    return random.expovariate(param)

def build_nodes(N, A, D):
    nodes = []
    for i in range(0, N):
        nodes.append(Node(i*D, A))
    return nodes

def csma(N, A, R, L, D, S, is_persistent):
    curr_time = 0
    transmitted_packets = 0
    successfuly_transmitted_packets = 0
    allPackets = 0
    nodes = build_nodes(N, A, D)
    for node in nodes:
        if len(node.queue) > 0:
            allPackets += len(node.queue)
    min_node = Node(None, A)  # 最低结点
    min_node.queue = [float("infinity")]
    succFlag=True


    while True:

    # Step 1: 找到最先发送数据节点
        for node in nodes:
            if len(node.queue) > 0:
                min_node = min_node if min_node.queue[0] < node.queue[0] else node  #找到最近的queue
                # print(node.queue)
        # print("mini node",min_node.queue[0],min_node.queue[1],min_node.queue[2],min_node.queue[3])
        # if len(min_node.queue) >= 4:
        #     print("mini node location and queue", min_node.location,min_node.queue[0], min_node.queue[1], min_node.queue[2], min_node.queue[3])
        # else:
        #     for i in range(len(min_node.queue)):
        #         strOut = ""
        #         for i in range(len(min_node.queue)):
        #             strOut += (str(min_node.queue[i]) + ",")
        #     print("mini node location and queue",min_node.location, strOut)

        if min_node.location is None:  # 当全部传完后，终止。
            break
        dtTime= min_node.queue[0]-curr_time
        if  dtTime<L/float(R)and succFlag==True:
            print("delta time ", dtTime)
        curr_time = min_node.queue[0]
        transmitted_packets += 1

        # Step 2: 查看是否碰撞
        # 处理其他节点碰撞
        collsion_occurred_once = False
        for node in nodes:
            t_trans = L / float(R)
            if node.location != min_node.location and len(node.queue) > 0:
                delta_location = abs(min_node.location - node.location)
                t_prop = delta_location / float(S)

                # Check collision，未侦听到，发生碰撞
                if node.queue[0] <= (curr_time + t_prop):
                    will_collide = True
                else:
                    will_collide = False

                # Sense bus busy，侦听到了，等待信道
                if (curr_time + t_prop) < node.queue[0] < (curr_time + t_prop + t_trans):
                    if is_persistent is True:
                        for i in range(len(node.queue)):
                            if (curr_time + t_prop) < node.queue[i] < (curr_time + t_prop + t_trans):
                                node.queue[i] = (curr_time + t_prop + t_trans)#持续侦听到信道闲，然后发送
                            else:
                                break

                if will_collide:
                    collsion_occurred_once = True
                    transmitted_packets += 1
                    node.collision_occured(R)
            else:#避免自己的碰撞
                for i in range(1,len(node.queue)):
                    if node.queue[i] < (curr_time + t_trans):
                        node.queue[i] = (curr_time + t_trans)  # 持续侦听到信道闲，然后发送
                    else:
                        break
        # Step 3: min节点发送或碰撞
        if collsion_occurred_once is not True:  # 无碰撞
            successfuly_transmitted_packets += 1
            succFlag=True
            min_node.pop_packet()
            # if len(min_node.queue)>=4:
            #     print(curr_time,"mini pop ok location and queue",min_node.location,min_node.queue[0],min_node.queue[1],min_node.queue[2],min_node.queue[3])
            # else:
            #     strOut=""
            #     for i in range(len(min_node.queue)):
            #         strOut+=(str(min_node.queue[i])+",")
            #     print("mini pop ok location and queue",min_node.location,strOut)
        else:    # 有碰撞
            min_node.collision_occured(R)   #立即停止
            succFlag=False

        if curr_time>=maxSimulationTime:
            break
    print("Result of    ")
    print("Persistent: ", is_persistent,"Nodes: ", N, "Avg Packet: ", A)
    print("All packets: ", allPackets)
    print("successfuly_transmitted_packets:", successfuly_transmitted_packets, "transmitted_packets :",transmitted_packets)
    print("Effeciency", successfuly_transmitted_packets/float(transmitted_packets))
    print("Throughput", (L * successfuly_transmitted_packets/R) / float(maxSimulationTime))
    print("")


# Run Algorithm
# N = The number of nodes/computers connected to the LAN
# A = Average packet arrival rate (packets per second)
# R = The speed of the LAN/channel/bus (in bps)
# L = Packet length (in bits)
# D = Distance between adjacent nodes on the bus/channel
# S = Propagation speed (meters/sec)

f = open('output1.txt', 'a')

sys.stdout = f
sys.stderr = f

D = 20000
C = 3 * pow(10, 8) # 光速
S = (2/float(3)) * C    #数字信号在总线上的传输速度为2C/3(C为光速)

# Show the efficiency and throughput of the LAN (in Mbps) 
for N in range(40, 141, 20):
    for A in [8, 15, 25]:
        R = 1 * pow(10, 6)
        L = 1500
        print("Persistent: ", "Nodes: ", N, "Avg Packet: ", A)
        csma(N, A, R, L, D, S, True)


f.close()