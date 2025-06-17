#！/usr/bin/env python3
# -*- coding: utf-8 -*-

import rclpy
from rclpy.node import Node
import time
from sensor_msgs.msg import Joy
from unitree_go.msg import WirelessController


class PSJoyToUnitreeWirelessController(Node):
    def __init__(self):
        super().__init__('ps_joy_to_unitree_wireless_controller')
        
        self.action_hz = 0.2  # the Hz for go2 action
        self.last_publish_time = self.get_clock().now()
        
        #subscription: read playsation joy controller input button
        self.ps_joy_sub = self.create_subscription(Joy, '/joy', self.joy_callback, 5)

        #publisher: publish unitree wireless controller output msgs
        self.unitree_wireless_controller_pub = self.create_publisher(WirelessController, '/wirelesscontroller', 5)

        
        self.current_action_input = WirelessController()
        self.reset_unitree_wireless_controller_input()

        self.action_input_timer = self.create_timer(self.action_hz, self.current_button_callback)
    
    def reset_unitree_wireless_controller_input(self):
        self.current_action_input.rx = 0.0
        self.current_action_input.ry = 0.0
        self.current_action_input.lx = 0.0
        self.current_action_input.ly = 0.0
        self.current_action_input.keys = 0

    def joy_callback(self, msg):
        
        try:
            input_button = WirelessController()
            
            # Y Button [3] -> ly = 0.5
            if msg.buttons[3] == 1:
                input_button.ly = 0.5
            
            # A Button [0] -> ly = -0.5
            if msg.buttons[0] == 1:
                input_button.ly = -0.5
            
            # X Button [2] -> rx = -0.5
            if msg.buttons[2] == 1:
                input_button.rx = -0.5

            # B Button [1] -> rx = 0.5
            if msg.buttons[1] == 1:
                input_button.rx = 0.5
            
            self.current_action_input = input_button

        except IndexError:
            self.get_logger().warn("Error: IndexError", throttle_duration_sec=5)
                

    def current_button_callback(self):
        self.unitree_wireless_controller_pub.publish(self.current_action_input)

def main(args=None):
    rclpy.init(args=args)
    psj_to_uwc_node = PSJoyToUnitreeWirelessController() 
    try:
        rclpy.spin(psj_to_uwc_node)
    except KeyboardInterrupt:
        pass
    finally:
        psj_to_uwc_node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
