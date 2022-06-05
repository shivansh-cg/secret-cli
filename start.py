import json
from prompt_toolkit import PromptSession, prompt

from prompt_toolkit.shortcuts import input_dialog

from BaseCLI import BaseCLI
from utils import cred_string, toggle_input

from record import RecordApp
from utils import toggle_input


from prompt_toolkit import prompt
from prompt_toolkit.history import InMemoryHistory
from prompt_toolkit.shortcuts import clear
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from prompt_toolkit.completion import NestedCompleter
import os
from crypto import crypto

from exceptions import WrongPassLimit
from listing import ListingApp

pattern_working_first = r'^((?:(?:(?:\w*):(?:\w*)) )+)(?:((?:copy)|(?:view)|(?:edit))|(\w*) ((?:copy)|(?:view)|(?:edit)))$'


pattern1 = r"^((?:(?:(?:\w*):(?:\w*)) )+)(?:((?:copy)|(?:view)|(?:edit))|(\w*) ((?:copy)|(?:view)|(?:edit)))?"

 
pattern_final= r'^((?:(?:(?:[^ :]*):(?:[^ :]*) ?))+)(?:((?:copy)|(?:view)|(?:edit))|(\w*) ((?:copy)|(?:view)|(?:edit)))?$'
link = r'regexr.com/6n1qo'
class App:
    master_password = ""
    
    main_app = None # Handles the main tasks, like search and auto complete for everything
    view_app = None # Handles when we want to view the whole block
    list_app = None # Handles listing all the blocks after doing a search operation without single target
    edit_add_app = None # Handles when we are editing or adding a new secret to a block
    creds = None
    """
    Start with taking master password and also MFA(later on)
    """
    def authenticate(self):
        # self.master_password = input_dialog(
        #     title="Secret-cli",
        #     text="Please enter Master Password:",
        #     password=True,
        # ).run()
        # TODO 
        # MFA_code = input_dialog(
        #     title="Secret-cli",
        #     text="Please enter Master Password:",
        #     password=True,
        # ).run()
        chances = 3
        while True:
            # ! Remove later
            # self.master_password = toggle_input("Please Enter Master Password: ")   
            self.master_password = "MyPass"     
            try:
                c = crypto(self.master_password, **json.loads(self.creds))
                self.creds = json.loads(c.decrypt().to_dict()['data'])
                break
            except:
                chances-=1
                if chances == 0:
                    raise WrongPassLimit("Maximum Wrong Password limit reached")
                print("Wrong Password")
                
        for i,cred in enumerate(self.creds):
            cred['id'] = i
    
    def __init__(self) -> None:
        # Read the credential file
        self.creds = []
        try:
            with open("encrypted_data.json", "r") as file:
                self.creds = (file.read())
            # Authenticate and decrypt
            self.authenticate()
        except:
            with open("user_cred.json", "r") as file:
                self.creds = (json.loads(file.read()))
                for i,cred in enumerate(self.creds):
                    cred['id'] = i
        
        
        # Preprocessing for searching
        self.search_preprocessing()
        
        self.main_app = BaseCLI(self.creds, self.process_input)
        # self.main_app = cliApp(creds#, self.input_rec)
        
        self.main_app.run()    
            
    def search_preprocessing(self):
        self.search_list = []
        # print(type(self.creds))
        for cred in self.creds:
            self.search_list.append(set([ f'{key}:{cred["info"][key]}' for key in cred['info'] ]))
            
            
    def search_result(self, processed_input):
        clear()
        args = processed_input['arg']
        search_filter = [ text for text in processed_input['arg'] if ':' in text]
        search_results = []
        for i,search in enumerate(self.search_list):
            match_found = True
            for r in search_filter:
                if r not in search:
                    match_found = False
            if match_found:
                search_results.append((cred_string(self.creds[i]), ",".join([k for k in (self.creds[i]['info'])])))
                
        # Check count and if there exists a sub command
        if len(search_results) == 0:
            print("No Results Found!")
            return
        app = ListingApp(search_results)
        chosen = app.run()
        chosen_id = json.loads(chosen[0])['id']
        return chosen_id
        print(chosen_id)
    
    def process_input(self, processed_input):
        # print("=============")
        # print(json.dumps(processed_input, indent=4))
        if processed_input['type'] == "search":
            chosen_id = self.search_result(processed_input)
            # print(self.creds[chosen_id])
            app = RecordApp(self.creds[chosen_id])
            app.run()
        # res = (text_input.split())
        
        # for i,search in enumerate(self.search_list):
        #     match_found = True
        #     for r in res:
        #         if r not in search:
        #             match_found = False
        #     if match_found:
        #         print(i)
        #         print(json.dumps(self.creds[i], indent=4))
        #         print(search)
        #         print("------------")
        #         print("------------")
        # for cred in self.creds:
        #     for r in res:
        #         r = r.split(":")
        #         if r[0] not in cred['info']:
        #         if r in cred['info']:
        #             hey="hey"
        # print("=============")
        # print(self.search_list[0])
        # print("=============")
        
        

if __name__ == "__main__":
    try:  
        app = App()
    except (WrongPassLimit):
        print("Max Limit reached for Wrong Passwords, Try Again")
        
    # from InquirerPy import inquirer

    # name = inquirer.text(message="What's your name:").execute()
    # fav_lang = inquirer.select(
    #     message="What's your favourite programming language:",
    #     choices=["Go", "Python", "Rust", "JavaScript"],
    # ).execute()
    # print(fav_lang)
    # creds = {}
    
    # for i in range(10000):
    #     creds[f'i'] = {
    #         "abcd": None,
    #         "dcba": None
    #     }
    # creds["hh"] = {
    #     "hgfdg": None,
    #     "ghfh": None
    # }
    # # with open("user_cred.json", "r") as file:
    # #     creds = json.loads(file.read())
    # # creds = dict(creds)
    # ps = PromptSession(">")
    # while True:
    #     ans = ps.prompt(">", completer=NestedCompleter.from_nested_dict(creds))
    #     # ans = ps.prompt(">")
    #     if ans == "Exit":
    #         break
    #     print("=============")
    #     print(ans)
    #  
    #     print("=============")

    
