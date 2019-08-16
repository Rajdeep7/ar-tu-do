#!/usr/bin/env python

import math
import rospy
from sensor_msgs.msg import LaserScan
from drive_msgs.msg import drive_param

import torch

from parameters import *

'''
Abstract class for methods that are used both
during training and during driving.
'''
class ReinforcementLearningNode():
    def __init__(self):
        self.scan_indices = None
        self.drive_parameters_publisher = rospy.Publisher(
            TOPIC_DRIVE_PARAMETERS, drive_param, queue_size=1)
        rospy.Subscriber(TOPIC_SCAN, LaserScan, self.on_receive_laser_scan)

    def perform_action(self, action_index):
        if action_index < 0 or action_index >= len(ACTIONS):
            raise Exception("Invalid action: " + str(action_index))

        angle, velocity = ACTIONS[action_index]
        message = drive_param()
        message.angle = angle
        message.velocity = velocity
        self.drive_parameters_publisher.publish(message)

    def convert_laser_message_to_tensor(self, message):
        if self.scan_indices is None:
            self.scan_indices = [int(i * (len(message.ranges) - 1) / (LASER_SAMPLE_COUNT - 1)) for i in range(LASER_SAMPLE_COUNT)]  # nopep8

        values = [message.ranges[i] for i in self.scan_indices]
        values = [v if not math.isinf(v) else 100 for v in values]
        return torch.tensor(values, device=device, dtype=torch.float)

    def on_receive_laser_scan(self, message):
        raise Exception("on_receive_laser_scan is not implemented.")


device = torch.device("cuda" if torch.cuda.is_available() else "cpu")