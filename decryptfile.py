from cryptography.fernet import Fernet
import time

key = "mCrPIWf_sr-q8qMyicUfmYe8VGa7oTBecX0EzUM8hls="
encc = "e_c.txt"
encs = "e_s.txt"
enck = "e_k.txt"

encrypted_files = [encc, encs, enck]
count = 0

for decryption in encrypted_files:
    with open(encrypted_files[count], "rb") as f:
        data = f.read()  # opens files to read

    fernetkey = Fernet(key)
    decrypted = fernetkey.decrypt(data)  # secret key blank, set var as key, with key encrypt data.

    with open(encrypted_files[count], "wb") as f:
        f.write(decrypted)  # write encrypted data to new encrypted files

    count += 1
    time.sleep(1)