#include <FastLED.h>
#include <WiFi.h>

const char* ssid     = "NETGEAR94";
const char* password = "pinkskates674";

const int NUM_LEDS = 600;
const int DATA_PIN = 25;
const int CLOCK_PIN = 13;

const int COMMAND_LENGTH = 7;


WiFiServer server(80);
TaskHandle_t animationsTask;
TaskHandle_t serverTask;

CRGB leds[NUM_LEDS];

void setup()
{
  Serial.begin(115200);
  pinMode(LED_BUILTIN, OUTPUT);      // set the LED pin mode

  //start LED control
  FastLED.addLeds<WS2812, DATA_PIN, GRB>(leds, NUM_LEDS);
  for (int i = 0; i < NUM_LEDS; i++) {
    leds[i] = CRGB(0, 0, 0);
  }
  FastLED.show();

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
  digitalWrite(LED_BUILTIN, HIGH);
  Serial.println(WiFi.localIP());
  server.begin();


}

void response(WiFiClient client, int code) {
  
  client.print("HTTP/1.1 ");
  client.print(code);
  if(code == 200){
    client.println(" OK");
  } else {
    client.println(" BAD REQUEST");
  }
  client.println("Content-type:text/html");
  client.println();

  // the content of the HTTP response follows the header:
  client.print("Executed");
  client.println();
}

int executeCommands(WiFiClient client, int contentLength) {
  int commandCount = contentLength/COMMAND_LENGTH;
  byte body[contentLength];
  for (int i = 0; i < contentLength; i++) {
    body[i] = client.read();
  }
  if (contentLength != 0) {
    contentLength = 0;

    for(int i = 0; i < commandCount; i++){
      int ledStart = body[(i*COMMAND_LENGTH)];
      ledStart = ledStart << 8;
      ledStart += body[(i*COMMAND_LENGTH)+1];
      int ledEnd = body[(i*COMMAND_LENGTH)+2];
      ledEnd = ledEnd << 8;
      ledEnd += body[(i*COMMAND_LENGTH)+3];
      int r = body[(i*COMMAND_LENGTH)+4];
      int g = body[(i*COMMAND_LENGTH)+5];
      int b = body[(i*COMMAND_LENGTH)+6];

      Serial.print("ledStart: ");
      Serial.print(ledStart);
      Serial.print(", ledEnd: ");
      Serial.print(ledEnd);
      Serial.print(", r: ");
      Serial.print(r);
      Serial.print(" g: ");
      Serial.print(g);
      Serial.print(", b: ");
      Serial.println(b);

      for(int k = ledStart; k <= ledEnd; k++){
        leds[k] = CRGB(r,g,b);
      }
    }
    FastLED.show();
    return 1;
  }
  return 0;
}

void runServer() {
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
            int result = executeCommands(client, contentLength);
            if(result == 1){
              response(client, 200);
            } else {
              response(client, 400);
            }
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

void loop() {
  runServer();
}
