import win32gui
import win32api
import win32con
import ctypes
import pyautogui
import time

PUL = ctypes.POINTER(ctypes.c_ulong)

# Define the input structure
class INPUT(ctypes.Structure):
    _fields_ = [("type", ctypes.c_ulong),
                ("ki", ctypes.c_ulong * 4)]
    
class KeyBdInput(ctypes.Structure):
   _fields_ = [("wVk", ctypes.c_ushort),
               ("wScan", ctypes.c_ushort),
               ("dwFlags", ctypes.c_ulong),
               ("time", ctypes.c_ulong),
               ("dwExtraInfo", PUL)]


class HardwareInput(ctypes.Structure):
   _fields_ = [("uMsg", ctypes.c_ulong),
               ("wParamL", ctypes.c_short),
               ("wParamH", ctypes.c_ushort)]
   
   
class MouseInput(ctypes.Structure):
   _fields_ = [("dx", ctypes.c_long),
               ("dy", ctypes.c_long),
               ("mouseData", ctypes.c_ulong),
               ("dwFlags", ctypes.c_ulong),
               ("time", ctypes.c_ulong),
               ("dwExtraInfo", PUL)]
   
class Input_I(ctypes.Union):
   _fields_ = [("ki", KeyBdInput),
               ("mi", MouseInput),
               ("hi", HardwareInput)]

class Input(ctypes.Structure):
   _fields_ = [("type", ctypes.c_ulong),
("ii", Input_I)]
   

vf_window = win32gui.FindWindow(None, "Virtua Fighter 5 R.E.V.O.")  # Replace with the target window title

class WindowController:    
    
    @staticmethod
    def send_key(hwnd, key):
        win32api.PostMessage(hwnd, win32con.WM_KEYDOWN, key, 0)
        time.sleep(0.1)
        win32api.PostMessage(hwnd, win32con.WM_KEYUP, key, 0)

    @staticmethod
    def send_key_c(key_code, key_up=False):
        input_obj = INPUT()
        input_obj.type = 1  # Keyboard event
        input_obj.ki[0] = key_code
        input_obj.ki[1] = 0x0008  # Scan code
        input_obj.ki[2] = 0x0002 if key_up else 0x0000  # Key up flag
        input_obj.ki[3] = 0        
        ctypes.windll.user32.SendInput(1, ctypes.pointer(input_obj), ctypes.sizeof(input_obj))
        
    @staticmethod
    def press_key(key):
        extra = ctypes.c_ulong(0)
        ii_ = Input_I()

        flags = 0x0008

        ii_.ki = KeyBdInput(0, key, flags, 0, ctypes.pointer(extra))
        x = Input(ctypes.c_ulong(1), ii_)
        ctypes.windll.user32.SendInput(1, ctypes.pointer(x), ctypes.sizeof(x))

    @staticmethod
    def release_key(key):
        extra = ctypes.c_ulong(0)
        ii_ = Input_I()

        flags = 0x0008 | 0x0002

        ii_.ki = KeyBdInput(0, key, flags, 0, ctypes.pointer(extra))
        x = Input(ctypes.c_ulong(1), ii_)
        ctypes.windll.user32.SendInput(1, ctypes.pointer(x), ctypes.sizeof(x))
   
    @staticmethod
    def reload_watch_screen():                
        try:
            if vf_window:
                # Bring the window to the foreground                
                time.sleep(1)

                #i            
                WindowController.press_key(0x17)           
                time.sleep(0.25)
                WindowController.release_key(0x17)           
                time.sleep(0.25)

                #return
                WindowController.press_key(0x1C)           
                time.sleep(0.25)
                WindowController.release_key(0x1C)           
                time.sleep(5)
                
                #backspace
                WindowController.press_key(0x0E)           
                time.sleep(0.25)
                WindowController.release_key(0x0E)           
                time.sleep(1)

                #i
                WindowController.press_key(0x17)           
                time.sleep(0.25)
                WindowController.release_key(0x17)           
                time.sleep(1)
        except Exception as e:
            print(f"Exception while trying to make foreground window {e}")

win32gui.SetForegroundWindow(vf_window)