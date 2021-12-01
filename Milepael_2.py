import random
import time
import os
import sys
import threading

# Om du kjører koden lokalt kan du sette DEBUG til True.
# -- printer til terminal i stedet for RPi sensehat

"""
En liten visualisering på hvordan BUFFER fungerer
Det er en liste, delt inn i 8 lister, alle med 8 verdier hver
Hver liste fungerer som en y verdi, og hvert element i listen fungerer som en x verdi
Ser litt sånn her ut:

BUFFER:
--                                           --
| y_0[x_0, x_1, x_2, x_3, x_4, x_5, x_6, x_7] |
| y_1[x_0, x_1, x_2, x_3, x_4, x_5, x_6, x_7] |
| y_2[x_0, x_1, x_2, x_3, x_4, x_5, x_6, x_7] |
| ... -->                                     |
--                                           --
Eksempel:
Med fuel ønsker vi bare å bruke x_7 pixler
Derfor henter vi disse pixlene med f.eks en for/while løkke
hvor y varierer, mens x er konstant
i = 0
while i < 8:
    x_kordinater = BUFFER[i][7]
    i += 1
"""

DEBUG = False

if not DEBUG:
    from sense_hat import SenseHat
    sense = SenseHat()

ROWS = 8
COLS = 8

FPS = 20
FRAME_DURATION = 1 / FPS

FUEL_SPAWN_CHANCE = 2
FUEL_DECREASE = 4
FUEL_FREQUENCY = 8
FUEL_SLOWNESS = 3

GATE_FREQUENCY = 8
GATE_WIDTH = 2
GATE_SLOWNESS = 4

CAR_Y_POS = 6

CAR_COLOR = (255, 255, 255)
FUEL_COLOR = (120, 255, 0)
GATE_COLOR = (255, 0, 0)
NOCOLOR = (0, 0, 0)

MUSIC_FILE = "soundtrack_mgp.wav"


def restrict_value(value, min_value, max_value):
    return max(min_value, min(max_value, value))

    
def move_car_to(pos):
    global car_x_pos
    car_x_pos = pos

    
def move_car(change):
    move_car_to(restrict_value(car_x_pos + change, 0, COLS - 1))


def get_gate_pos():
    """Returner x-posisjon til gate som du skal treffe med bilen"""
    #Bredden til banen er COLS minus bredden til fuel-baren
    game_width = COLS - 2
    right_pole_max = game_width - GATE_WIDTH

    gate_pos = random.randint(0, right_pole_max)
    return gate_pos

def get_fuel_pos():
    """Returnerer x-posisjon til fuel som du skal treffe"""
    fuel_pos = random.randint(0, 6)
    return fuel_pos

def draw_fuel(mod_buffer, x):
    """Mellom 0 og 8, 0 er null fuel, 8 er max fuel
    funksjonen tar inn buffer-variabel og x (fuel)
    returnerer en modifisert buffer"""
    x_pos_fuelGauge_lokal = 7 #sier bare hvilken kolonne du ønsker
    i = 0
    u = 0
    if x < 0:
        return mod_buffer
    if x > 8:
        x = 8
    #Dette skriver om på buffer, og lager en kollonne med fuel
    while i < x:
        mod_buffer[i][x_pos_fuelGauge_lokal] = (255 - u, u, 0)
        i += 1
        u += 36
    u = 0 #bruker u som nullverdi for neste whileløkke
        #og beholder i, ettersom i er y verdi for sorte pixler
    resterende_pixler = 8 - x
    while u < resterende_pixler:
        mod_buffer[i][x_pos_fuelGauge_lokal] = NOCOLOR
        u += 1
        i += 1
    return mod_buffer #returnerer en modifisert buffer


def draw_score_bar(buffer, score):
    """Tegner score på den øverste baren"""
    
    SCORE_BAR_COLOR = (133, 133, 133)
    SCORE_POINTS_COLOR = (133, 0, 255)
    BAR_Y_POS = 0
    BAR_LENGTH = 6

    #Får "score" over til binærtall eks: 19 --> 10011
    binary_str_score = str(bin(score))[2:]
    
    #Legger til bakgrunnen
    for x in range(BAR_LENGTH):
        buffer[BAR_Y_POS][x] = SCORE_BAR_COLOR

    #Legger til prikker for score
    for x_pos, char in enumerate(binary_str_score):
        if char == "1":
            buffer[BAR_Y_POS][x_pos] = SCORE_POINTS_COLOR

    #Returnerer den modifiserte bufferen
    return buffer


def intro_graphic():
    TheGame = 'Midjo GP'  # Spillets navn
    TheGame_odd = TheGame[::2] # Skiller ut odde karakterer
    TheGame_even = TheGame[1::2] # Skiller ut jevne karakterer

    g = (96, 125, 139)  # Gråfarge til bakgrunn
    w = (10, 10, 10)   # Hvit farge til bokstav
    r = (244, 66, 54)  # Rød farge til bokstav

    Background = []  # Tom liste som fylles av forløkke for bakgrunn
    # For løkke for å lage bakgrunn
    for color in range(0,64): # range 64 grunnet 64 pixler
        Background.append(g)


    # Første bilde med 1 bokstav
    Midjo = [w, g, g, g, w, g, g, g,
             w, w, g, w, w, g, g, g,
             w, g, w, g, w, g, g, g,
             w, g, g, g, w, g, g, g,
             w, g, g, g, g, g, g, g,
             g, g, g, g, g, g, g, g,
             g, g, g, g, g, g, g, g,
             g, g, g, g, g, g, g, g,]

    # Andre bilde med 2 bosktaver
    Grand = [w, g, g, g, w, g, g, g,
             w, w, g, w, w, g, g, g,
             w, g, w, g, w, g, g, g,
             w, g, g, g, w, g, g, g,
             w, r, r, g, g, g, g, g,
             r, g, g, g, g, g, g, g,
             r, g, r, r, g, g, g, g,
             g, r, r, g, g, g, g, g,] 

    # Tredje bilde med 3 bokstaver
    Prix = [w, g, g, g, w, g, g, g,
            w, w, g, w, w, g, g, g,
            w, g, w, g, w, g, g, g,
            w, g, g, g, w, g, g, g,
            w, r, r, g, g, r, r, g,
            r, g, g, g, g, r, g, r,
            r, g, r, r, g, r, r, g,
            g, r, r, g, g, r, g, g,]

    sense.set_pixels(Background)
    time.sleep(1)
    sense.set_pixels(Midjo)
    time.sleep(1)
    sense.set_pixels(Grand)
    time.sleep(1)
    sense.set_pixels(Prix)
    time.sleep(1)
  
    # for løkke for å stave spillnavn meg generel lengde på spillets navn. Dette selv om variablene er kortere
    for character in range(0, len(TheGame)):
      if character < len(TheGame_odd):  # Printer kun hvis charakter er innen range til odd variabel
        # Printer hver odde bokstav meg tekst hvit og sort bakgrunn
        sense.show_letter(TheGame_odd[character], text_colour=[255, 255, 255], back_colour=[0, 0 ,0])
        time.sleep(0.4)  # Delay på 0.4s
      if character < len(TheGame_even): # Printer kun hvis charakter er innen range til even variabel
        # Printer hver partall bokstav med hvit bakrunn og sort tekst
        sense.show_letter(TheGame_even[character], text_colour=[0,0,0], back_colour=[255, 255, 255])
        time.sleep(0.4)  # Delay på 0.4s
    sense.clear()  # Tømmer led-matrise


def nextLevel():
    # Sier hvilket Level vi befinner oss i
    Lvl = 3
    
    W = (255, 255, 255)
    B = (0, 0, 0)
    r = (255, 0, 0)
    
    # Tegner speedometeret
    speedometer = [
        B, B, W, W, W, W, B, B,
        B, W, B, B, B, B, W, B,
        W, B, B, B, B, B, B, W,
        W, B, B, B, B, B, B, W,
        W, B, B, B, B, B, B, W,
        W, B, B, B, B, B, B, W,
        B, W, B, B, B, B, W, r,
        B, B, W, B, B, W, r, r,
        ]
  
    # Definerer arugmentene, og sier rangen på index
    def print_speedometer(message, maxRange):
        sense.show_message(message, speed, text_colour=W, back_colour=B)
        for index in range(0, maxRange):
            plot_ranges(index)
    
    def plot_ranges(index):
        # Lister over alle speedometer nivåene fra 0 til 6
        color_ranges = [
            [(44, 45), (51, 52)],
            [(41, 45)],
            [(44, 45), (35, 36), (26, 27), (17, 18)],
            [(44, 45), (36, 37), (28, 29), (20, 21), (12, 13)],
            [(43, 44), (36, 37), (29, 30), (22, 23)],
            [(43, 47)],
            [(43, 44), (52, 53)],
            ]
    
        # Bytter ut pixlene i speedometeret med, 
        # hvilket speedometer nivå som vises
        pixels = [v for v in speedometer]
        for (start, end) in color_ranges[index]:
          for i in range(start, end):
            pixels[i] = r
        
        # Clearer og printer ut speedometeret for hvert nivå,
        # helt til den når siste nivå for angitt level 
        sense.clear()
        sense.set_pixels(pixels)
        sleep(0.4)
  
    # Hastigheten på teksten som printes        
    speed = 0.04
      
    # Sier hvilken speedometer nivåer som skal printes,
    # avhengig av hvilket level vi befinner oss i
    levelPixelRange = {
        1: 3,
        2: 5,
        3: 7,
        }
      
    # Level må indekseres i levelPixelRange  
    if Lvl == 0 or Lvl > 3:
        raise ValueError("Level must be 1, 2 or 3")
      
    # Printer ut meldingen av hvilket level vi befinner oss i, 
    # og alle nivåene på speedometeret
    print_speedometer("Lvl " + str(Lvl) , levelPixelRange[Lvl])
        
    sleep(1)
    

def game_over_graphic(score):
    StrScore = str(score)  # egen variabel med score som string
    sense.low_light = True   # Lav lysintensitet
  
    # Viser teksten med scroll speed 0.04s og farge vist i lister
    sense.show_message("Game Over! Score:", scroll_speed=0.04, text_colour=[255, 0, 0], back_colour=[194, 27, 209])
    
    # For-løkke for å printe poeng sum et siffer av gangen
    for number in range(0, len(StrScore)):   # for hvert siffer i poengsum
        sense.show_letter(StrScore[number], back_colour=[194, 27, 209])  # Bruker show letter for 
        time.sleep(0.4)  # Setter delay etter tall på 0.4s
        sense.clear(194, 27, 209)  # Clearer ut forgie siffer
        time.sleep(0.4) # Delay før neste siffer

    # Printer points til slutt med speed 0.04
    sense.show_message("Points", scroll_speed=0.04, back_colour=[194, 27, 209])
    sense.clear()  # Clearer matrise


def get_imu_values():
    """Få xyz-verdi"""
    _gyro = sense.get_gyroscope()
    pitch = _gyro["pitch"]
    return round(pitch)


def calculate_car_position(gyro):
    #Høyresving
    if gyro <= 180:
        pass

    #Venstresving
    if gyro >= 180:
        gyro = - abs(360 - gyro)

    #Endre bilposisjon
    return -(gyro // 10) + 3


def debug_print(buffer):
    os.system("clear")
    for line in buffer:
        for char in line:
            if char == NOCOLOR:
                print("..", end="")
            if char == CAR_COLOR:
                print("XX", end="")
            if char == GATE_COLOR:
                print("OO", end="")
        print()
    print()


def main():
    running = True
    iterator = 0
    score = 0
    fuel = 8
    turn = 0
    visible_fuel_list = []
    car_x_pos = 4

    #TODO: reformater koden slik at en kan endre level og dermed alle frekvenser
    #      automatisk.


    #TODO: Endre flyten i spillet slik at det er levler.
    # lvl 1 --> 32
    #   speedometer-gfx
    # lvl 2 --> 64
    #   speedometer-gfx
    # lvl 3 --> evig



    #Spillet starter
    if not DEBUG:
        intro_graphic()
        os.system("mpg123" + MUSIC_FILE)

    #Hovedloopen som kjører så lenge spillet varer
    while running:
        #Lager ny buffer (som til slutt skal printes til skjermen)
        buffer = [[NOCOLOR for x in range(COLS)] for y in range(ROWS)]


        #Finn nye gyro-verdier for xyz
        if not DEBUG:
            imu_values = get_imu_values()


        #Finn ut hvor bilen skal stå
        if not DEBUG:
            car_x_pos = calculate_car_position(imu_values)
        else:
            #TODO: legg inn keyboard-kontroller her så du kan 
            # styre med piltastene på pc
            car_x_pos = 3


        #Legg bilen til i printebuffer
        buffer[CAR_Y_POS][car_x_pos] = CAR_COLOR
        

        #Etter "GATE_FREQUENCY" iterasjoner, lag en ny gate
        if iterator % (GATE_FREQUENCY * GATE_SLOWNESS) == 0:
            gate_x_pos = get_gate_pos()
            gate_y_start = iterator
            gate_already_taken == False


        #Legg gaten til i printebuffer
        gate_y_pos = abs(iterator - gate_y_start) // GATE_SLOWNESS
        buffer[gate_y_pos][gate_x_pos] = GATE_COLOR                 #Venstre påle
        buffer[gate_y_pos][gate_x_pos + GATE_WIDTH] = GATE_COLOR    #Høyre påle


        #Etter "FUEL_FREQUENCY" iterasjoner, lag en ny gate
        if iterator % (FUEL_FREQUENCY * FUEL_SLOWNESS) == 1:
            fuel_x_pos = get_fuel_pos()
            fuel_y_start = iterator
            fuel_already_taken == False
            

        #Legg fuel til i printebuffer
        if iterator > 1:
            fuel_y_pos = abs(iterator - fuel_y_start) // FUEL_SLOWNESS
            buffer[fuel_y_pos][fuel_x_pos] = FUEL_COLOR
        

        #Fuelnivået synker hver GATE_FREQUENCY*FUEL_DECREASE 'te gang
        if iterator % (GATE_FREQUENCY*FUEL_DECREASE) == 0:
            if fuel_already_taken == False:
                fuel -= 1


        #Oppdaterer fuelbaren med verdi fra "fuel"
        buffer = draw_fuel(buffer, fuel)


        #Når bilen passerer en gate, sjekk om du traff
        if CAR_Y_POS == gate_y_pos:
            if gate_x_pos <= car_x_pos <= gate_x_pos + GATE_WIDTH:
                if fuel_already_taken == False:
                    if car_x_pos == gate_x_pos + GATE_WIDTH // 2:
                        score += 3
                        print("Score + 3")
                    else:
                        score += 1
                        print("Score + 1")

                    #Denne variablen passer på at du ikke tar fuelen flere ganger
                    fuel_already_taken = True


        #Tegner poengbar i toppen av skjermen
        draw_score_bar(buffer, score)


        #Når bilen passerer en fuel, sjekk om du traff
        if iterator > 1:
            if CAR_Y_POS == fuel_y_pos:
                if fuel_x_pos == car_x_pos:
                    fuel += 1
                    #TODO: Blink fuelbaren når du treffer fuel


        #Om tanken blir full renner det over
        if fuel > 8:
            fuel = 8


        #Inkrementer iterator
        iterator += 1


        #Print banen
        if DEBUG:
            debug_print(buffer)
        else:
            #Får alt over på éi liste i stedet for ei liste av lister
            flat_buffer = [element for sublist in buffer for element in sublist]

            #Printer til sensehat-skjermen
            sense.set_pixels(flat_buffer)


        #Om du går tom for fuel er spillet over
        if fuel <= 0:
            if DEBUG:
                break
            #TODO: Add Midjo som gråter når du går tom for fuel.
            game_over_graphic(score)
            running = False
        

        #Delay
        time.sleep(FRAME_DURATION)


def host_websocket():
    """
        Multiplayer is hosted on
        http://pearpie.is-very-sweet.org:5001/site/index.html
    """
    from flask import Flask
    from sense_hat import SenseHat
    from flask_cors import CORS
    from flask_socketio import SocketIO
    from logging.config import dictConfig
    
    app = Flask(__name__, static_url_path='/site', static_folder='web')
    cors = CORS(app)
    app.config['CORS_HEADERS'] = 'Content-Type'
    socketio = SocketIO(app, cors_allowed_origins="*")

    @socketio.on('move_to')
    def on_socket_move_to(json):
        # Json is in this case an int sent by the ws client
        move_car_to(json)
        print(car_x_pos)

    @socketio.on('move_left')
    def on_socket_move_left(json):
        move_car(-1)

    @socketio.on('move_right')
    def on_socket_move_right(json):
        move_car(1)

    @socketio.on('stop_moving_left')
    def on_socket_stop_move_left(json):
        # TODO: Implement holding button down to move car
        pass

    @socketio.on('stop_moving_right')
    def on_socket_stop_move_right(json):
        # TODO: Implement holding button down to move car
        pass

    def configure_flask_logger():
        """Makes the logs less verbose"""
        dictConfig({
            'version': 1,
            'formatters': {'default': {
                'format': '[%(asctime)s] %(levelname)s in %(module)s: %(message)s',
            }},
            'handlers': {'wsgi': {
                'class': 'logging.StreamHandler',
                'stream': 'ext://flask.logging.wsgi_errors_stream',
                'formatter': 'default'
            }},
            'root': {
                'level': 'ERROR',
                'handlers': ['wsgi']
            }
        })
    
    configure_flask_logger()
    port=443
    # Port 443 is HTTPS
    if port == 443:
        ssl_certificate_folder = "/etc/letsencrypt/live/epstin.com/"
        context = (ssl_certificate_folder + "cert.pem", ssl_certificate_folder + "privkey.pem")#certificate and key files
        app.run(host="0.0.0.0", port=port, ssl_context=context)
    else:
        app.run(host="0.0.0.0", port=port)
    socketio.run(app)

if __name__ == "__main__":
    # use command "sudo python3 Milepael_2.py host" to host multiplayer
    if len(sys.argv) == 0:
        if sys.argv[1] == "host":
            threading.Thread(target=host_websocket).start()
    main()
