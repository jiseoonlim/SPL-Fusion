#include <DynamixelWorkbench.h>
#include <Wire.h>
#include <LIDARLite.h>

DynamixelWorkbench dxl_wb;          // Dynamixel Workbench 객체 생성
LIDARLite lidarLite; //lidar object

bool stop_requested = false;  // check STOP signal 

// Define motor IDs and communication settings
#define DXL_ID_1         1           // 첫 번째 다이나믹셀 ID
#define DXL_ID_2         2           // 두 번째 다이나믹셀 ID
#define BAUDRATE         1000000       // 통신 속도
#define DEVICENAME       ""          // OpenCR의 포트 이름

#define DXL_MIN_POSITION 0           // 최소 위치 (0도)
#define DXL_MAX_POSITION 4096        // 최대 위치 (300도)
#define DXL_MOVING_SPEED 1000         // 모터 속도

void setup() {
  Serial.begin(115200);              // Serial 모니터 시작

  lidarLite.begin(0, true); // Set configuration to default and I2C to 400 kHz
  lidarLite.configure(0); // Change this number to try out alternate configurations

  // Dynamixel 초기화 및 통신 설정
  if (dxl_wb.init(DEVICENAME, BAUDRATE)) {
    Serial.println("Dynamixel 초기화 성공");
  } else {
    Serial.println("Dynamixel 초기화 실패");
    while (1);                      // 초기화 실패 시 멈춤
  }

  // 각 모터 연결 확인
  if (dxl_wb.ping(DXL_ID_1)) {
    Serial.print("ID ");
    Serial.print(DXL_ID_1);
    Serial.println(": 모터 연결됨");
  } else {
    Serial.print("ID ");
    Serial.print(DXL_ID_1);
    Serial.println(": 모터 연결 실패");
  }

  if (dxl_wb.ping(DXL_ID_2)) {
    Serial.print("ID ");
    Serial.print(DXL_ID_2);
    Serial.println(": 모터 연결됨");
  } else {
    Serial.print("ID ");
    Serial.print(DXL_ID_2);
    Serial.println(": 모터 연결 실패");
  }
  dxl_wb.torqueOff(DXL_ID_1);
  dxl_wb.torqueOff(DXL_ID_2);
  dxl_wb.setOperatingMode(DXL_ID_1, 3);
  dxl_wb.setOperatingMode(DXL_ID_2, 3);
  dxl_wb.torqueOn(DXL_ID_1);
  dxl_wb.torqueOn(DXL_ID_2);

  uint32_t profile_velocity = 32767;  
  dxl_wb.writeRegister(DXL_ID_1, "Profile_Velocity", profile_velocity);
  dxl_wb.writeRegister(DXL_ID_2, "Profile_Velocity", profile_velocity);

  uint32_t profile_acceleration = 32737;  
  dxl_wb.writeRegister(DXL_ID_1, "Profile_Acceleration", profile_acceleration);
  dxl_wb.writeRegister(DXL_ID_2, "Profile_Acceleration", profile_acceleration);
  }

void move() {
  int initialPosition1 = 512;    
  int initialPosition2 = 0; 
  dxl_wb.goalPosition(DXL_ID_1, initialPosition1);
  dxl_wb.goalPosition(DXL_ID_2, initialPosition2);
  delay(1000);

  for (int pos1 = 512; pos1 <= 1536;) {
    for (int pos2 = 0; pos2 <= 2048; pos2 += 16) {
      dxl_wb.goalPosition(DXL_ID_2, pos2);
      Serial.println((String) "s, " + pos1 + ", " + pos2 + ", " + lidarLite.distance() + ", " + (String) "e");
    }
    pos1 = pos1 + 16;
    dxl_wb.goalPosition(DXL_ID_1, pos1);
    delay(100);
  

    for(int pos2 = 2048; pos2 >= 0; pos2 -= 16) {
      dxl_wb.goalPosition(DXL_ID_2, pos2);
      Serial.println((String) "s, " + pos1 + ", " + pos2 + ", " + lidarLite.distance() + ", " + (String) "e");
    }
    pos1 = pos1 + 16;
    dxl_wb.goalPosition(DXL_ID_1, pos1);
    delay(100);

  }
}

void loop() {
  int initialPosition1 = 512;    
  int initialPosition2 = 512; 
  dxl_wb.goalPosition(DXL_ID_1, initialPosition1);
  dxl_wb.goalPosition(DXL_ID_2, initialPosition2);
  if (Serial.available() > 0){
     String signal = Serial.readStringUntil('\n');  // 신호를 문자열로 읽기

    if (signal == "START") {
      stop_requested = false;  // START 신호 시 동작 재개
      move();
      Serial.println("--End of Scan--");
    } 
  }
}
