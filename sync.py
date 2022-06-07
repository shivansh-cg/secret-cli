
from InquirerPy import inquirer
from InquirerPy.base.control import Choice
import qrcode
import random
import pyperclip

from InquirerPy.validator import NumberValidator, PasswordValidator

SERVER_URL = "http://localhost:5000"

class SyncHandler:
    
    def add_device():
        print("Please Visit the following Link, a code will be displayed.")
        print("That Code needs to be entered here later")
        
        qr = qrcode.QRCode()
        # ! Later use something else than random
        link = f"{SERVER_URL}/add_device?secret_code={random.randint(100000, 999999)}"
        pyperclip.copy(link)
        print("Link has aslo been copied into clipboard")
        qr.add_data(link)
        qr.make()
        qr.print_ascii(tty=True, invert=True)
        
        input("Press Enter when ready to proceed")
        
        device_code = inquirer.text(
            message="Enter the Device Code",
            validate=PasswordValidator(length=6)
        ).execute()
        
        
        # self.chosen_config = inquirer.select(
        #         message="How do you want to login?",
        #         choices= [
        #             "Enter Email(google email used to login) here and get the code from our website and enter here later",    
        #             "Visit website using the link and enter the code genereted on the page here later",    
        #         ],
        #         instruction="You need to be logged in to our website using Google(will be prompted if not)",
        #         long_instruction="You will get a code on our website and need to be entered here. ",
        #         cycle=True
        #     ).execute()
        
    
    def __init__(self, creds) -> None:
        self.creds = creds
        
        
        self.chosen_config = inquirer.select(
                message="Next Step?",
                choices= [
                    "Re-enter MFA Code",    
                    "Proceed to enter Device Code",    
                ],
                instruction="You need to be logged in to our website using Google(will be prompted if not)",
                long_instruction="You will get a code on our website and need to be entered here. ",
                cycle=True
            ).execute()
        
        
        if inquirer.confirm("Ready to enter code from the website here?",default=True, long_instruction="You will be prompted for code after this").execute():
            # Place the POST request to fetch creds
            pass
        else:
            return
if __name__ =="__main__":
    s = SyncHandler("asd")
    