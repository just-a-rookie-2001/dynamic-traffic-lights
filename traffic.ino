#include <Servo.h>

const int delay_ms = 2000;
const int signal_1_data_pin = 2;
const int signal_1_red_pin = 3;
const int signal_1_green_pin = 4;
const int signal_2_data_pin = 5;
const int signal_2_red_pin = 6;
const int signal_2_green_pin = 7;
const int signal_3_data_pin = 8;
const int signal_3_red_pin = 9;
const int signal_3_green_pin = 10;
const int camera_motor_pin = 13;


int recognize_vehicles()
{
	// send command to python to perform capture image from camera and perform Object Detection
	Serial.println("capture");
	Serial.flush();
	// wait for reply
	while (!Serial.available() > 0);
	// read and convert reply to integer
	String data = Serial.readStringUntil("\n");
	int int_data = data.toInt();
	return int_data;
}

void turn_all_red_on()
{
	//turn on all red
	digitalWrite(signal_1_red_pin, HIGH);
	digitalWrite(signal_2_red_pin, HIGH);
	digitalWrite(signal_3_red_pin, HIGH);
	
	//turn off all green
	digitalWrite(signal_1_green_pin, LOW);
	digitalWrite(signal_2_green_pin, LOW);
	digitalWrite(signal_3_green_pin, LOW);
}

void turn_green(int signal_num, int vehicles)
{
	// decide delay based on number of vehicles
	long vehicle_dependent_delay = vehicles * 1000;
	if (vehicles >= 30)
		vehicle_dependent_delay = 30000;

	if (signal_num == 1)
	{
		turn_all_red_on();
		digitalWrite(signal_1_red_pin, LOW);
		digitalWrite(signal_1_green_pin, HIGH);
		delay(vehicle_dependent_delay);
		turn_all_red_on();
	}
	else if (signal_num == 2)
	{
		turn_all_red_on();
		digitalWrite(signal_2_red_pin, LOW);
		digitalWrite(signal_2_green_pin, HIGH);
		delay(vehicle_dependent_delay);
		turn_all_red_on();
	}
	else if (signal_num == 3)
	{
		turn_all_red_on();
		digitalWrite(signal_3_red_pin, LOW);
		digitalWrite(signal_3_green_pin, HIGH);
		delay(vehicle_dependent_delay);
		turn_all_red_on();
	}
	else
		Serial.println("Specify signal number(1/2/3/4)");
}

void setup()
{
	Serial.begin(9600);

	pinMode(signal_1_red_pin, OUTPUT);
	pinMode(signal_1_green_pin, OUTPUT);
	pinMode(signal_2_red_pin, OUTPUT);
	pinMode(signal_2_green_pin, OUTPUT);
	pinMode(signal_3_red_pin, OUTPUT);
	pinMode(signal_3_green_pin, OUTPUT);

	pinMode(signal_1_data_pin, INPUT);
	pinMode(signal_2_data_pin, INPUT);
	pinMode(signal_3_data_pin, INPUT);

	myservo.attach(camera_motor_pin);
}

void loop()
{
	Servo myservo;
	turn_all_red_on();

	if (!digitalRead(signal_1_data_pin))
	{
		myservo.write(0);
		delay(15);
		turn_green(1, recognize_vehicles());
	}

	if (!digitalRead(signal_2_data_pin))
	{
		myservo.write(90);
		delay(15);
		turn_green(2, recognize_vehicles());
	}

	if (!digitalRead(signal_3_data_pin))
	{
		myservo.write(180);
		delay(15);
		turn_green(3, recognize_vehicles());
	}
}