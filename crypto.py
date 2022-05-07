import base64
import json
import os
from threading import Thread
import time
import cryptography
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.fernet import Fernet, InvalidToken


# Returns a string representation of a salt
def generate_salt(size=16):
    """Returns a string representation of a salt

    Args:
        size (int, optional): Random bytes size. Defaults to 16.

    Returns:
        string: String representation of random bytes
    """
    return base64.b64encode(os.urandom(size)).decode()

class InvalidKeyException(Exception):
    pass

# TODO add functionality to re-encrypt data after some timeout time
class crypto:
    """Cryptography class for Encrypting and Decrypting text
    """

    def __init__(self, pass_phrase, data, salt=generate_salt()):
        """initializes the crypto class

        Args:
            pass_phrase (str): the password for encrypting or decrypting
            data (str): the data we want to decrypt or encrypt
            salt (str, optional): string representation of a salt we want to use for creating key. Defaults to generate_salt().
        """
        self.data = str(data)
        self.salt = salt
        self.pass_phrase = pass_phrase
        self.die=False
        
        self.valid_key = True
        self.__max_counter = 20
        self.counter = self.__max_counter
        self.pass_watcher_thread = Thread(target=self.countdown)
        self.pass_watcher_thread.start()
        self.refresh_counter()

    def create_key(self):
        """creates key encryption

        Returns:
            bytes: key in form of bytes
        """
        
        # Taken from the website itse
        # https://cryptography.io/en/latest/fernet/#using-passwords-with-fernet
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=base64.b64decode(self.salt),
            iterations=10000
        )

        key = base64.urlsafe_b64encode(kdf.derive(self.pass_phrase.encode()))

        return key    


    def encrypt(self):
        """Encrypts the Data
        """
        # if self.encrypt_status == True:
        #     return
        if not self.valid_key:
            raise InvalidKeyException("Invalid PassPhrase")

        key = self.create_key()
        f = Fernet(key)
        self.data = f.encrypt(self.data.encode()).decode()
        # self.encrypt_level+=1
        # self.encrypt_status = True
        return self

    def decrypt(self):
        """Decrypts the data
        """
        # if self.encrypt_status == False:
        #     return
        if not self.valid_key:
            raise InvalidKeyException("Invalid PassPhrase")
        # if self.encrypt_level <= 0:
        #     return self
        
        key = self.create_key()

        try:
            f = Fernet(key)
            self.data = f.decrypt(self.data.encode()).decode()
        except InvalidToken:
            return self 
        except:
            raise InvalidKeyException("Invalid PassPhrase")
        # self.encrypt_level-=1
        # self.encrypt_status = False
        return self

    def countdown(self):
        """Will run in separate thread and will after some time, reset the pass_phrase and encrypt the data
        """
        while self.counter > 0:
            time.sleep(1)
            self.counter-=1
            if self.die == True:
                print("DIEE")
                return
        self.encrypt()
        self.valid_key=False
        self.pass_phrase = ""
            
    def update_pass_phrase(self, pass_phrase):
        """Will run after we have run down our countdown and we wish to again use the data, need to re enter password for encryption or decryption

        Args:
            pass_phrase (str): the password for encryption or decryption of the data
        """
        self.pass_phrase = pass_phrase
        self.valid_key = True
        self.refresh_counter()

    def refresh_counter(self):
        self.counter = self.__max_counter
        if self.pass_watcher_thread.is_alive():
            return
        self.pass_watcher_thread = Thread(target=self.countdown)
        self.pass_watcher_thread.start()

    def __str__(self):
        return json.dumps(self.to_dict())

    def to_dict(self):
        return {
            'salt':self.salt,
            'data':self.data
        }

    def clean(self):
        self.die=True