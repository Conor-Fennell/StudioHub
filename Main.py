import sys
import tkinter as tk
from tkinter import filedialog  # Using this for windows explorer popup

import PyQt5
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtGui import QCursor
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (QApplication, QCompleter, QHBoxLayout, QLabel,
                             QLineEdit, QMainWindow, QPushButton, QScrollArea,
                             QSizePolicy, QSpacerItem, QVBoxLayout, QWidget, QMessageBox
                             ,QErrorMessage, QInputDialog, QFormLayout)

import Drive as s

creds = None
service = s.GoogleAuth(creds) #authenticate user, make sure permissions are accepted
exists, folder_id = s.searchFile(service,'StudioHub') #Check if folder exists and get its id
if (exists == 0): #if we have not created a google drive StudioHub folder
    print("No folder named StudioHub existed, creating new one")
    folder_id = s.createFolder(service, 'StudioHub', None) #Get folder_id of new folder created
else: #We have already created StudioHub folder, its id is the one from searchFile function
        print("StudioHub folder already exists") 


#Main window that opens when we start the program, 
#has all the projects and contacts button, create project etc
class ProjectsWindow(QMainWindow):
    def __init__(self, *args, **kwargs):
        super().__init__()
        #Create our 4 main buttons, the add contacts button will only be visible 
        #on the contacts screen 
        self.setStyleSheet('background-color: #242424; color: white; font-size: 14pt;'
                            'font: Courier;')
        self.create = QtWidgets.QPushButton(self)
        self.create.setText("Create Project")
# padding: 6px;')
        self.create.setStyleSheet("QPushButton{background-color : darkSlateGray;}"
                                "QPushButton::pressed{background-color : #242424;}")
        self.create.setCursor(QCursor(QtCore.Qt.PointingHandCursor))
        self.create.clicked.connect(self.createProj)

        self.view = QtWidgets.QPushButton(self)
        self.view.setText("View All Projects")
        self.view.setStyleSheet("QPushButton{background-color : darkSlateGray;}"
                                "QPushButton::pressed{background-color : #242424;}") 
        self.view.setCursor(QCursor(QtCore.Qt.PointingHandCursor))
        self.view.clicked.connect(self.projView)

        self.contacts = QtWidgets.QPushButton(self)
        self.contacts.setText("Contacts")
        self.contacts.setStyleSheet("QPushButton{background-color : darkSlateGray;}"
                                "QPushButton::pressed{background-color : #242424;}") 
        self.contacts.setCursor(QCursor(QtCore.Qt.PointingHandCursor))
        self.contacts.clicked.connect(self.contactsView)

        #This button is hidden and only made visible on contacts screen
        self.NewContact = QtWidgets.QPushButton(self)
        self.NewContact.setText("Add New Contact")
        self.NewContact.clicked.connect(self.addNew)
        self.NewContact.setStyleSheet("QPushButton{background-color : darkSlateGray;}"
                                "QPushButton::pressed{background-color : #242424;}") 
        self.NewContact.setCursor(QCursor(QtCore.Qt.PointingHandCursor))
        self.NewContact.hide()

        self.controls = QWidget()  #Controls container widget.
        self.controlsLayout = QVBoxLayout()   #Controls container layout.

        # List of names, widgets are stored in a dictionary by these keys.  
        self.projWidget = []
        project_dict = s.listProjects(folder_id,service)
        #Iterating through all the projects, creating a widget 
        #for each one with their own buttons
        for name in project_dict:
            project_id = project_dict[name]
            #print("adding",name, "to widget:", project_id, "ProjectWindow")
            item = ProjectWidget(name, project_id, self) #make a project widget with the name of the current project
            self.controlsLayout.insertWidget(0,item) #^^^ we pass self so we can hide it from the widgets inside it
            self.projWidget.append(item) #append it to our list of widgets of projects

        self.contWidget = [] #empty list of contact widgets
        contacts = s.addContact(None, None, None) #get the list of contacts

        for name in contacts:
            user_email = contacts[name] #accessing email from dictionary of contacts
            item = contactsWidget(name, user_email,self) #make a project widget with the name of the current project
            #and with the list with file_id and project_id
            self.controlsLayout.insertWidget(0,item)
            self.contWidget.append(item) #append it to our list of widgets of projects

        #Hide the contacts until the contact view is opened
        for widget in self.contWidget:
            widget.hide()

        self.fileWidget = [] #declaring this for later use in viewing the files in a project

        #Hide the project view widgets until a project is clicked
        for widget in self.fileWidget:
            widget.hide()

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
        self.searchbar.setStyleSheet('background-color: white; color: black; font: Courier; padding: 6px;'
                                            'border-style: outset;'
                                            'border-width: 2px; border-radius: 6px;'
                                            'border-color: beige;')
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
        containerLayout.addWidget(self.NewContact)
        containerLayout.addWidget(self.searchbar)
        containerLayout.addWidget(self.scroll)

        container.setLayout(containerLayout)
        self.setCentralWidget(container)

        self.showMaximized()
        self.setWindowTitle('StudioHub')

        #when we initialise this is the current window
        #We will keep track of this and hide all other results outside of it
        self.currentWindow = self.projWidget
    def update_display(self, text):
        for widget in self.currentWindow:
            if text.lower() in widget.name.lower():
                widget.show()
            else:
                widget.hide()

    def createProj(self): 
        #Text input doalog window to input project name
        text, ok = QInputDialog.getText(self, 'New Project', 'Name your project:')
        if (ok): #if okay button pressed
            project_name = str(text) #project name is string of inputted text
            #calling it project id created to use it if we want to upload soemthing to it straight away
            project_id_created = s.newProject(folder_id, project_name, service) #make a new project with that name
            for widget in self.contWidget:
                widget.hide()
            for widget in self.fileWidget:
                widget.hide()
            for widget in self.projWidget:
                widget.hide()
            # List of names, widgets are stored in a dictionary by these keys.  
            self.projWidget = []
            project_dict = s.listProjects(folder_id,service)
            #Iterating through all the projects, creating a widget 
            #for each one with their own buttons
            for name in project_dict:
                project_id = project_dict[name]
                #print("adding",name, "to widget:", project_id, "ProjectWindow")
                item = ProjectWidget(name, project_id, self) #make a project widget with the name of the current project
                self.controlsLayout.insertWidget(0,item) #^^^ we pass self so we can hide it from the widgets inside it
                self.projWidget.append(item) #append it to our list of widgets of projects

            q_box = QtWidgets.QMessageBox(self) #create a message box asking do you want to upload to the project
            q_box.setStandardButtons(QtWidgets.QMessageBox.No | QtWidgets.QMessageBox.Yes)
            q_box.setWindowTitle("Upload to Project")
            q_box.setText("Would you like to upload a file to this project?")
            q_box.setStyleSheet('background-color: darkSlateGray; color: white; font: Courier')
            q_box.exec_()
            if (q_box.result() == QtWidgets.QMessageBox.Yes):
                loop = True #reacurring loop if we keep cancelling uploads and then say we want to upload
                while (loop == True):
                    file_uploaded = s.upload(service, project_name, project_id_created)
                    if(file_uploaded == None):
                        q_box = QtWidgets.QMessageBox(self) #create a message box asking do you want to upload to the project
                        q_box.setStandardButtons(QtWidgets.QMessageBox.No | QtWidgets.QMessageBox.Yes)
                        q_box.setWindowTitle("Upload to Project")
                        q_box.setText("No file was uploaded, do you want to try again?")
                        q_box.setStyleSheet('background-color: darkSlateGray; color: white; font: Courier')
                        q_box.exec_()
                        if (q_box.result() != QtWidgets.QMessageBox.Yes):
                            loop = False
                        else: #loop around again
                            loop = True
                    else: #This means we uploaded a file successfully
                        msg_box = QtWidgets.QMessageBox(self) #create a message box asking do you want to upload to the project
                        msg_box.setWindowTitle("Upload Successful")
                        msg_box.setText("File uploaded to "+project_name)
                        msg_box.setStyleSheet('background-color: darkSlateGray; color: white; font: Courier')
                        msg_box.exec_()
                        loop = False
        for widget in self.contWidget:
            widget.hide()
        for widget in self.fileWidget:
            widget.hide()
        self.currentWindow = self.projWidget
        

    def projView(self):
        for widget in self.fileWidget:#hide all file widgets
            widget.hide()
        for widget in self.contWidget: #hide all contacts widgets
            widget.hide()
        for widget in self.projWidget: #hide all project widgets
            widget.hide()
        # List of names, widgets are stored in a dictionary by these keys.  
        self.projWidget = []
        project_dict = s.listProjects(folder_id,service)
        #Iterating through all the projects, creating a widget 
        #for each one with their own buttons
        for name in project_dict:
            project_id = project_dict[name]
            #print("adding",name, "to widget:", project_id, "ProjectWindow")
            item = ProjectWidget(name, project_id, self) #make a project widget with the name of the current project
            self.controlsLayout.insertWidget(0,item) #^^^ we pass self so we can hide it from the widgets inside it
            self.projWidget.append(item) #append it to our list of widgets of projects

        self.NewContact.hide() #hide the add new contacts button
        self.contacts.show() #show the view contacts button
        self.currentWindow = self.projWidget
 
        
    def contactsView(self):
        for widget in self.projWidget:
            widget.hide() #hide all the projects widgets
        for widget in self.fileWidget:
            widget.hide() #hide all the file widgets
        for widget in self.contWidget:
            widget.hide() #show all the contacts widgets
        self.contacts.hide() #hide view contacts button
        self.NewContact.show() #show add new contacts button 
        #this will to take us to scrollable contacts view
        self.contWidget = [] #empty list of contact widgets
        contacts = s.addContact(None, None, None) #get the list of contacts
        for name in contacts:
            user_email = contacts[name] #accessing email from dictionary of contacts
            item = contactsWidget(name, user_email,self) #make a project widget with the name of the current project
            #and with the list with file_id and project_id
            self.controlsLayout.insertWidget(0,item)
            self.contWidget.append(item) #append it to our list of widgets of projects
        self.currentWindow = self.contWidget


    def addNew(self):
        contacts = s.addContact(None, None, None) #refresh the contacts list
        loop = True #loop around until they either create a new contact successfully or decide to not create one
        while loop == True:
            name_in, ok = QInputDialog.getText(self, 'New Contact', 'Contact Name:')
            if (ok): #if okay button pressed for name
                contact_name = str(name_in) #convert to string
                email_in, ok = QInputDialog.getText(self, 'New Contact', 'Contact Email:')
                contact_email = str(email_in) #convert to string
                if (ok) & (contact_name != contact_email): #if okay button pressed for email, and theyre not the same
                    s.addContact(contact_name, contact_email, contacts)
                    for widget in self.contWidget: #hide all the widgets
                        widget.hide()
                    item = contactsWidget(contact_name, contact_email,self) #make a project widget with the name of the current project
                    self.controlsLayout.insertWidget(0,item) #insert it at the top of the list
                    self.contWidget.append(item) #append it to our list of widgets of projects
                    for widget in self.contWidget: #show all widgets with new contacts appended to it
                        widget.show() #show all the contacts widgets
                    loop = False
                elif (contact_name == contact_email):
                    msg_box = QtWidgets.QMessageBox(self)
                    msg_box.setWindowTitle("New Contact Error")
                    msg_box.setText("Contact name and email address can't be the same")
                    msg_box.setStyleSheet('background-color: darkSlateGray; color: white; font: Courier')
                    msg_box.exec_() #they cant be the same, ask them to enter new details
            else: #break from loop as we chose not to add a new contact
                loop = False
        self.currentWindow = self.contWidget


class ProjectWidget(QWidget): 
    def __init__(self, name, project_id, win):
        super(ProjectWidget, self).__init__()
        self.setStyleSheet('background-color: #3A3A3A; color: white; font-size: 14pt; font: Courier')
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        #we passed in the ProjectWindow, we can hide it when we need to
        self.win = win
        self.name = name
        self.project_id = project_id
        self.proj = [self.name, self.project_id]
        self.is_on = False

        self.lbl = QLabel(self.name)
        self.lbl.setStyleSheet('background-color: #242424; color: white; font-size: 14pt;font: Courier;')

        self.btn_upload = QPushButton("Upload to Project")
        self.btn_upload.setCursor(QCursor(QtCore.Qt.PointingHandCursor))
        self.btn_upload.setStyleSheet(
                                "QPushButton{background-color : darkSlateGray;}"
                                "QPushButton::pressed{background-color : #242424;}") 

        self.btn_view = QPushButton("View Project")
        self.btn_view.setCursor(QCursor(QtCore.Qt.PointingHandCursor))
        self.btn_view.setStyleSheet(
                                "QPushButton{background-color : darkSlateGray;}"
                                "QPushButton::pressed{background-color : #242424;}") 

        self.btn_collab = QPushButton("Make Collaborative")
        self.btn_collab.setCursor(QCursor(QtCore.Qt.PointingHandCursor))
        self.btn_collab.setStyleSheet(
                                "QPushButton{background-color : darkSlateGray;}"
                                "QPushButton::pressed{background-color : #242424;}") 

        self.btn_delete = QPushButton("Delete Project")
        self.btn_delete.setCursor(QCursor(QtCore.Qt.PointingHandCursor))
        self.btn_delete.setStyleSheet(
                                "QPushButton{background-color : darkSlateGray;}"
                                "QPushButton::pressed{background-color : #242424;}") 

        self.hbox = QHBoxLayout()
        
        self.hbox.addWidget(self.lbl)
        self.hbox.addWidget(self.btn_view)
        self.hbox.addWidget(self.btn_upload)
        self.hbox.addWidget(self.btn_collab)
        self.hbox.addWidget(self.btn_delete)

        self.btn_upload.clicked.connect(self.uploadToProj)
        self.btn_view.clicked.connect(self.viewProj)
        self.btn_collab.clicked.connect(self.collaborateProj)
        self.btn_delete.clicked.connect(self.deleteProj)
        
        self.setLayout(self.hbox)

    def show(self):

        for w in [self, self.lbl, self.btn_upload, self.btn_view, self.btn_collab]:
            w.setVisible(True)

    def hide(self):

        for w in [self, self.lbl, self.btn_upload, self.btn_view, self.btn_collab]:
            w.setVisible(False)
            
    def uploadToProj(self):
        print(self.name, "id is",self.project_id)
        loop = True #reacurring loop if we keep cancelling uploads and then say we want to upload
        while (loop == True):
            file_uploaded = s.upload(service, self.name, self.project_id)
            if(file_uploaded == None):
                q_box = QtWidgets.QMessageBox(self) #create a message box asking do you want to upload to the project
                q_box.setStandardButtons(QtWidgets.QMessageBox.No | QtWidgets.QMessageBox.Yes)
                q_box.setWindowTitle("Upload to Project")
                q_box.setStyleSheet('background-color: darkSlateGray; color: white; font: Courier')
                q_box.setText("No file was uploaded, do you want to try again?")
                q_box.exec_()
                if (q_box.result() != QtWidgets.QMessageBox.Yes):
                    loop = False
            else: #This means we uploaded a file successfully
                msg_box = QtWidgets.QMessageBox(self) #create a message box asking do you want to upload to the project
                msg_box.setWindowTitle("Upload Successful")
                msg_box.setText("File uploaded to "+self.name)
                msg_box.setStyleSheet('background-color: darkSlateGray; color: white; font: Courier')
                msg_box.exec_()
                loop = False
        self.win.currentWindow = self.win.projWidget

    def viewProj(self):
        print("id is",self.project_id)
        for widget in self.win.projWidget:
            widget.hide()
        self.win.fileWidget = []
        project_dict = s.listProjects(folder_id,service)
        #print(project_dict)
        proj_id = project_dict[self.name]
        thisProj_dict = s.listProjects(proj_id,service)
        for name in thisProj_dict:
            file_id = thisProj_dict[name] #access file_id from the dictionary
            fileProj_id = [file_id, proj_id] #bundle it into list object
            #print("adding",name, "to widget:", file_id)
            item = viewWidget(name, fileProj_id) #make a project widget with the name of the current project
            #and with the list with file_id and project_id
            self.win.controlsLayout.insertWidget(0,item)
            self.win.fileWidget.append(item) #append it to our list of widgets of projects
        self.win.currentWindow = self.win.fileWidget #set it as current window to filter results in search bar

    def collaborateProj(self):
        contacts = s.addContact(None, None, None) 
        contact_selected, ok = QInputDialog.getItem(self, "Collaborate on Project","Contacts", contacts, 0, False)
        if ok and contact_selected:
            user_email = contacts[contact_selected]
            try:
                s.shareProject(service, self.project_id, user_email)
                message = "Project shared with "+contact_selected+": "+contacts[contact_selected]
                print(message)
                msg = QMessageBox()
                msg.setText(message)
                msg.setWindowTitle("Shared Project")
                msg.setIcon(QMessageBox.Information)
                msg.setStyleSheet('background-color: darkSlateGray; color: white; font: Courier')
                msg.exec_()
            except:
                message = "Unable to share project with "+(user_email)
                msg = QMessageBox()
                msg.setText(message)
                msg.setWindowTitle("Share Project Error")
                message = "Please ensure "+user_email+" is a valid email address"
                msg.setInformativeText(message)
                msg.setIcon(QMessageBox.Warning)
                msg.setStyleSheet('background-color: darkSlateGray; color: white; font: Courier')
                msg.exec_()

    def deleteProj(self):
        try:
            q_box = QtWidgets.QMessageBox(self) #create a message box asking do you want to delete the project
            q_box.setStandardButtons(QtWidgets.QMessageBox.No | QtWidgets.QMessageBox.Yes)
            q_box.setWindowTitle("Delete Project")
            q_box.setText("Are you sure you would like to delete this project?")
            q_box.setStyleSheet('background-color: darkSlateGray; color: white; font: Courier')
            q_box.setCursor(QCursor(QtCore.Qt.PointingHandCursor))
            q_box.exec_()
            if (q_box.result() == QtWidgets.QMessageBox.Yes):#if response is yes, deletes the the project
                s.delete(service, self.project_id)
                #hide the deleted widget
                self.win.currentWindow = self.win.projWidget
                self.hide()
            else:
                print("User chose not to delete", self.name)
        except: #if file doesn't exist, must already be deleted
            error_dialog = QtWidgets.QErrorMessage() #show project already deleted error msg
            error_dialog.showMessage("Project already deleted")
            error_dialog.setWindowTitle("File error")
            error_dialog.setStyleSheet('background-color: darkSlateGray; color: white; font: Courier')
            error_dialog.exec_()


#viewing the contacts widget
class contactsWidget(QWidget):
    def __init__(self, name, user_email, win):
        super(contactsWidget, self).__init__()
        self.setStyleSheet('background-color: #3A3A3A; color: white; font-size: 14pt; font: Courier')
        self.win = win
        self.user_email = user_email
        self.name = name #name of file
        self.is_on = False
        #labelling the buttons and labels
        self.lbl_name = QLabel(self.name)
        self.lbl_name.setStyleSheet('background-color: #242424; color: white; font-size: 14pt;font: Courier;')
        self.lbl_email = QLabel(self.user_email)
        self.lbl_email.setStyleSheet('background-color: #242424; color: white; font-size: 14pt;font: Courier;')
        self.btn_share = QPushButton("Add to Project")
        self.btn_share.setCursor(QCursor(QtCore.Qt.PointingHandCursor))
        self.btn_share.setStyleSheet(
                                "QPushButton{background-color : darkSlateGray;}"
                                "QPushButton::pressed{background-color : #242424;}") 
        self.btn_delete = QPushButton("Delete Contact")
        self.btn_delete.setCursor(QCursor(QtCore.Qt.PointingHandCursor))
        self.btn_delete.setStyleSheet(
                                "QPushButton{background-color : darkSlateGray;}"
                                "QPushButton::pressed{background-color : #242424;}") 

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
            
    def share(self):
        project_dict = s.listProjects(folder_id,service)
        project_name, ok = QInputDialog.getItem(self, "Collaborate","Select a project to share", project_dict, 0, False)
        if ok and project_name:
            project_id = project_dict[project_name]
            print(self.user_email)
            try:
                s.shareProject(service, project_id, self.user_email)
                message = "Project shared with "+(self.user_email)
                msg = QMessageBox()
                msg.setText(message)
                msg.setWindowTitle("Shared Project")
                msg.setStyleSheet('background-color: darkSlateGray; color: white; font: Courier')
                msg.setIcon(QMessageBox.Information)
                msg.exec_()
            except:
                message = "Unable to share project with "+(self.user_email)
                msg = QMessageBox()
                msg.setText(message)
                msg.setStyleSheet('background-color: darkSlateGray; color: white; font: Courier')
                msg.setWindowTitle("Share Project Error")
                message = "Please ensure "+self.user_email+" is a valid email address"
                msg.setInformativeText(message)
                msg.setIcon(QMessageBox.Warning)
                msg.exec_()

    def delete(self): 
        print("Deleting from contacts:", self.user_email)
        s.deleteContact(self.user_email)
        message = "Deleted "+self.user_email+" from contacts"
        msg = QMessageBox()
        msg.setText(message)
        msg.setWindowTitle("Deleted Contact")
        msg.setStyleSheet('background-color: darkSlateGray; color: white; font: Courier')
        msg.setIcon(QMessageBox.Information)
        msg.exec_()
        #self.hide()
        for widget in self.win.contWidget: #show all widgets with contact deleted from it
            widget.hide() #show all the contacts widgets
        contacts = s.addContact(None, None, None)
        self.win.contWidget = []
        #have to update the contacts widget so that when we add a new contact or delete contacts
        #old ones dont reappear
        for name in contacts:
            user_email = contacts[name] #accessing email from dictionary of contacts
            item = contactsWidget(name, user_email,self.win) #make a project widget with the name of the current project
            #and with the list with file_id and project_id
            self.win.controlsLayout.insertWidget(0,item)
            self.win.contWidget.append(item) #append it to our list of widgets of projects
        for widget in self.win.contWidget: #show all widgets with contact deleted from it
            widget.show() #show all the contacts widgets
        self.win.currentWindow = self.win.contWidget


#viewing the files inside an indiviual project
class viewWidget(QWidget):
    def __init__(self, name, fileProj_id):
        super(viewWidget, self).__init__()
        self.setStyleSheet('background-color: #3A3A3A; color: white; font-size: 14pt; font: Courier')
        self.fileProj_id = fileProj_id #file_id and project_id
        self.name = name #name of file
        self.is_on = False
        #labelling the buttons and labels
        self.lbl = QLabel(self.name)
        self.lbl.setStyleSheet('background-color: #242424; color: white; font-size: 14pt;font: Courier;')
        self.btn_download = QPushButton("Download")
        self.btn_download.setCursor(QCursor(QtCore.Qt.PointingHandCursor))
        self.btn_download.setStyleSheet(
                                "QPushButton{background-color : darkSlateGray;}"
                                "QPushButton::pressed{background-color : #242424;}") 
        self.btn_delete = QPushButton("Delete")
        self.btn_delete.setCursor(QCursor(QtCore.Qt.PointingHandCursor))
        self.btn_delete.setStyleSheet(
                                "QPushButton{background-color : darkSlateGray;}"
                                "QPushButton::pressed{background-color : #242424;}") 

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
        try:
            loop = True
            while loop == True:
                print("Downloading file with id:",self.fileProj_id[0])
                success = s.download(self.fileProj_id[0], service) #download the file from the drive
                if success:
                    return loop == False
                else:
                    q_box = QtWidgets.QMessageBox(self) #create a message box asking do you want to delete file
                    q_box.setStandardButtons(QtWidgets.QMessageBox.No | QtWidgets.QMessageBox.Yes)
                    q_box.setWindowTitle("Download Failed")
                    q_box.setText("Would you like to try and download the file again?")
                    q_box.setStyleSheet('background-color: darkSlateGray; color: white; font: Courier')
                    q_box.exec_()
                    if (q_box.result() != QtWidgets.QMessageBox.Yes):#if response is not yes, breaks the loop
                        cancel_dialog = QtWidgets.QMessageBox() #let user know they cancelled the download
                        cancel_dialog.setText("The file was not downloaded")
                        cancel_dialog.setWindowTitle("Download Cancelled")
                        cancel_dialog.setStyleSheet('background-color: darkSlateGray; color: white; font: Courier')
                        cancel_dialog.exec_() #show the message box
                        return loop == False #breaks loop
        except:
            cancel_dialog = QtWidgets.QMessageBox() #let user know they cancelled the download
            cancel_dialog.setText("The file was not downloaded")
            cancel_dialog.setWindowTitle("Download Cancelled")
            cancel_dialog.setStyleSheet('background-color: darkSlateGray; color: white; font: Courier')
            cancel_dialog.exec_() #show the message box
         


    def delete(self, fileProj_id): 
        try:
            q_box = QtWidgets.QMessageBox(self) #create a message box asking do you want to delete file
            q_box.setStandardButtons(QtWidgets.QMessageBox.No | QtWidgets.QMessageBox.Yes)
            q_box.setWindowTitle("Delete File")
            q_box.setText("Are you sure you would like to delete this file?")
            q_box.setStyleSheet('background-color: darkSlateGray; color: white; font: Courier')
            q_box.exec_()
            if (q_box.result() == QtWidgets.QMessageBox.Yes):#if response is yes, deletes the file
                s.delete(service, self.fileProj_id[0])
                #hide the deleted widget
                self.hide()
            else:
                print("User chose not to delete", self.name)
        except: #if file doesn't exist, must already be deleted
            error_dialog = QtWidgets.QErrorMessage() #show file already deleted error msg
            error_dialog.showMessage("File already deleted")
            error_dialog.setWindowTitle("File error")
            error_dialog.setStyleSheet('background-color: darkSlateGray; color: white; font: Courier')
            error_dialog.exec_()

#Initilisation of the GUI
app = QApplication(sys.argv)
w = ProjectsWindow()
w.show()
sys.exit(app.exec_())
