from Crypto.Cipher import AES
import base64

# Encrypted password (with correct Base64 padding)
cpass = "LjFWQMzS3GWDeav7+0Q0oSoOM43VwD30YZDVaItj8e0="

# Decode the Base64 string
passw = base64.b64decode(cpass)

# AES encryption key (from MSDN)
key = b"\x4e\x99\x06\xe8\xfc\xb6\x6c\xc9\xfa\xf4\x93\x10\x62\x0f\xfe\xe8\xf4\x96\xe8\x06\xcc\x05\x79\x90\x20\x9b\x09\xa4\x33\xb6\x6c\x1b"

# AES block size and mode
size = AES.block_size  # 16 bytes
mode = AES.MODE_CBC
IV = b'\x00' * size  # IV must be bytes

# Initialize AES decryptor
decryptor = AES.new(key, mode, IV=IV)

# Decrypt the password
decrypted = decryptor.decrypt(passw)

# Remove null bytes and decode
password = ''.join(decrypted.decode().split('\x00'))  # Removing null bytes
print(password)
