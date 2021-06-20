from cryptography.fernet import Fernet

genkey = Fernet.generate_key()
file = open("genkeyfile.txt", "wb")
file.write(genkey)
file.close()
