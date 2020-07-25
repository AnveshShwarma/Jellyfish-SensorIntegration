import smbus			#import SMBus module of I2C
import time           #import
import requests

#some MPU6050 Registers and their Address
PWR_MGMT_1   = 0x6B
SMPLRT_DIV   = 0x19
CONFIG       = 0x1A
GYRO_CONFIG  = 0x1B
INT_ENABLE   = 0x38
ACCEL_XOUT_H = 0x3B
ACCEL_YOUT_H = 0x3D
ACCEL_ZOUT_H = 0x3F
GYRO_XOUT_H  = 0x43
GYRO_YOUT_H  = 0x45
GYRO_ZOUT_H  = 0x47


def MPU_Init():
	#write to sample rate register
	bus.write_byte_data(Device_Address, SMPLRT_DIV, 7)
	
	#Write to power management register
	bus.write_byte_data(Device_Address, PWR_MGMT_1, 1)
	
	#Write to Configuration register
	bus.write_byte_data(Device_Address, CONFIG, 0)
	
	#Write to Gyro configuration register
	bus.write_byte_data(Device_Address, GYRO_CONFIG, 24)
	
	#Write to interrupt enable register
	bus.write_byte_data(Device_Address, INT_ENABLE, 1)

def read_raw_data(addr):
	#Accelero and Gyro value are 16-bit
        high = bus.read_byte_data(Device_Address, addr)
        low = bus.read_byte_data(Device_Address, addr+1)
    
        #concatenate higher and lower value
        value = ((high << 8) | low)
        
        #to get signed value from mpu6050
        if(value > 32768):
                value = value - 65536
        return value

DEVICE     = 0x23 # Default device I2C address
POWER_DOWN = 0x00 # No active state
POWER_ON   = 0x01 # Power on
RESET      = 0x07 # Reset data register value
ONE_TIME_HIGH_RES_MODE = 0x20
 
bus = smbus.SMBus(1)  # Rev 2 Pi uses 1
 
def convertToNumber(data):
  # Simple function to convert 2 bytes of data
  # into a decimal number
	return ((data[1] + (256 * data[0])) / 1.2)
 
def readLight(addr=DEVICE):
	data = bus.read_i2c_block_data(addr,ONE_TIME_HIGH_RES_MODE)
	return convertToNumber(data)

 	# or bus = smbus.SMBus(0) for older version boards
Device_Address = 0x68   # MPU6050 device address
MPU_Init()
counter=0
seconds=0
f_seconds=0
while True:
	
	#Read Accelerometer raw value
	acc_x = read_raw_data(ACCEL_XOUT_H)
	
	#Read Gyroscope raw value
	gyro_x = read_raw_data(GYRO_XOUT_H)
	
	#Full scale range +/- 250 degree/C as per sensitivity scale factor
	Ax = acc_x/16384.0
	
	Gx = gyro_x/131.0
	if readLight()<50: #can change number based on lap
		counter+=1
		if f_seconds>seconds or f_seconds==0:
			f_seconds=seconds
		seconds=0
	#gyro in degrees/sec
	#accel in g or m/second squared
	payload = {'Gyro_x': Gx ,'Accel_x': Ax,"Lap_Count":counter,'Lap Time':seconds,'Fastest Time':f_seconds}
	r = requests.post('http://things.ubidots.com/api/v1.6/devices/raspberry-pi/?token=BBFF-4ex7AYIQ7VIOaHRudf9RgXWQTIR2uW', data=payload)
	time.sleep(1)
	seconds+=1
		
