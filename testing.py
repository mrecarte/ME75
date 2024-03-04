import sensor
import time
import mjpeg
import machine
from lsm6dsox import LSM6DSOX
from machine import Pin, SPI, I2C
from vl53l1x import VL53L1X

# Initialize sensors
tof = VL53L1X(I2C(2))
lsm = LSM6DSOX(SPI(5), cs=Pin("PF6", Pin.OUT_PP, Pin.PULL_UP))

# Initialize camera
sensor.reset()
sensor.set_pixformat(sensor.RGB565)
sensor.set_framesize(sensor.QVGA)
sensor.skip_frames(time=2000)

led = machine.LED("LED_RED")
led.on()

# Initialize MJPEG recording
m = mjpeg.Mjpeg("example.mjpeg")

#format data as a CSV line
def format_csv_line(time, distance, accel_data, gyro_data):
    return "{},{},{},{},{},{},{},{}".format(time, distance, *accel_data, *gyro_data)

try:
    with open('sensor_data.csv', 'w') as file:
        file.write("Time,Distance,Accel_X,Accel_Y,Accel_Z,Gyro_X,Gyro_Y,Gyro_Z\n")

        for i in range(500):  # Adjust the range for desired number of frames
            # Record sensor data
            distance = tof.read()
            accel_data = lsm.accel()
            gyro_data = lsm.gyro()
            current_time = time.time()

            csv_line = format_csv_line(current_time, distance, accel_data, gyro_data)
            file.write(csv_line + '\n')

            #Capture/add frame to video
            m.add_frame(sensor.snapshot())

            #Print sensor data or FPS
            print(f"Distance: {distance}mm")
            print("Accelerometer: x:{:>8.3f} y:{:>8.3f} z:{:>8.3f}".format(*accel_data))
            print("Gyroscope:     x:{:>8.3f} y:{:>8.3f} z:{:>8.3f}".format(*gyro_data))
            print("")

            time.sleep_ms(100)

    m.close()  # Close the MJPEG file
    led.off()

except Exception as e:
    print("error occurred with the file saving:", str(e))

raise Exception("Reset the camera to see the file, the reset button is on the nicla vision.")
