#!/usr/bin/env python
# license removed for brevity
import rospy
from std_msgs.msg import Float64
from dxl.dxlchain import DxlChain

chain = DxlChain("/dev/ttyUSB0", rate=250000)

motors = chain.get_motor_list()

chain.set_reg(1, "torque_enable", 1)
chain.set_reg(2, "torque_enable", 1)
chain.set_reg(3, "torque_enable", 1)
chain.set_reg(4, "torque_enable", 1)
chain.set_reg(5, "torque_enable", 1)

def callback_linear(data):
	command = abs(round(data.data * 25600))
	
	#if command > 5:
	#	command = command + 80
	
	if command > 1023: 
		command = 1023
	
	if data.data < 0:
		command = command + 1024
	
	chain.set_reg(1, "moving_speed", command)
	
def callback_shoulder(data):
	command = 2048 + round(data.data / 0.001533203)
	chain.goto(2, command, speed=0, blocking=False)
	
def callback_elbow(data):
	command = 2048 + round(data.data / 0.001533203)
	chain.goto(3, command, speed=0, blocking=False)
	
def callback_wrist(data):
	command = 2048 + round(data.data / 0.001533203)
	chain.goto(4, command, speed=0, blocking=False)
	
def callback_fingerjoint(data):
	command = 512 + round(data.data / 0.005117188)
	chain.goto(5, command, speed=0, blocking=False)

def talker():
	rospy.init_node('full_hw_controller')
	
	rospy.Subscriber("/full_hw_controller/linear/command", Float64, callback_linear)
	
	shoulder_pub = rospy.Publisher("/full_hw_controller/shoulder/state", Float64, queue_size=10)
	rospy.Subscriber("/full_hw_controller/shoulder/command", Float64, callback_shoulder)
	
	elbow_pub = rospy.Publisher("/full_hw_controller/elbow/state", Float64, queue_size=10)
	rospy.Subscriber("/full_hw_controller/elbow/command", Float64, callback_elbow)
	
	wrist_pub = rospy.Publisher("/full_hw_controller/wrist/state", Float64, queue_size=10)
	rospy.Subscriber("/full_hw_controller/wrist/command", Float64, callback_wrist)
	
	fingerjoint_pub = rospy.Publisher("/full_hw_controller/fingerjoint/state", Float64, queue_size=10)
	rospy.Subscriber("/full_hw_controller/fingerjoint/command", Float64, callback_fingerjoint)
	
	rate = rospy.Rate(20) # 10hz
	
	while not rospy.is_shutdown():
		rawval = (chain.get_reg(2, "present_position") - 2048) * 0.001533203
		shoulder_pub.publish(Float64(rawval))
		
		rawval = (chain.get_reg(3, "present_position") - 2048) * 0.001533203
		elbow_pub.publish(Float64(rawval))
		
		rawval = (chain.get_reg(4, "present_position") - 2048) * 0.001533203
		wrist_pub.publish(Float64(rawval))
		
		rawval = (chain.get_reg(5, "present_position") - 512) * 0.005117188
		fingerjoint_pub.publish(Float64(rawval))
		
		rate.sleep()

if __name__ == '__main__':
	try:
		talker()
	except rospy.ROSInterruptException:
		chain.disable()
		pass