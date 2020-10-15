#include "TaskUtils.h"
#include "BNO055_support.h"
#include <EEPROM.h>
#include <ESP8266WiFi.h>
#include <Wire.h>

struct MovementData {
  short acc_x, acc_y, acc_z, quat_x, quat_y, quat_z, quat_w;
  unsigned long time1, time2;
};

const PROGMEM char endingMessage[] = "WAITING FOR COMMAND";

const char *host = "192.168.0.115";
const uint16_t appLoginPort = 51423;
const int notYetImplementedResult = 1111;
const int bufferSize = 30;
const int nSamples = 1000;
char ssid[bufferSize] = "probanet";
char pswd[bufferSize] = "figyelemezproba";
char deviceName[bufferSize] = "MeasurementUnit #1";
TaskRepository taskRepo;

struct bno055_t bno;
struct bno055_linear_accel linaccData;
struct bno055_quaternion quaternionData;
struct MovementData data[nSamples];
byte accCalibration = 0, magCalibration = 0, gyroCalibration = 0, sysCalibration = 0;

WiFiServer server(52555);
WiFiClient client;

void wr(const char *msg, bool shouldAddLineEnding = false){
  Serial.print(msg);
  client.print(msg);
  if(shouldAddLineEnding){
    Serial.println();
    client.println();
  }
}

void wrln(const char *msg){
  wr(msg, true);
}

void wr(int msg, bool shouldAddLineEnding = false){
  // int max value is 32767, five characters plus optionally a minus sign = 6 chars
  char numberBuffer[6];
  sprintf(numberBuffer, "%d", msg);
  wr(numberBuffer, shouldAddLineEnding);
}

void wrln(int msg){
  wr(msg, true);
}

void setup() {
  Serial.begin(115200);
  delay(3000);
  wr("Hello!\nThis is "); wrln(deviceName);
  wr("Setting up tasks...");
  taskRepo.addTask(".", setupChangeHandler);
  taskRepo.addTask("connect", connectAllHandler);
  taskRepo.addTask("connwifi", connectToWiFiHandler);
  taskRepo.addTask("connapp", connectToApplicationHandler);
  taskRepo.addTask("startm", startMeasurementHandler);
  taskRepo.addTask("s", startMeasurementHandler);
  taskRepo.addTask("printres", printResultsHandler);
  taskRepo.addTask("p", printResultsHandler);
  taskRepo.addTask("printcal", printCalibrationHandler);
  taskRepo.addTask("c", printCalibrationHandler);
  taskRepo.addTask("printinfo", printSensorInfoHandler);
  taskRepo.addTask("i", printSensorInfoHandler);
  taskRepo.addTask("reinit", initializeSensorHandler);
  taskRepo.addTask("r", initializeSensorHandler);
  taskRepo.addTask("quateronly", quaternionOnlyHandler);
  wrln("DONE.");

  Wire.begin(4, 5);

  int connSuccess = taskRepo.getTask("connect")->execute("");
  wr("Connection during setup: "); wrln(connSuccess);
  taskRepo.getTask("r")->execute("");

  wr("Starting server...");
  server.begin();
  wr("DONE.");

  wrln("\nSETUP DONE.");
  printEndOfCurrentIteration();
}

void loop() {
  // Variables needed for handling input
  char inputBuffer[bufferSize] = "";
  int charCounter = 0;
  client = server.available();

  // Wait for a command
  if(Serial.available() <= 0 && !client){
    delay(1);
    return;
  }

  Serial.println("MSG_RCV.");
  
  char incomingChar;

  // The Serial has priority
  if(Serial.available()){
  incomingChar  = Serial.read();
    while(incomingChar != '\n'){
      while(!Serial.available()) {}
      if(charCounter >= bufferSize){
        wrln("BUFFER OVERFLOW!");
        Serial.read();
      }
      inputBuffer[charCounter++] = incomingChar;
      incomingChar = Serial.read();
    }
  }
  else{ // The message is coming in over WiFi
    
    if(!client){ // I think this should not be true at any time
      return;
    }
    // TODO: Read char by char instead of the resource-hungry String
    Serial.print("This came over the wifi: ");
    String helper = client.readStringUntil('\n');
    helper.trim();
    strcpy(inputBuffer, helper.c_str());
    Serial.println(inputBuffer);
  }

  Task *taskToExecute;
  if(inputBuffer[0] == '.'){
    taskToExecute = taskRepo.getTask(".");
  }
  else{
    taskToExecute = taskRepo.getTask(inputBuffer);
  }
  
  if(taskToExecute == NULL){
    wrln("Unknown command.");
  }
  else{
    int returnCode = taskToExecute->execute(inputBuffer);
    if(returnCode == 0){
      wrln("SUCCESSFUL.");
    }
    else{
      wr("ERROR: "); wr(returnCode); wr(" (command: \""); wr(inputBuffer); wrln("\")");
    }
  }
  
  printEndOfCurrentIteration();
}

void printEndOfCurrentIteration(){
  //wrln(endingMessage);
  wrln("/>");
}

// The format of a setup changing command is:
// .settingToChange=new setting value
// Return values:
//       10 - Wrong argument format
//       11 - New value too long
//       14 - Setting not found
int setupChangeHandler(char *in){
  wr("Setup modification: ");
  wrln(in);

  if(in[0] != '.'){
    return 10;
  }
  
  char settingBuffer[bufferSize] = "";
  char valueBuffer[bufferSize] = "";
  int eqSignIndex = -1;
  for(int i = 1; i < strlen(in); ++i){
    if(in[i] == '='){
      eqSignIndex = i;
      break;
    }
    settingBuffer[i - 1] =  in[i];
  }

  if(eqSignIndex == strlen(in) - 1 || eqSignIndex < 2){
    return 10;
  }

  ++eqSignIndex;
  for(int i = eqSignIndex; i < strlen(in); ++i){
    valueBuffer[i - eqSignIndex] = in[i];
  }

  if(strlen(valueBuffer) > bufferSize){
    return 11;
  }
  
  wr("Setting \""); wr(settingBuffer); wr("\" to \""); wr(valueBuffer); wrln("\".");

  if(strcmp(settingBuffer, "devname") == 0){
    strcpy(deviceName, valueBuffer);
  }
  else if(strcmp(settingBuffer, "ssid") == 0){
    strcpy(ssid, valueBuffer);
  }
  else if(strcmp(settingBuffer, "pswd") == 0){
    strcpy(pswd, valueBuffer);
  }
  else{
    return 14;
  }
  
  return 0;
}

// Return codes:
//       1 - Configured SSID cannot be reached
//       4 - Password is incorrect
//       109 - Wi-Fi is in process of changing between statuses
// For further information, see the documentation of the ESP8266WiFi
int connectToWiFiHandler(char *in){
  wrln("Connecting to WiFi...");  
  wr("\tSSID: "); wrln(ssid);
  WiFi.mode(WIFI_STA);
  //WiFi.setSleepMode(WIFI_NONE_SLEEP);
  WiFi.begin(ssid, pswd);

  int timeout = 0, maxTimeout = 5000;
  while(WiFi.status() != WL_CONNECTED && timeout <= maxTimeout){
    wr(".");
    delay(500);
    timeout += 500;
  }

  if(WiFi.status() == WL_CONNECTED){
    wrln("*");
    wr("IP address: "); wrln(WiFi.localIP().toString().c_str());
    return 0;
  }
  wrln("\\");

  // Overwrite the return value if it would be zero
  return (WiFi.status() == 0)? 109 : WiFi.status();
}

// Return codes:
//       77 - The WiFi is not connected
//       66 - Could not connect
int connectToApplicationHandler(char *in){
  const int maxTryCount = 5;
  if(WiFi.status() != WL_CONNECTED){
    return 77;
  }
  WiFiClient appLoginClient;

  for(int tryCount = 1; tryCount <= maxTryCount; tryCount++){
    wr(tryCount); wr(". try to connect to host at "); wr(host); wr(":"); wrln(appLoginPort);
    if(appLoginClient.connect(host, appLoginPort)){
      wrln("OK");
      appLoginClient.println("Hello, this device #123987");
      return 0;
    }
    wrln("NotOK");
  }
  return 66;
}

int connectAllHandler(char *in){
  int wifiSuccess = connectToWiFiHandler("");
  if(wifiSuccess != 0){
    return wifiSuccess;
  }
  return connectToApplicationHandler("");
}

int startMeasurementHandler(char *in){
  for(int i = 0; i < nSamples; ++i){
    data[i].time1 = micros();
    bno055_read_linear_accel_xyz(&linaccData);
    bno055_read_quaternion_wxyz(&quaternionData);
    data[i].time2 = micros();
    data[i].acc_x = linaccData.x;
    data[i].acc_y = linaccData.y;
    data[i].acc_z = linaccData.z;
    data[i].quat_x = quaternionData.x;
    data[i].quat_y = quaternionData.y;
    data[i].quat_z = quaternionData.z;
    data[i].quat_w = quaternionData.w;
    
    delay(5);
  }

  return 0;
}

int printResultsHandler(char *in){
  for(int i = 0; i < nSamples; ++i){
    wr(data[i].acc_x); wr("\t");
    wr(data[i].acc_y); wr("\t");
    wr(data[i].acc_z); wr("\t");
    wr(data[i].quat_w); wr("\t");
    wr(data[i].quat_x); wr("\t");
    wr(data[i].quat_y); wr("\t");
    wr(data[i].quat_z); wr("\t");
    wr(data[i].time1); wrln(data[i].time2);
    delay(0);
  }

  return 0;
}

void getCalibration(){
  bno055_get_accelcalib_status(&accCalibration);
  bno055_get_magcalib_status(&magCalibration);
  bno055_get_gyrocalib_status(&gyroCalibration);
  bno055_get_syscalib_status(&sysCalibration);
}

int printCalibrationHandler(char *in){
  getCalibration();
  wrln("ACC\tMAG\tGYR\tSYS");
  wr(accCalibration);
  wr("\t");
  wr(magCalibration);
  wr("\t");
  wr(gyroCalibration);
  wr("\t");
  wrln(sysCalibration);

  return 0;
}

int printSensorInfoHandler(char *in){
  return notYetImplementedResult;
}

int initializeSensorHandler(char *in){
  BNO_Init(&bno);
  /* Set the oeration mode of the BNO055
   *  NDOF = Nine Degrees Of Freedom
   *  M4G = Magnetormetr For Gyroscope (use magnetom. data instead of the gyro)
   */
  bno055_set_operation_mode(OPERATION_MODE_NDOF);

  return 0;
}

// This metod uses Serial.print instead of the custom function
int quaternionOnlyHandler(char *in){
  bno055_quaternion oq;

  while(true){
    bno055_read_quaternion_wxyz(&oq);
    Serial.print(oq.x); Serial.print("\t");
    Serial.print(oq.y); Serial.print("\t");
    Serial.print(oq.z); Serial.print("\t");
    Serial.println(oq.w);

    delay(25);
  }
}
