import board
import keypad
import rotaryio
import neopixel
import usb_hid
import busio
import displayio
import terminalio
import i2cdisplaybus
from adafruit_display_text import label
import adafruit_displayio_ssd1306
from adafruit_hid.keyboard import Keyboard
from adafruit_hid.keycode import Keycode
from adafruit_hid.consumer_control import ConsumerControl
from adafruit_hid.consumer_control_code import ConsumerControlCode

kbd = Keyboard(usb_hid.devices)
cc = ConsumerControl(usb_hid.devices)

pixels = neopixel.NeoPixel(board.D3, 6, brightness=0.2)
current_color = (0, 255, 120)

matrix = keypad.KeyMatrix(row_pins=(board.D10, board.D9),
                          column_pins=(board.D0, board.D1, board.D2, board.D6),
                          columns_to_anodes=True)

encoder =  rotaryio.IncrementalEncoder(board.D8, board.D7)
last_position = encoder.position

displayio.release_displays()
i2c = busio.I2C(scl=board.D5, sda=board.D4)
display_bus = i2cdisplaybus.I2CDisplayBus(i2c, device_address=0x3C)
display = adafruit_displayio_ssd1306.SSD1306(display_bus, width=128, height=32)

splash = displayio.Group()
layer_label = label.Label(terminal.FONT, text="Layer: LAPTOP", color=0xFFFFFF, x=0, y=8)
mode_label = label.Label(terminal.FONT, text ="Knob: VOL / BRGT", color=0xFFFFFF, x=0, y=24)
splash.append(layer_label)
splash.append(mode_label)
display.root_group = splash

current_layer = 0
colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0), (0, 255, 255), (255, 0, 255)]
led_brightness = 0.2

def  update_leds():
    pixels_brightness = led_brightness
    pixels.fill(current_color)
    
update_leds()


while True:
    event = matrix.events.get()
    if event:
        key_idx = event.key_number
        pressed = event.pressed
        
        if key_idx == 7 and pressed:
            current_layer = 1 - current_layer
            layer_label.text = "Layer: LED Config" if current_layer == 1 else "Layer: LAPTOP"
            mode_label.text = "Knob: LED BRGT" if current_layer == 1 else "Knob: VOL / BRGT"
            
            elif current_layer == 0:
                if pressed:
                    if key_idx == 0:
                        kbd.send(Keycode.CONTROL, Keycode.C)
                    elif key_idx == 1:
                        kbd.send(Keycode.CONTROL, Keycode.V)
                    elif key_idx == 2:
                        kbd.send(Keycode.CONTROL, Keycode.Z)
                    elif key_idx == 4:
                        cc.send(ConsumerControlCode.MUTE)
                    elif key_idx == 5:
                        cc.send(ConsumerControlCode.PLAY_PAUSE)
                    elif key_idx == 6:
                        cc.send(ConsumerControlCode.BRIGHTNESS_DECREMENT)
                        
                    elif current_layer == 1:
                        if pressed and key_idx in [0,1,2,4,5,6]:
                            c_idx = key_idx if key_idx < 3 else key_idx - 1
                            current_color = colors[c_idx]
                            update_leds()
                            
                        current_position = encoder.position
                        if current_position != last_position:
                            delta = current_position - last_position
                            last_position = current_position
                            
                            if current_layer == 0:
                                for _ in range(abs(delta)):
                                    if delta > 0:
                                        cc.send(ConsumerControlCode.VOLUME_INCREMENT)
                                    else:
                                        cc.send(ConsumerControlCode.VOLUME_DECREMENT)
                            else:
                                led_brightness += (delta*0.05)
                                led_brightness = max(0.0, min(1.0, led_brightness))
                                update_leds()
