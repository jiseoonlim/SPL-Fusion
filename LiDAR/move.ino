#include <DynamixelWorkbench.h>
#include <Wire.h>
#include <LIDARLite.h>

DynamixelWorkbench dxl_wb;          // Dynamixel Workbench 객체 생성
LIDARLite lidarLite; //lidar object

// Define motor IDs and communication settings
#define DXL_ID_1         1           // 첫 번째 다이나믹셀 ID
#define DXL_ID_2         2           // 두 번째 다이나믹셀 ID
#define BAUDRATE         1000000       // 통신 속도
#define DEVICENAME       ""          // OpenCR의 포트 이름

#define DXL_MIN_POSITION 0           // 최소 위치 (0도)
#define DXL_MAX_POSITION 1023        // 최대 위치 (300도)
#define DXL_MOVING_SPEED 100         // 모터 속도

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

  // 모터 위치 제어 모드 설정
  dxl_wb.torqueOff(DXL_ID_1);
  dxl_wb.torqueOff(DXL_ID_2);
  dxl_wb.setOperatingMode(DXL_ID_1, 3);
  dxl_wb.setOperatingMode(DXL_ID_2, 3);
  dxl_wb.torqueOn(DXL_ID_1);
  dxl_wb.torqueOn(DXL_ID_2);

}

void move() {

  for (int pos1 = 60; pos1 <= 150;) {
    for (int pos2 = 20; pos2 <= 180; pos2++) {
      dxl_wb.goalPosition(DXL_ID_2, pos2);
      Serial.println(pos1); 
      Serial.println(pos2);
      Serial.println(lidarLite.distance());
    }
    pos1 = pos1 + 5;
    dxl_wb.goalPosition(DXL_ID_1, pos1);
  

    for(int pos2 = 180; pos2 >= 20; pos2--) {
      dxl_wb.goalPosition(DXL_ID_2, pos2);
      Serial.println(pos1); 
      Serial.println(pos2);
      Serial.println(lidarLite.distance());
    }
    pos1 = pos1 + 5;
    dxl_wb.goalPosition(DXL_ID_1, pos1);
  }
}

void loop() {
  // 초기 위치 설정 (원점에 위치시키기)
  int initialPosition1 = 0;    // 모터 1의 초기 위치 (예: 0)
  int initialPosition2 = 0; // 모터 2의 초기 위치 (예: -180도)

  // 모터 1, 2 초기 위치로 이동
  dxl_wb.goalPosition(DXL_ID_1, initialPosition1);
  dxl_wb.goalPosition(DXL_ID_2, initialPosition2);
  delay(1000);


  move();
  Serial.write("--End of Scan--");
}
