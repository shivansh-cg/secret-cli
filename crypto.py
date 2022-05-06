import base64
import json
import os

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.fernet import Fernet


# Returns a string representation of a salt
def generate_salt(size=16):
    """Returns a string representation of a salt

    Args:
        size (int, optional): Random bytes size. Defaults to 16.

    Returns:
        string: String representation of random bytes
    """
    return base64.b64encode(os.urandom(size)).decode()


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
        
        # self.encrypt_status = False

        self.key = self.create_key()


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

        f = Fernet(self.key)

        self.data = f.encrypt(self.data.encode()).decode()
        # self.encrypt_status = True
        return self

    def decrypt(self):
        """Decrypts the data
        """
        # if self.encrypt_status == False:
        #     return

        f = Fernet(self.key)

        self.data = f.decrypt(self.data.encode()).decode()
        # self.encrypt_status = False
        return self

    def __str__(self):
        return json.dumps(self.to_dict())

    def to_dict(self):
        return {
            'salt':self.salt,
            'data':self.data
        }
