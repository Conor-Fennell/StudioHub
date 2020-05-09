import sys
import tkinter as tk
from tkinter import filedialog  # Using this for windows explorer popup

import PyQt5
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (QApplication, QCompleter, QHBoxLayout, QLabel,
                             QLineEdit, QMainWindow, QPushButton, QScrollArea,
                             QSizePolicy, QSpacerItem, QVBoxLayout, QWidget, QMessageBox
                             ,QErrorMessage, QInputDialog, QFormLayout)

import StudioHub as s

creds = None
service = s.GoogleAuth(creds) #authenticate user, make sure permissions are accepted
exists, folder_id = s.searchFile(service,'StudioHub') #Check if folder exists and get its id
if (exists == 0): #if we have not created a google drive StudioHub folder
    print("No folder named StudioHub existed, creating new one")
    folder_id = s.createFolder(service, 'StudioHub', None) #Get folder_id of new folder created
else: #We have already created StudioHub folder, its id is the one from searchFile function
        print("StudioHub folder already exists") 

class ProjectWidget(QWidget):
    def __init__(self, name, project_id):
        super(ProjectWidget, self).__init__()
        self.name = name
        self.project_id = project_id
        self.is_on = False

        self.lbl = QLabel(self.name)
        self.btn_upload = QPushButton("Upload to Project")
        self.btn_download = QPushButton("View Project")
        self.btn_collab = QPushButton("Make Collaborative")

        self.hbox = QHBoxLayout()
        
        self.hbox.addWidget(self.lbl)
        self.hbox.addWidget(self.btn_upload)
        self.hbox.addWidget(self.btn_download)
        self.hbox.addWidget(self.btn_collab)

        self.btn_upload.clicked.connect(self.uploadToProj)
        self.btn_download.clicked.connect(self.viewProj)
        self.btn_collab.clicked.connect(self.collaborateProj)
        
        self.setLayout(self.hbox)

    def show(self):

        for w in [self, self.lbl, self.btn_upload, self.btn_download, self.btn_collab]:
            w.setVisible(True)

    def hide(self):

        for w in [self, self.lbl, self.btn_upload, self.btn_download, self.btn_collab]:
            w.setVisible(False)
            
    def uploadToProj(self):
        print(self.name, "id is",self.project_id)
        loop = True #reacurring loop if we keep cancelling uploads and then say we want to upload
        while (loop == True):
            file_uploaded = s.upload(service, self.name, self.project_id)
            if(file_uploaded == None):
                q_box = QtWidgets.QMessageBox #create a message box asking do you want to upload to the project
                response = q_box.question(self,'', "You did not select a file. Continue with upload?", q_box.Yes | q_box.No)
                if (response != q_box.Yes): 
                    loop = False
            else: #This means we uploaded a file successfully
                loop = False

    def viewProj(self, project_id):
        print("id is",self.project_id)
        self.thisProj_dict = s.listProjects(self.project_id, service)
        self.FileWin = FilesWindow(self.project_id) 
        #pass the project_id and assign self.FileWin to next window
        self.FileWin.show() #show the file window
        w.hide() #hide project window
        #here we need to switch to other window
 
    def collaborateProj(self):
        print("collab")
        #s.shareProject(service, folder_id, user_email)
        pass

#Main window that opens when we start the program, 
#has all the projects and contacts button, create project etc
class ProjectsWindow(QMainWindow):
    def __init__(self, *args, **kwargs):
        super().__init__()
        project_dict = s.listProjects(folder_id,service)
       
        self.create = QtWidgets.QPushButton(self)
        self.create.setText("Create Project")
        self.create.clicked.connect(self.createProj)

        self.view = QtWidgets.QPushButton(self)
        self.view.setText("View All Projects")
        self.view.clicked.connect(self.projView)

        self.contacts = QtWidgets.QPushButton(self)
        self.contacts.setText("Contacts")
        self.contacts.clicked.connect(self.contactsView)

        self.controls = QWidget()  # Controls container widget.
        self.controlsLayout = QVBoxLayout()   # Controls container layout.

        # List of names, widgets are stored in a dictionary by these keys.  
        self.widgets = []

        #Iterating through all the projects, creating a widget 
        #for each one with an upload and download button
        for name in project_dict:
            project_id = project_dict[name]
            #print("adding",name, "to widget:", project_id, "ProjectWindow")
            item = ProjectWidget(name, project_id) #make a project widget with the name of the current project
            self.controlsLayout.addWidget(item)
            self.widgets.append(item) #append it to our list of widgets of projects

        spacer = QSpacerItem(1, 1, QSizePolicy.Minimum, QSizePolicy.Expanding)  
        self.controlsLayout.addItem(spacer)
        self.controls.setLayout(self.controlsLayout)

        # Scroll Area Properties.
        self.scroll = QScrollArea()
        self.scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll.setWidgetResizable(True)
        self.scroll.setWidget(self.controls)

        # Search bar.
        self.searchbar = QLineEdit()
        self.searchbar.textChanged.connect(self.update_display)

        # Adding Completer.
        self.completer = QCompleter(project_dict)
        self.completer.setCaseSensitivity(Qt.CaseInsensitive)
        self.searchbar.setCompleter(self.completer)

        #Add the items to VBoxLayout (applied to container widget) 
        #which encompasses the whole window.
        container = QWidget()
        containerLayout = QVBoxLayout()
        containerLayout.addWidget(self.create)
        containerLayout.addWidget(self.view)
        containerLayout.addWidget(self.contacts)
        containerLayout.addWidget(self.searchbar)
        containerLayout.addWidget(self.scroll)

        container.setLayout(containerLayout)
        self.setCentralWidget(container)

        self.setGeometry(600, 200, 600, 600)
        self.setWindowTitle('StudioHub')

    def update_display(self, text):
        for widget in self.widgets:
            if text.lower() in widget.name.lower():
                widget.show()
            else:
                widget.hide()

    def createProj(self): 
        #Text input doalog window to input project name
        text, ok = QInputDialog.getText(self, 'New Project', 'Name your project:')
        if (ok): #if okay button pressed
            project_name = str(text) #project name is string of inputted text
            project_id = s.newProject(folder_id, project_name, service) #make a new project with that name
            #dont need to update dictionary as its updated when the window refreshes
            q_box = QtWidgets.QMessageBox #create a message box asking do you want to upload to the project
            response = q_box.question(self,'', "Would you like to upload a file to this project?", q_box.Yes | q_box.No)
            if (response == q_box.Yes): #if you want to upload, do this
                s.upload(service, project_name, project_id)
        #refresh window
        self.ProjWin = ProjectsWindow() #project dictionary is updated when window is initialised again
        self.ProjWin.update()#updates the window so the new projects are shown
        self.ProjWin.show() #show the window 
        self.hide() #hide current window

    def projView(self):
        print("This is already the current window")
        
    def contactsView(self):
        self.contView = ContactsWindow()
        self.contView.show()
        self.hide()
        #this will to take us to scrollable contacts view

#viewing the files inside an indiviual project
class viewWidget(QWidget):
    def __init__(self, name, fileProj_id):
        super(viewWidget, self).__init__()
        self.fileProj_id = fileProj_id #file_id and project_id
        self.name = name #name of file
        self.is_on = False
        #labelling the buttons and labels
        self.lbl = QLabel(self.name)
        self.btn_download = QPushButton("Download")
        self.btn_delete = QPushButton("Delete")

        self.hbox = QHBoxLayout()
        #adding the widgets
        self.hbox.addWidget(self.lbl)
        self.hbox.addWidget(self.btn_download)
        self.hbox.addWidget(self.btn_delete)
        #linking the buttons to the functions
        self.btn_download.clicked.connect(self.down) 
        self.btn_delete.clicked.connect(self.delete)
        
        self.setLayout(self.hbox)

    def show(self):
        for w in [self, self.lbl, self.btn_download, self.btn_delete]:
            w.setVisible(True)

    def hide(self):
        for w in [self, self.lbl, self.btn_download, self.btn_delete]:
            w.setVisible(False)
            
    def down(self, fileProj_id):
        print("Downloading file with id:",self.fileProj_id[0])
        s.download(self.fileProj_id[0], service) #download the file from the drive

    def delete(self, fileProj_id): 
        try:
            qm = QtWidgets.QMessageBox #Message box asks if you want to delete the file
            response = qm.question(self,'', "Are you sure you want to delete this file?", qm.Yes| qm.No)
            if response == qm.Yes: #if response is yes, deletes the file
                s.delete(service, self.fileProj_id[0])
                self.FileWin = FilesWindow(self.fileProj_id[1]) #fileProj_id[1] = project_id
                self.FileWin.hide() #updates the window so the deleted file is not shown anymore
                self.hide()
            else:
                print("User chose not to delete", self.name)
        except: #if file doesn't exist, must already be deleted
            error_dialog = QtWidgets.QErrorMessage() #show file already deleted error msg
            error_dialog.showMessage("File already deleted")
            error_dialog.setWindowTitle("File error")
            error_dialog.exec_()
  
#Window when we view a particular project, has create and contacts buttons 
#and displays all file in a project in a scrollable area with options for each file
class FilesWindow(QMainWindow): 
    def __init__(self, project_id):
        super().__init__()
        thisProj_dict = s.listProjects(project_id,service)
        print("FilesWindow loading")
        print("This project_dict", thisProj_dict)
        self.create = QtWidgets.QPushButton(self)
        self.create.setText("Create Project")
        self.create.clicked.connect(self.createProj)

        self.view = QtWidgets.QPushButton(self)
        self.view.setText("View All Projects")
        self.view.clicked.connect(self.projView)

        self.contacts = QtWidgets.QPushButton(self)
        self.contacts.setText("Contacts")
        self.contacts.clicked.connect(self.contactsView)

        self.controls = QWidget()  # Controls container widget.
        self.controlsLayout = QVBoxLayout()   # Controls container layout.
        
        self.widgets = []
        #Iterating through all the projects, creating a widget 
        #for each one with an upload and download button
        for name in thisProj_dict:
            file_id = thisProj_dict[name] #access file_id from the dictionary
            fileProj_id = [file_id, project_id] #bundle it into list object
            #print("adding",name, "to widget:", file_id, "FilesWindow")
            item = viewWidget(name, fileProj_id) #make a project widget with the name of the current project
            #and with the list with file_id and project_id
            self.controlsLayout.addWidget(item)
            self.widgets.append(item) #append it to our list of widgets of projects


        spacer = QSpacerItem(1, 1, QSizePolicy.Minimum, QSizePolicy.Expanding)  
        self.controlsLayout.addItem(spacer)
        self.controls.setLayout(self.controlsLayout)

        # Scroll Area Properties.
        self.scroll = QScrollArea()
        self.scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll.setWidgetResizable(True)
        self.scroll.setWidget(self.controls)

        # Search bar.
        self.searchbar = QLineEdit()
        self.searchbar.textChanged.connect(self.update_display)

        # Adding Completer.
        self.completer = QCompleter()
        self.completer.setCaseSensitivity(Qt.CaseInsensitive)
        self.searchbar.setCompleter(self.completer)


        #Add the items to VBoxLayout (applied to container widget) 
        #which encompasses the whole window.
        container = QWidget()
        containerLayout = QVBoxLayout()
        containerLayout.addWidget(self.create)
        containerLayout.addWidget(self.view)
        containerLayout.addWidget(self.contacts)
        containerLayout.addWidget(self.searchbar)
        containerLayout.addWidget(self.scroll)

        container.setLayout(containerLayout)
        self.setCentralWidget(container)

        self.setGeometry(600, 200, 600, 600)
        self.setWindowTitle('StudioHub')


    def update_display(self, text):
        for widget in self.widgets:
            if text.lower() in widget.name.lower():
                widget.show()
            else:
                widget.hide()

    def createProj(self): 
        #Text input doalog window to input project name
        text, ok = QInputDialog.getText(self, 'New Project', 'Name your project:')
        if (ok): #if okay button pressed
            project_name = str(text) #project name is string of inputted text
            project_id = s.newProject(folder_id, project_name, service) #make a new project with that name
            project_dict = s.listProjects(folder_id,service)
            project_dict[project_name] = project_id #add this project to the dictionary
            q_box = QtWidgets.QMessageBox #create a message box asking do you want to upload to the project
            response = q_box.question(self,'', "Would you like to upload a file to this project?", q_box.Yes | q_box.No)
            if (response == q_box.Yes): #if you want to upload, do this
                s.upload(service, project_name, project_id)

    def projView(self):
        self.ProjWin = ProjectsWindow() 
        self.ProjWin.update()#updates the window so the new projects are shown
        self.ProjWin.show() #show the window 
        self.hide() #hide current window

    def contactsView(self):
        self.contView = ContactsWindow()
        self.contView.show()
        self.hide()
        #this will to take us to scrollable contacts view

#viewing the contacts widget
class contactsWidget(QWidget):
    def __init__(self, name, user_email):
        super(contactsWidget, self).__init__()
        self.user_email = user_email
        self.name = name #name of file
        self.is_on = False
        #labelling the buttons and labels
        self.lbl_name = QLabel(self.name)
        self.lbl_email = QLabel(self.user_email)
        self.btn_share = QPushButton("Add to Project")
        self.btn_delete = QPushButton("Delete Contact")

        self.hbox = QHBoxLayout()
        #adding the widgets
        self.hbox.addWidget(self.lbl_name)
        self.hbox.addWidget(self.lbl_email)
        self.hbox.addWidget(self.btn_share)
        self.hbox.addWidget(self.btn_delete)
        #linking the buttons to the functions
        self.btn_share.clicked.connect(self.share) 
        self.btn_delete.clicked.connect(self.delete)
        
        self.setLayout(self.hbox)

    def show(self):
        for w in [self, self.lbl_name,self.lbl_email, self.btn_share, self.btn_delete]:
            w.setVisible(True)

    def hide(self):
        for w in [self, self.lbl_name,self.lbl_email, self.btn_share, self.btn_delete]:
            w.setVisible(False)
            
    def share(self, file_id):
        print("Share contact button pressed")
        pass

    def delete(self, user_email): 
        print("Delete contact button pressed")
        pass
  
#Window when we view contacts
class ContactsWindow(QMainWindow): 
    def __init__(self):
        super().__init__()
        contacts = s.addContact(None, None, None)
        #updates contacts dictionary
        self.create = QtWidgets.QPushButton(self)
        self.create.setText("Create Project")
        self.create.clicked.connect(self.createProj)

        self.view = QtWidgets.QPushButton(self)
        self.view.setText("View All Projects")
        self.view.clicked.connect(self.projView)

        self.contacts = QtWidgets.QPushButton(self)
        self.contacts.setText("Add New Contact")
        self.contacts.clicked.connect(self.addNew)

        self.controls = QWidget()  # Controls container widget.
        self.controlsLayout = QVBoxLayout()   # Controls container layout.
        
        self.widgets = []
        #Iterating through all the projects, creating a widget 
        #for each one with an upload and download button
        for name in contacts:
            user_email = contacts[name] #accessing email from dictionary of contacts
            item = contactsWidget(name, user_email) #make a project widget with the name of the current project
            #and with the list with file_id and project_id
            self.controlsLayout.addWidget(item)
            self.widgets.append(item) #append it to our list of widgets of projects

        spacer = QSpacerItem(1, 1, QSizePolicy.Minimum, QSizePolicy.Expanding)  
        self.controlsLayout.addItem(spacer)
        self.controls.setLayout(self.controlsLayout)

        # Scroll Area Properties.
        self.scroll = QScrollArea()
        self.scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll.setWidgetResizable(True)
        self.scroll.setWidget(self.controls)

        # Search bar.
        self.searchbar = QLineEdit()
        self.searchbar.textChanged.connect(self.update_display)

        # Adding Completer.
        self.completer = QCompleter()
        self.completer.setCaseSensitivity(Qt.CaseInsensitive)
        self.searchbar.setCompleter(self.completer)


        #Add the items to VBoxLayout (applied to container widget) 
        #which encompasses the whole window.
        container = QWidget()
        containerLayout = QVBoxLayout()
        containerLayout.addWidget(self.create)
        containerLayout.addWidget(self.view)
        containerLayout.addWidget(self.contacts)
        containerLayout.addWidget(self.searchbar)
        containerLayout.addWidget(self.scroll)

        container.setLayout(containerLayout)
        self.setCentralWidget(container)

        self.setGeometry(600, 200, 600, 600)
        self.setWindowTitle('StudioHub')


    def update_display(self, text):
        for widget in self.widgets:
            if text.lower() in widget.name.lower():
                widget.show()
            else:
                widget.hide()

    def createProj(self): 
        #Text input doalog window to input project name
        text, ok = QInputDialog.getText(self, 'New Project', 'Name your project:')
        if (ok): #if okay button pressed
            project_name = str(text) #project name is string of inputted text
            project_id = s.newProject(folder_id, project_name, service) #make a new project with that name
            project_dict = s.listProjects(folder_id,service)
            project_dict[project_name] = project_id #add this project to the dictionary
            q_box = QtWidgets.QMessageBox #create a message box asking do you want to upload to the project
            response = q_box.question(self,'', "Would you like to upload a file to this project?", q_box.Yes | q_box.No)
            if (response == q_box.Yes): #if you want to upload, do this
                s.upload(service, project_name, project_id)

    def projView(self):
        self.ProjWin = ProjectsWindow() 
        self.ProjWin.update()#updates the window so the new projects are shown
        self.ProjWin.show() #show the window 
        self.hide() #hide current window

    def addNew(self):
        contacts = s.addContact(None, None, None) #refresh the contacts list
        name_in, ok = QInputDialog.getText(self, 'New Contact', 'Contact Name:')
        if (ok): #if okay button pressed for name
            contact_name = str(name_in) #convert to string
            email_in, ok = QInputDialog.getText(self, 'New Contact', 'Contact Email:')
            if (ok): #if okay button pressed for email
                contact_email = str(email_in) #convert to string
                s.addContact(contact_name, contact_email, contacts)
                self.ContWin = ContactsWindow()
                self.ContWin.show() #show updated version of the window
                self.hide() #hide current window

#Initilisation of the GUI
app = QApplication(sys.argv)
w = ProjectsWindow()
w.show()
sys.exit(app.exec_())
