import StudioHub as s #lets us access the functions from the backend, eg: s.function()
import kivy #Using kivy to design the GUI 
from kivy.app import App
from kivy.uix.label import Label


creds = None
service = s.GoogleAuth(creds) #authenticate user, make sure permissions are accepted
exists, folder_id = s.searchFile(service,'StudioHub') #Check if folder exists and get its id
if (exists == 0): #if we have not created a google drive StudioHub folder
    print("No folder named StudioHub existed, creating new one")
    folder_id = s.createFolder(service, 'StudioHub', None) #Get folder_id of new folder created
else: #We have already created StudioHub folder, its id is the one from searchFile function
        print("StudioHub folder already exists") 
#creates dictionary containing all contacts
contacts = s.addContact(None, None, None)


class MyApp(App):
    def build(self):
        return Label(text="Hello world")


if __name__ == "__main__":
    MyApp().run()

