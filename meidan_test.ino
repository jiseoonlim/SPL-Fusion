#include <DynamixelWorkbench.h>
#include <Wire.h>
#include <LIDARLite.h>

DynamixelWorkbench dxl_wb;          // Dynamixel Workbench 객체 생성
LIDARLite lidarLite; //lidar object

bool stop_requested = false;  // check STOP signal 

// Define motor IDs and communication settings
#define DXL_ID_1         1           // 첫 번째 다이나믹셀 ID
#define DXL_ID_2         2           // 두 번째 다이나믹셀 ID
#define BAUDRATE         1000000     // 통신 속도
#define DEVICENAME       ""          // OpenCR의 포트 이름

#define DXL_MIN_POSITION 0           // 최소 위치 (0도)
#define DXL_MAX_POSITION 4096        // 최대 위치 (360도)
#define DXL_MOVING_SPEED 1000         // 모터 속도

int step = 16; //단위는 step

void setup() {
  Serial.begin(115200);              // Serial 모니터 시작

  lidarLite.begin(0, true); // Set configuration to default and I2C to 400 kHz
  lidarLite.configure(0); // Change this number to try out alternate configurations

  // Dynamixel 초기화 및 통신 설정
  if (dxl_wb.init(DEVICENAME, BAUDRATE)) {
    Serial.println("Dynamixel 초기화 성공");
  }
  else {
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

int tilt_start = 0;
int pan_start = 0;
int tilt = 0;
int pan = 0;
int32_t pan_position = 0;
int32_t tilt_position = 0;
String command = Serial.readString();


void read_serial() {
  if (Serial.available()) {

    if (command.startsWith("start pos ")) {
      tilt_start = Serial.parseInt();
      pan_start = Serial.parseInt(); 

      dxl_wb.goalPosition(DXL_ID_1, tilt_start);
      do {
        dxl_wb.getPresentPositionData(DXL_ID_1, &tilt_position);
      }
      while (abs(tilt_position - tilt_start) >= 4);

      dxl_wb.goalPosition(DXL_ID_2, pan_start);
      do {
        dxl_wb.getPresentPositionData(DXL_ID_2, &pan_position);
      }
      while (abs(pan_position - pan_start) >= 4);

      Serial.println((String) "s, " + tilt_start + ", " + pan_start + ", " + lidarLite.distance() + ", " + (String) "e");
    }

    else if(command.startsWith("pos ")){
      tilt = Serial.parseInt();
      pan = Serial.parseInt(); 

      dxl_wb.goalPosition(DXL_ID_1, tilt);
      do {
        dxl_wb.getPresentPositionData(DXL_ID_1, &tilt_position);
      }
      while (abs(tilt_position - tilt) >= 4);

      dxl_wb.goalPosition(DXL_ID_2, pan);
      do {
        dxl_wb.getPresentPositionData(DXL_ID_2, &pan_position);
      }
      while (abs(pan_position - pan) >= 4);

      Serial.println((String) "s, " + tilt + ", " + pan + ", " + lidarLite.distance() + ", " + (String) "e");
    }
  }
}


void loop() {
  int initialPosition1 = 0;    // 초기 위치
  int initialPosition2 = 0;
  dxl_wb.goalPosition(DXL_ID_1, initialPosition1);
  dxl_wb.goalPosition(DXL_ID_2, initialPosition2);  

  if (Serial.available()) {  // Serial 입력이 있을 때만 읽기
    command.trim();  // 개행 문자(\n, \r) 제거

    if (command == "reset") {
      dxl_wb.goalPosition(DXL_ID_1, initialPosition1);
      dxl_wb.goalPosition(DXL_ID_2, initialPosition2);
      Serial.println("Motors reset to initial position.");
    }
    else {
      read_serial();  // 받은 command를 read_serial()에 전달
    }
  }
}
