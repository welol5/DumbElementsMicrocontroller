#include <FastLED.h>
#include <Arduino_JSON.h>
#include <WiFi.h>

const char* ssid     = "NETGEAR94";
const char* password = "pinkskates674";

const int NUM_LEDS = 121;
const int DATA_PIN = 25;
const int CLOCK_PIN = 13;


WiFiServer server(80);

CRGB leds[NUM_LEDS];

void setup()
{
  Serial.begin(115200);
  pinMode(LED_BUILTIN, OUTPUT);      // set the LED pin mode

  delay(10);

  //connect to WiFi
  Serial.println();
  Serial.println();
  Serial.print("Connecting to ");
  Serial.println(ssid);
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("");
  Serial.println("WiFi connected.");
  Serial.println("IP address: ");
  Serial.println(WiFi.localIP());
  server.begin();

  //start LED control
  FastLED.addLeds<WS2812, DATA_PIN, GRB>(leds, NUM_LEDS);
  for(int i = 0; i < NUM_LEDS; i++){
    leds[i] = CRGB(0,0,0);
  }
  FastLED.show();
}

void loop() {
  WiFiClient client = server.available();

  if (client) {
    Serial.println("Client connected");

    String currentLine = "";
    int contentLength = 0;
    while (client.connected()) {
      if (client.available()) {
        char c = client.read();
        Serial.write(c);
        if (c == '\n') {
          if (currentLine.length() == 0) {
            JSONVar command = readBody(client, contentLength);
            Serial.println(command);
            executeCommand(command);
            response(client, 200);
            break;//disconnect from client, interaction finished
          } else {
            //end of header line
            //check content length header
            if (currentLine.startsWith("Content-Length: ")) {
              int split = currentLine.indexOf(" ");
              currentLine.remove(0, split);
              contentLength = currentLine.toInt();
            }
            currentLine = "";
          }
        } else if (c != '\r') {
          currentLine += c;
        }


      }
    }
    client.stop();
    Serial.println("Client Disconnected.");
  }

}

void response(WiFiClient client, int code) {
  //headers recived
  client.println("HTTP/1.1 200 OK");
  client.println("Content-type:text/html");
  client.println();

  // the content of the HTTP response follows the header:
  client.print("Click <a href=\"/H\">here</a> to turn the LED on pin 5 on. This does not work<br>");
  client.print("Click <a href=\"/L\">here</a> to turn the LED on pin 5 off.<br>");
  client.println();
}

JSONVar readBody(WiFiClient client, int contentLength) {
  String body = "";
  for (int i = 0; i < contentLength; i++) {
    body += (char)client.read();
  }
  if (contentLength != 0) {
    contentLength = 0;
    Serial.println(body);
    JSONVar command = JSON.parse(body);
    if (JSON.typeof(command) == "undefined") {
      Serial.println("Parsing input failed!");
      return NULL;
    } else {
      Serial.println("parse success");
    }
    return command;
  }
}

void executeCommand(JSONVar command) {
  Serial.println("execute");
  int ledStart = 0;
  int ledEnd = NUM_LEDS;
  int r = 0;
  int g = 0;
  int b = 0;

  //parse JSON
  if(command.hasOwnProperty("ledStart")){
    ledStart = (int)command["ledStart"];
  }
  if(command.hasOwnProperty("ledEnd")){
    ledEnd = (int)command["ledEnd"];
  }
  if(command.hasOwnProperty("r")){
    r = (int)command["r"];
  }
  if(command.hasOwnProperty("g")){
    g = (int)command["g"];
  }
  if(command.hasOwnProperty("b")){
    b = (int)command["b"];
  }

  Serial.println(ledStart);
  Serial.println(ledEnd);
  Serial.println(r);
  Serial.println(g);
  Serial.println(b);

  for(int i = ledStart; i < ledEnd && i < NUM_LEDS; i++){
    leds[i] = CRGB(r,g,b);
  }
  FastLED.show();
  Serial.println("LEDs should be showing");
}
