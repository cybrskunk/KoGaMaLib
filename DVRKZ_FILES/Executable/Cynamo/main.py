import os
import sys
from random import randint
from tkinter import Tk
from tkinter.filedialog import askopenfilename
from PIL import Image
from hashlib import sha256
from base64 import b64encode, b64decode

DIM_ORANGE = "\033[38;5;208m"
SAND_YELLOW = "\033[38;5;221m"
LIGHT_YELLOW = "\033[38;5;228m"
DIM_RED = "\033[38;5;124m"
RESET = "\033[0m"

HEADER_SIZE_BITS = 32  # Fixed header size

def text_to_bits(message: str) -> str:
    return ''.join(f"{b:08b}" for b in message.encode("utf8"))

def bits_to_text(bits: str) -> str:
    bytes_list = [int(bits[i:i+8], 2) for i in range(0, len(bits), 8)]
    return bytes(bytes_list).decode("utf8")

def open_image():
    Tk().withdraw()
    path = askopenfilename(filetypes=[("Images", "*.png;*.bmp;*.jpg;*.jpeg")])
    if not path:
        print(f"{DIM_RED}No file selected.{RESET}")
        return None
    img = Image.open(path).convert("RGBA")
    img.filename = path
    return img

def save_image(image):
    base, ext = os.path.splitext(image.filename)
    new_path = f"{base}_encoded{ext}"
    image.save(new_path)
    print(f"{LIGHT_YELLOW}Saved image as {new_path}{RESET}")

def update_pixel(pixel: tuple, bit: int) -> tuple:
    r, g, b, a = pixel
    if (r + g + b) & 1 != bit:
        channel = randint(0, 2)
        rgb = [r, g, b]
        rgb[channel] = (rgb[channel] + 1) % 256
        r, g, b = rgb
    return (r, g, b, a)

def write_bits(image: Image.Image, bits: str, start=0):
    width, height = image.size
    px = image.load()
    for i, bit in enumerate(bits):
        pos = start + i
        x, y = pos % width, pos // width
        px[x, y] = update_pixel(px[x, y], int(bit))

def read_bits(image: Image.Image, start: int, length: int) -> str:
    width, height = image.size
    px = image.load()
    bits = []
    for i in range(length):
        pos = start + i
        x, y = pos % width, pos // width
        r, g, b, _ = px[x, y]
        bits.append("1" if (r+g+b)&1 else "0")
    return ''.join(bits)

def hide_message():
    img = open_image()
    if not img: return
    message = input("Message to hide: ")
    bits = text_to_bits(message)
    width, height = img.size
    max_bits = width * height - HEADER_SIZE_BITS
    if len(bits) > max_bits:
        print(f"{DIM_RED}Message too large for image!{RESET}")
        return
    write_bits(img, f"{len(bits):0{HEADER_SIZE_BITS}b}", start=0)
    write_bits(img, bits, start=HEADER_SIZE_BITS)
    save_image(img)
    img.close()
    wait_for_input()

def read_message():
    img = open_image()
    if not img: return
    length = int(read_bits(img, 0, HEADER_SIZE_BITS), 2)
    bits = read_bits(img, HEADER_SIZE_BITS, length)
    try:
        msg = bits_to_text(bits)
        print(f"{LIGHT_YELLOW}Hidden message: {msg}{RESET}")
    except Exception:
        print(f"{DIM_RED}Failed to decode message.{RESET}")
    img.close()
    wait_for_input()

def hash_sha256(msg: str) -> str:
    return sha256(msg.encode()).hexdigest()

def dehash_sha256(hash_str: str, msg: str) -> bool:
    return hash_sha256(msg) == hash_str

def caesar_cipher(msg: str, shift: int) -> str:
    result = []
    for c in msg:
        if c.isalpha():
            base = ord('A') if c.isupper() else ord('a')
            result.append(chr(base + (ord(c)-base + shift) % 26))
        else:
            result.append(c)
    return ''.join(result)

def rot13(msg: str) -> str:
    return msg.translate(str.maketrans(
        'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz',
        'NOPQRSTUVWXYZABCDEFGHIJKLMnopqrstuvwxyzabcdefghijklm'
    ))

def xor_bytes(data: bytes, key: str) -> bytes:
    key_bytes = key.encode()
    return bytes(b ^ key_bytes[i % len(key_bytes)] for i, b in enumerate(data))

def caesar_menu():
    action = input("Encode (e) or Decode (d): ").strip().lower()
    if action not in 'ed': print(f"{DIM_RED}Invalid choice.{RESET}"); return
    msg = input("Message: ")
    shift = int(input("Shift: "))
    if action == 'd': shift = -shift
    print(f"{LIGHT_YELLOW}Result: {caesar_cipher(msg, shift)}{RESET}")
    wait_for_input()

def rot13_menu():
    action = input("Encode (e) or Decode (d): ").strip().lower()
    if action not in 'ed': print(f"{DIM_RED}Invalid choice.{RESET}"); return
    msg = input("Message: ")
    print(f"{LIGHT_YELLOW}Result: {rot13(msg)}{RESET}")
    wait_for_input()

def base64_menu():
    action = input("Encode (e) or Decode (d): ").strip().lower()
    msg = input("Message: ")
    try:
        if action == 'e':
            print(f"{LIGHT_YELLOW}Result: {b64encode(msg.encode()).decode()}{RESET}")
        elif action == 'd':
            print(f"{LIGHT_YELLOW}Result: {b64decode(msg).decode()}{RESET}")
        else:
            print(f"{DIM_RED}Invalid choice.{RESET}")
    except Exception as e:
        print(f"{DIM_RED}Error: {e}{RESET}")
    wait_for_input()

def xor_menu():
    action = input("Encrypt (e) or Decrypt (d): ").strip().lower()
    if action not in 'ed': print(f"{DIM_RED}Invalid choice.{RESET}"); return
    msg = input("Message: ").encode()
    key = input("Key: ")
    result = xor_bytes(msg, key)
    if action == 'e':
        print(f"{LIGHT_YELLOW}Encrypted (base64): {b64encode(result).decode()}{RESET}")
    else:
        print(f"{LIGHT_YELLOW}Decrypted: {result.decode(errors='ignore')}{RESET}")
    wait_for_input()

def main():
    while True:
        choice = show_menu()
        if choice == '1':
            msg = input("Message to hash: ")
            hashed = hash_sha256(msg)
            print(f"{LIGHT_YELLOW}SHA-256: {hashed}{RESET}")
            if input("Dehash? (y/n): ").strip().lower() == 'y':
                test = input("Test message: ")
                print(f"{LIGHT_YELLOW if dehash_sha256(hashed,test) else DIM_RED}"
                      f"{'Matches!' if dehash_sha256(hashed,test) else 'Does not match!'}{RESET}")
            wait_for_input()
        elif choice == '2': hide_message()
        elif choice == '3': read_message()
        elif choice == '4': caesar_menu()
        elif choice == '5': base64_menu()
        elif choice == '6': rot13_menu()
        elif choice == '7': xor_menu()
        elif choice == '8':
            print(f"{DIM_RED}Exiting...{RESET}"); break
        else:
            print(f"{DIM_RED}Invalid choice.{RESET}")

def show_menu():
    os.system('cls' if os.name == 'nt' else 'clear')
    print(f"{DIM_ORANGE}Welcome to CYNAMON - Stego & Crypto Tool{RESET}")
    print(f"{SAND_YELLOW}1. SHA-256 Hash{RESET}")
    print(f"{SAND_YELLOW}2. Hide Message in Image{RESET}")
    print(f"{SAND_YELLOW}3. Read Message from Image{RESET}")
    print(f"{SAND_YELLOW}4. Caesar Cipher{RESET}")
    print(f"{SAND_YELLOW}5. Base64 Encode/Decode{RESET}")
    print(f"{SAND_YELLOW}6. ROT13 Encode/Decode{RESET}")
    print(f"{SAND_YELLOW}7. XOR Encrypt/Decrypt{RESET}")
    print(f"{DIM_RED}8. Exit{RESET}")
    return input("Choice: ").strip()

def wait_for_input():
    action = input(f"{DIM_ORANGE}Type 'c' to continue or 'x' to exit: {RESET}").strip().lower()
    if action == 'x':
        print(f"{DIM_RED}Exiting...{RESET}")
        sys.exit()
    elif action == 'c':
        os.system('cls' if os.name == 'nt' else 'clear')

if __name__ == "__main__":
    main()
