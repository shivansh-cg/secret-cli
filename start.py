import json

from prompt_toolkit.shortcuts import input_dialog

from cli import cliApp
from utils import toggle_input


class App:
    master_password = ""
    
    main_app = None # Handles the main tasks, like search and auto complete for everything
    view_app = None # Handles when we want to view the whole block
    list_app = None # Handles listing all the blocks after doing a search operation without single target
    edit_add_app = None # Handles when we are editing or adding a new secret to a block
    
    """
    Start with taking master password and also MFA(later on)
    """
    def authenticate(self):
        # self.master_password = input_dialog(
        #     title="Secret-cli",
        #     text="Please enter Master Password:",
        #     password=True,
        # ).run()
        self.master_password = toggle_input("Please Enter Master Password: ")        
        # TODO 
        # MFA_code = input_dialog(
        #     title="Secret-cli",
        #     text="Please enter Master Password:",
        #     password=True,
        # ).run()

        # !REMOVE
        print(f"Result = {self.master_password}")
        
    def __init__(self) -> None:
        self.authenticate()
        creds = []

        with open("user_cred.json", "r") as file:
            creds = json.loads(file.read())
            
        self.main_app = cliApp(creds)
        self.main_app.run()    
    
        
        

if __name__ == "__main__":
    app = App()
    
