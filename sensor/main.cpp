#include <Arduino.h>
#include <Adafruit_MLX90640.h>

#include "HX711.h"
#include "TFMini.h"

#define WIDTH_TEMP_CAM 32
#define HEIGHT_TEMP_CAM 24

#define SDA_SCALE 25
#define SCL_SCALE 26
#define CALIBRATION_FACTOR 12025

void getTemperature();
void getWeight(void * parameter);
void getHeight(void * parameter);

Adafruit_MLX90640 mlx; //SDA 21, SCL 22
HX711 scale; // SDA 25, SCL 26
TFMini tfmini; //TX 17, RX 16

float frame[HEIGHT_TEMP_CAM * WIDTH_TEMP_CAM]; // buffer for full frame of temperatures
bool enable_run = false;

float return_temperature = -1.0;
float return_height = -1.0;
float return_weight = -1.0;

void setup() {
	Serial.begin(115200);
	while(!Serial) delay(10);

    Serial2.begin(TFMINI_BAUDRATE);
	tfmini.begin(&Serial2);
	delay(100);
	    
    if (!mlx.begin(MLX90640_I2CADDR_DEFAULT, &Wire)){
        Serial.println("MLX90640 not found!");
        while (1)
            delay(10);
    }

    Serial.println("Found Adafruit MLX90640");
    mlx.setMode(MLX90640_CHESS);
    mlx.setResolution(MLX90640_ADC_18BIT);
    mlx.setRefreshRate(MLX90640_2_HZ);
	delay(100);

    scale.begin(SDA_SCALE, SCL_SCALE);
	scale.set_scale(CALIBRATION_FACTOR);
    scale.tare(); //Reset the scale to 0
    long zero_factor = scale.read_average();

	xTaskCreate(
		getWeight,    // Function that should be called
		"Get Weight",   // Name of the task (for debugging)
		1000,            // Stack size (bytes)
		NULL,            // Parameter to pass
		1,               // Task priority
		NULL             // Task handle
	);

	xTaskCreate(
		getHeight,    // Function that should be called
		"Get Height",   // Name of the task (for debugging)
		1000,            // Stack size (bytes)
		NULL,            // Parameter to pass
		1,               // Task priority
		NULL            // Task handle
	);
}

void getWeight(void * parameter){
	float count = 0.0;
	float sum_weight = 0.0;
	for(;;){
		if(enable_run){
			float units = scale.get_units();
			if (units < 0) units = 0.00;
			float kg = units * 0.453592;
			sum_weight += kg;
			count += 1.0;

			if(count >= 10.0){
				return_weight = (int)((sum_weight / count) * 100) / 100.0;
				sum_weight = 0.0;
				count = 0.0;
			}
		}
    	vTaskDelay(100 / portTICK_PERIOD_MS);
	}
}

void getTemperature(){
	uint8_t ret = mlx.getFrame(frame);
	float sum_temp = 0.0;
	float count = 0.0;
	if (ret == 0){
		for(int k = 0; k < 10; k++){
			for(int i = k + 1; i < HEIGHT_TEMP_CAM * WIDTH_TEMP_CAM; i++){
				if(frame[i] > frame[k]){
					float temp = frame[k];
					frame[k] = frame[i];
					frame[i] = temp;
				}
			}
			if(frame[k] >= 30.0 && frame[k] <= 43.0){
				count += 1.0;
				sum_temp += frame[k];
			}
		}

		if(count != 0.0) return_temperature = (int)((sum_temp / count) * 10) / 10.0;
		else return_temperature = -1;
	}
	else{
		return_temperature = -1;
	}
}

void getHeight(void * parameter){
	int count = 0;
	int sum_distance = 0;
	for(;;){
		if(enable_run){
			int distance = tfmini.getDistance();
			if(distance != -1 && distance < 1000){
				count ++;
				sum_distance += distance;
			}
			
			if(count >= 10){
				return_height = (int)(sum_distance / count) / 100.0;
				count = 0;
				sum_distance = 0;
			}
		}
    	vTaskDelay(10 / portTICK_PERIOD_MS);
	}
}

void loop() {
	if (Serial.available() > 0){
		int request = Serial.read();
		if(request == 49 && enable_run == false){
			enable_run = true;
			delay(1000);
		}
		else if(request == 48 && enable_run == true){
			String response = "0x82";
			Serial.println(response);
			enable_run = false;
			ESP.restart();
		}
	}

	if(enable_run){
		getTemperature();
		String response = "0x83/" + String(return_weight) + '/' + String(return_height) + '/' + String(return_temperature);
		Serial.println(response);
		return_height = -1.0;
		return_weight = -1.0;
		return_temperature = -1.0;
	}
	else{
		float units = scale.get_units();
		delay(100);
	}

	delay(10);
}