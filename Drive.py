from __future__ import print_function
import os, io, sys #accessing files and directories
import tkinter as tk
from tkinter import filedialog #Using this for windows explorer popup 
import shutil #Used for zip archiving/extracting
import stat #Used to remove read_only off hidden files
import pickle #serialising auth data 
import os.path #for deleting files and finding directories
import csv #making and adding contacts
from apiclient import errors
from googleapiclient.discovery import build #google drive api
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.http import MediaIoBaseDownload, MediaFileUpload, MediaIoBaseUpload

import PyQt5
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt, QTimer, QThread, pyqtSignal, QObject
from PyQt5.QtWidgets import QProgressBar, QProgressDialog, QPushButton, QDialog, QMessageBox, QVBoxLayout

# If modifying these scopes, delete the file token.pickle.
#level of access we are requesting (full access)
SCOPES = ['https://www.googleapis.com/auth/drive']    

 #This is called if an error occurs when extracting zip files  
 #Clear the readonly bit and reattempt the removal 
def remove_readonly(func, path, _):
    os.chmod(path, stat.S_IWRITE)   
    func(path)

#This function is derived from the google drive api documentation
#It authenticates the user and asks for permission so access their google drive
def GoogleAuth(creds):
    if os.path.exists('token.pickle'): #This fail authenticates the user
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'client_id.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)
    #build our drive privelages, use service to access google drive functions
    service = build('drive', 'v3', credentials=creds)
    return service

#This function uploads a file to google drive
#It takes in the name of the file, its path, and the parent folder in google drive it should be uploaded under
#it returns the file id of the file you downloaded
def toDrive(file_name, file_path, folder_id, service, onerror=remove_readonly):
    CHUNK_SIZE = 256 * 1024
    try:
        file_metadata = {'name': file_name, 'parents': [folder_id]} #Metadata for the file we are going to upload
        media = MediaFileUpload(file_path, mimetype='application/zip',chunksize=CHUNK_SIZE, resumable=True) 
        request = service.files().create(body=file_metadata, media_body=media, fields='id')
        progress = progressBarUpload(request) #create instance off progress bar class
        progress.exec_() #execute it
        progress.hide() #hide it off the screen after
        print(file_name + " uploaded successfully")
        return 1 #returns 1 if it was successful
    except: 
        print("File could not be uploaded")
        return None

#This function pulls a file from google drive onto the pc
#it takes in the file_id of the file you wish to download
#it returns the file name of the downloaded file
def fromDrive(file_id, service, onerror=remove_readonly):
    print("from Drive id received:", file_id)
    request = service.files().get_media(fileId=file_id) #request download file
    fh = io.BytesIO() #specify to download as bytes     
    downloader = MediaIoBaseDownload(fh, request)
    print(downloader)
    progress = progressBarDownload(downloader) #create instance off progress bar class
    progress.exec_() #execute it
    progress.hide() #hide it off the screen after
    file = service.files().get(fileId=file_id).execute() #get file metadata
    file_name = file.get('name') #get the name from the metadata
    file_path = file_name+".zip" #We are going to download it to the StudioHub directory
    with io.open(file_path,'wb') as file: #open a new file in write binary mode
        fh.seek(0) #start writing form the 0th bit in the file (whole file)
        file.write(fh.read()) #write the file to the destination
        print("File written to", file_path)
    #return the full file path including the file name and return the file path without the name
    return file_name

#This opens a win explorer popup to select folder for upload
#returns the file path we selected
def selectFolder(onerror=remove_readonly):
    root = tk.Tk() #instantiating tkinter window
    root.withdraw() #Prevents tkinter gui opening
    select = False #will loop around until they select a file or choose to abandon
    while select == False:
        file_path = filedialog.askdirectory() #opening windows explorer
        if(file_path): #if they selected a file
            root.destroy() #Destroys tkinter window
            print(file_path) #printing the folders file path
            return file_path
        else: #they closed window without selecting a file
            return None

#Popup window asks which file you would like to compress
#It compresses the file into a zip file
def zip(project_name, file_path,onerror=remove_readonly):
    print("Select the file you wish to push to", project_name)
    #file_path = selectFolder() #opens up popup to select folder
    if(file_path): #If user selects a file
        try:
            file_name = os.path.basename(file_path) #file name without the rest of the file path
            print("Zipping", file_name, "and preparing it for upload")
            shutil.make_archive(file_name, 'zip', file_path) #compresses the file
            print("Successfully zipped contents of",file_path, "into", file_name+'.zip')
            return file_name #returns the file name to the upload function
        except: #return nothing if the zipping fails
            return None
    else: #do nothing and return None
        return None

#Popup window asks which directory you would like to unzip the inputted file into
def unzip(file_to_unzip, file_path, onerror=remove_readonly):
    print("Where would you like to save the file?")
    #We will be unzipping from the StudioHub directory and extracting to
    #wherever to user chooses to save the file
    #file_path = selectFolder() #where are we going to save the file?
    directory = file_path + '\ ' +file_to_unzip #New directory in the file path the user selected
    print("Extracting", file_to_unzip, "to", file_path)
    #extract(filename.zip, format is zip file, directory to extract to)
    shutil.unpack_archive(file_to_unzip+".zip", format='zip', extract_dir=directory)
    print("Successfully extracted contents of", file_to_unzip)
  

  #file_name is name of this particular sub folder, folder_id is the parent folder
  #eg if we are uploading a new project folder, folder_id is the StudioHub folder id
def upload(service, file_name, folder_id, onerror=remove_readonly):
    upload = True
    while upload == True:
        try:
            file_path = selectFolder()
            msg_box = QtWidgets.QProgressDialog()
            msg_box.setWindowTitle("Compressing File, Please Wait...")
            msg_box.setFixedSize(400,20)
            msg_box.setStyleSheet('background-color: darkSlateGray; color: white; font: Courier')
            msg_box.show()
            file_name = zip(file_name, file_path) #lets you choose a file and then zips the file
            msg_box.hide()
            if (file_name): #If zip returns a file name then user selected a file
                print("File:", file_name, "Path:",file_name+".zip")
                file_uploaded = toDrive(file_name, file_name+".zip",folder_id, service) 
                #uploads the zipped file to the drive
            else:
                print("No file pushed to project")
                return None
                #If the user chose not to select a file print this message
        except: 
            print("File could not be uploaded, please try again")
            #Will loop around again and let you upload a different file 
        try:
            if os.path.exists(file_name+".zip"):
                print("removing"+file_name+".zip") 
                os.remove(file_name+".zip") #delete the zipped file we uplaoded
                print("Zip file deleted")
            upload = False #breaks loop as file was successfully uploaded
            return file_uploaded #returns 1 if file was uploaded and zip deleted successfully
        except: 
            print("Zip file could not be deleted")
            #Will loop around again and let you upload a different file  

#Pass in the file_id of a file and retrive the file
def download(file_id, service):
    print("download: ",file_id)
    file_name = fromDrive(file_id,service) #download file from drive
    try:
        file_path = selectFolder()
        unzip(file_name, file_path) #unzip the file we downloaded
        os.remove(file_name+".zip") #delete the zipped file we downloaded
        return 1 #return 1 for success
    #leaving only the unzipped version
    except:#if they didn't select a file
        if os.path.exists(file_name+".zip"):
            os.remove(file_name+".zip") #delete zip file 
        return None #return and let them try again

#Deletes a file or a project, pass service, file/project id and parent folder id
#if deleting a project, pass in service, project_id
#if deleting an individual file, pass service and file_id
def delete(service, file_id):
    try:
        service.files().delete(fileId=file_id).execute()
        print("Deleted:", file_id)
    except:
        print("error deleting file")
             
                    
#searched through google drive for specific file
def searchFile(service,file_name):
    page_token = None
    results = service.files().list(
        q="name='" + file_name + "' and mimeType='application/vnd.google-apps.folder' and trashed=false",
        spaces='drive',fields='nextPageToken, files(id, name)',pageToken=page_token).execute()
    items = results.get('files', [])
    if not items:
        print('No files found with the name:', file_name)
        return 0, None
    else:
        print('Files:')
        for item in items:
            print(item)
            print('{0} ({1})'.format(item['name'], item['id']))
            folder_id = item['id']
        print("Folder id is:",folder_id)
        return 1, folder_id

def createFolder(service, name, parent_folder):
        #File metadata is set to the file name and is a folder
        file_metadata = {'name': name,
                        'mimeType': 'application/vnd.google-apps.folder', 
                        'parents': [parent_folder]}
        #creates a folder with that metadata 
        file = service.files().create(body=file_metadata, fields='id').execute()
        #print('Folder ID: %s' % file.get('id')) 
        file_id = file.get('id') #get the id of the newly created folder
        return file_id

def listProjects(folder_id,service):
    page_token = None 
    project_dict = {}
    while True:
        response = service.files().list(
            q="parents in '" + folder_id + "'and trashed=false",
            spaces='drive',fields='nextPageToken, files(id, name)', pageToken=page_token).execute()
        for file in response.get('files', []):
            # Process change
            project_name = file.get('name')
            project_id = file.get('id')
            project_dict[project_name] = project_id
            #print('Found:', project_name,':',project_id)
        page_token = response.get('nextPageToken', None)
        if page_token is None:
            break
    return project_dict

def newProject(folder_id, project_name, service):
    project_id = createFolder(service, project_name, folder_id)
    #response = input("Would you like to add a comment to the project? y/n: ")
    #if response == 'y':
        #insert_comment(service, project_id) #This feature doesn't work yet
    #else:
        #print("No comments added")
    return project_id

#Derived from google drive API documentation
#allows you to make a new comment on a file or folder
#This doesn't work yet
def insert_comment(service, file_id):
    comments = input("Comments:")
    new_comment = {'content': comments}
    service.comments().create(new_comment, file_id).execute()

def shareProject(service, folder_id, user_email):
    user_permission = {
    'type': 'user',
    'role': 'writer',
    'emailAddress': user_email}
    service.permissions().create(fileId=folder_id,body=user_permission,fields='id').execute()
    print("Project successfully shared with", user_email)

def addContact(contact_name, contact_email, contacts, onerror=remove_readonly):
    #if(contacts == None):
       # contacts = {}

    contact_info = [contact_name, contact_email] #our new contact information
    if (not os.path.exists("contacts.csv")): #If file doesn't exist
        with open('contacts.csv', 'wb', newline='') as file: #wb mode creates the file
            file.write('Name,EmailAddress') #writes the headers
            print("CSV file created")
    #If we added a new email and name, it means we already created dictionary when program started
    #so we just add the new entries to the csv file and to the dictionary, 
    # no need to create new dictionary from scratch
    if(contact_name and contact_email != None): 
        with open ("contacts.csv", 'a', newline='') as file:
            data = csv.writer(file) #open file in write mode
            data.writerow(contact_info) #write new contact to file
        with open ("contacts.csv", "r", newline='') as file:
            data = csv.reader(file) #open file in reader mode
            contacts[contact_name] = contact_email #add new entry to dictionary
    #We didn't add new contacts, so this is the first time we've opened the file 
    # So we must create the dicitonary from scratch and not just append it       
    if(contacts == None):
        with open ("contacts.csv", "r", newline='') as file:
            data = csv.reader(file) #open file in reader mode
            contacts = {} #create blank dictionary
            i = 0 #for skipping front row
            for row in data: #rows in csv file
                #Skipping the first row which is just the headers
                if (i == 0):
                    i = i+1
                    print("\n Name, Email")
                else: #iterate through contacts, adding them to dictonary and printing them
                    contacts[row[0]] = row[1] #contacts['name']['email'] returns email address
                    print("Name:",row[0],"Email:",contacts[row[0]])
    return contacts #return the dictionary


def deleteContact(contact_email, onerror=remove_readonly):
        lines = list() #empty list
        with open("contacts.csv", "r", newline='') as readFile: #open csv file
            reader = csv.reader(readFile)
            for row in reader: #add all the data from the csv file into the list
                lines.append(row)
                for entry in row: #for every entry in the rows of the new list
                    if entry == contact_email: #if an entry == contact email
                        print(entry, row)
                        lines.remove(row) #remove that row (name,email)
        with open("contacts.csv", "w", newline='') as writeFile: 
            #Overwrite the csv file with all the data besides the deleted contact 
            writer = csv.writer(writeFile)
            writer.writerows(lines)


class ThreadDownload(QThread):
    signal = pyqtSignal(int)
    def __init__(self, downloader):
        super(ThreadDownload,self).__init__()
        self.downloader = downloader

    def run(self):
        done = False
        while done == False:
            status, done = self.downloader.next_chunk()
            value = int(status.progress() * 100)
            print("Downloaded",value,"%")
            self.signal.emit(value)

#define the progress bar download class, this is the widget with the progress bar on it
# ive it its dimensions and style etc and instantiate a new progress bar for it
class progressBarDownload(QDialog):
    def __init__(self,downloader):
        super().__init__()
        self.downloader = downloader
        self.title = "Downloading"
        self.setWindowTitle(self.title)
        self.setFixedSize(400,60)
        vbox = QVBoxLayout()
        self.progressbar = QProgressBar() #instansiate a progress bar
        self.progressbar.setMaximum(100) #set its max value to 100 percent
        self.progressbar.setStyleSheet("QProgressBar {border: 2px solid grey;border-radius:8px;padding:1px}")
        vbox.addWidget(self.progressbar) #add it to the widget
        self.startProgressBar()
        self.setLayout(vbox)
        self.show()
 
    def startProgressBar(self):
        self.thread = ThreadDownload(self.downloader) #open new thread with downloader object
        self.thread.signal.connect(self.setProgressVal) 
        #connect the signal from the download thread to update the progress bar
        self.thread.start() #start the thread
 
    def setProgressVal(self, value):
        self.progressbar.setValue(value) #update the progress bar
        if(value == 100): #if its value is 100
            self.hide() #were finished so we can hide it

class ThreadUpload(QThread):
    signal = pyqtSignal(int)
    def __init__(self, request):
        super(ThreadUpload,self).__init__()
        self.request = request

    def run(self):
        response = None
        while response is None:
            status, response = self.request.next_chunk()
            if status:
                value = int(status.progress() * 100)
                print("Uplaoded",value,"%")
                self.signal.emit(value)
        #sometimes goes straight from 99% -> Done and freezes, this is a failesafe
        self.signal.emit(100)
        print(response)

#define the progress bar upload class, this is the widget with the progress bar on it
# ive it its dimensions and style etc and instantiate a new progress bar for it
class progressBarUpload(QDialog):
    def __init__(self,request):
        super().__init__()
        self.request = request
        self.title = "Uploading"
        self.setWindowTitle(self.title)
        self.setFixedSize(400,60)
        vbox = QVBoxLayout()
        self.progressbar = QProgressBar() #instansiate a progress bar
        self.progressbar.setMaximum(100) #set its max value to 100 percent
        self.progressbar.setStyleSheet("QProgressBar {border: 2px solid grey;border-radius:8px;padding:1px}")
        vbox.addWidget(self.progressbar) #add it to the widget
        self.startProgressBar()
        self.setLayout(vbox)
        self.show()
 
    def startProgressBar(self):
        self.thread = ThreadUpload(self.request) #open new thread with downloader object
        self.thread.signal.connect(self.setProgressVal) 
        #connect the signal from the download thread to update the progress bar
        self.thread.start() #start the thread
 
    def setProgressVal(self, value):
        self.progressbar.setValue(value) #update the progress bar
        if(value == 100): #if its value is 100
            self.hide() #were finished so we can hide it

def main():
#======================================Setup=================================================================    
#    creds = None
#    service = GoogleAuth(creds) #authenticate user, make sure permissions are accepted
#    exists, folder_id = searchFile(service,'StudioHub') #Check if folder exists and get its id
#    if (exists == 0): #if we have not created a google drive StudioHub folder
#        print("No folder named StudioHub existed, creating new one")
#        folder_id = createFolder(service, 'StudioHub', None) #Get folder_id of new folder created
#    else: #We have already created StudioHub folder, its id is the one from searchFile function
#        print("StudioHub folder already exists") 
#    #creates dictionary containing all contacts
#    contacts = addContact(None, None, None)
#=============================================================================================================
    #print(contacts['Conor']['email'])
    #appends the csv file and the contacts dictionary with new contact
    #contacts = addContact(name, email, contacts)


    #project_id = newProject(folder_id, service)
    #ans = input("Would you like to add team members to this project? y/n: ")
    #if (ans == 'y'):
        #email = input("Enter the team members email: ")
        #shareProject(service, project_id, email)
    #else:
        #print("No team members added")

    #This doesn't work yet
    #insert_comment(service, folder_id)

    #Upload a new file to folder and returns its file_id
    #project_name here is only relevent if we're pushing to a project
    #it just displays the name of the project when selecting a file to push
    #it does nothing else, leave as None if not needed
    #upload(service, None, folder_id)

    #Doesn't support downloading whole folders yet
    #download(file_id,service)

    #Lets you see all your projects within StudioHub folder
    #print("Listing all projects")
    #project_dict = listProjects(folder_id,service)
    #for projects in project_dict:
        #print(projects, ':',project_dict[projects])

    #Lets you see all the files in a particular project
    #listProjects(project_id,service)

    #Makes a new project inside StudioHub Folder, returns projects id
    #also allows you to push to project
    #newProject(folder_id,service)
    #newProject(folder_id,service)
    #project_dict = listProjects(folder_id,service)
    #for projects in project_dict:
        #print(projects, ':',project_dict[projects])
    pass
if __name__ == "__main__":
    main()
