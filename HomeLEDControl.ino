#include <FastLED.h>
#include <WiFi.h>

const char* ssid     = "NETGEAR94";
const char* password = "pinkskates674";

const int NUM_LEDS = 600;
const int DATA_PIN = 25;
const int CLOCK_PIN = 13;


WiFiServer server(80);
TaskHandle_t animationsTask;
TaskHandle_t serverTask;

CRGB leds[NUM_LEDS];

struct LEDCommand {
  int ledStart;
  int ledEnd;
  int r;
  int g;
  int b;
};

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
  Serial.println(WiFi.localIP());
  server.begin();


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

int executeCommands(WiFiClient client, int contentLength) {
  String body = "";
  for (int i = 0; i < contentLength; i++) {
    body += (char)client.read();
  }
  if (contentLength != 0) {
    contentLength = 0;
    //    Serial.println(body);

    int lineCount = 0;
    int lastFoundIndex = 0;
    while (body.indexOf('\n', lastFoundIndex) != -1) {
      lineCount++;
      lastFoundIndex = body.indexOf('\n', lastFoundIndex) + 1;
    }
    lineCount++;//last line
    if (lineCount % 4 != 0) {
      Serial.println("Line count wrong");
      //      return NULL;
    } else {
      String lines[lineCount];
      lastFoundIndex = 0;
      for (int i = 0; i < lineCount; i++) {
        if (i == lineCount - 1) {
          lines[i] = body.substring(lastFoundIndex);
        } else {
          lines[i] = body.substring(lastFoundIndex, body.indexOf('\n', lastFoundIndex));
          lastFoundIndex = body.indexOf('\n', lastFoundIndex) + 1;
        }
      }
      int commandCount  = lineCount / 4;
      LEDCommand cmds[commandCount];
      int split;
      for (int i = 0; i < commandCount; i ++) {
        split = lines[(i*4)].indexOf('-');
        int ledStart = lines[(i*4)].substring(5, split).toInt();
        int ledEnd = lines[(i*4)].substring(split + 1).toInt();
        int r = lines[(i*4) + 1].substring(2).toInt();
        int g = lines[(i*4) + 2].substring(2).toInt();
        int b = lines[(i*4) + 3].substring(2).toInt();

        cmds[i] = {ledStart, ledEnd, r, g, b};
      }

    Serial.println("Commands executed:");
      for (int c = 0; c < commandCount; c++) {
        LEDCommand command = cmds[c];
        Serial.print(c);
        Serial.print(". ledStart: ");
        Serial.print(command.ledStart);
        Serial.print(", ledEnd: ");
        Serial.print(command.ledEnd);
        Serial.print(", r: ");
        Serial.print(command.r, HEX);
        Serial.print(", g: ");
        Serial.print(command.g, HEX);
        Serial.print(", b: ");
        Serial.println(command.b, HEX);
        for (int i = command.ledStart; i <= command.ledEnd; i++) {
          leds[i] = CRGB(command.r, command.g, command.b);
        }
      }
      FastLED.show();
      Serial.println("LEDs should be showing");
      return lineCount / 4;
    }
  }
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

void loop() {
  runServer();
}
