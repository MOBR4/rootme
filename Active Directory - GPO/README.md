# Active Directory GPP Decryption Writeup

## Challenge

During a security audit, the network traffic during the boot sequence of a workstation enrolled in an Active Directory was recorded. Analyze this capture and find the administrator’s password.
## Approach

Initially, I knew that the task was to find the **admin password**. Upon investigating the environment, I suspected that the password might be stored in a **Group Policy Preferences (GPP) XML file**. **GPP** is a feature in **Active Directory** that can store passwords, including those of local admin accounts, and it was found that these passwords were often encrypted using AES. However, the encryption key was **publicly available**, which meant I could potentially decrypt the password if I found the right file.

**KEY : https://learn.microsoft.com/en-us/openspecs/windows_protocols/ms-gppref/2c15cbf0-f086-4c74-8b70-1f2fa45dd4be**

![image](https://github.com/user-attachments/assets/9ebe4a18-e29d-4025-990f-909242bf0bba)


To locate the GPP XML files, I decided to focus on **SMB traffic**. This was because SMB (Server Message Block) is a protocol commonly used for file sharing on Windows networks, including access to the **SYSVOL** share where GPP files are **stored**. These files can be accessed by domain users, and it was highly likely that the encrypted password I was looking for was stored in one of these files.

### SMB Filter in Wireshark

To filter SMB traffic, I used the following filter in Wireshark:

```
smb || smb2
```

This filter captures all SMB-related traffic, including requests to read and write files on the network. Specifically, I was looking for SMB requests related to **Group Policy Preferences (GPP)** XML files stored in the `SYSVOL` directory on domain controllers.

I found this part of **group.xlm** when following the tcp stream of smb2 :

![image](https://github.com/user-attachments/assets/898a615d-49d0-44dd-adfe-3909cb85c131)

**cpassword for Administrateur : LjFWQMzS3GWDeav7+0Q0oSoOM43VwD30YZDVaItj8e0**


## The Decryption Script

To recover the passwords, I wrote a Python script that utilizes the known AES encryption key to decrypt the credentials. The key is publicly known due to the misuse of GPP by Microsoft, and the IV used during encryption is a fixed value.

### Script to Decrypt the GPP Encrypted Password

```python
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
```

### Explanation of the Script

1. **Base64 Decoding:**
   The encrypted password is first Base64-decoded to retrieve the raw binary data.
   
2. **AES Decryption:**
   - The script uses the **AES** algorithm in **CBC mode**.
   - A known static **AES key** (from Microsoft documentation) is used to initialize the AES decryption object.
   - The **IV** is set to 16 null bytes (`\x00`), which is the standard IV used by Microsoft for GPP encryption.
   
3. **Null Byte Removal:**
   After decryption, the script removes any null bytes (`\x00`) from the decrypted string to clean the output and reveal the plaintext password.



   ![image](https://github.com/user-attachments/assets/3945f4ad-2056-4396-a949-10d1805ad056)

