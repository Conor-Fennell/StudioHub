# StudioHub

File sharing desktop application built using Python and Google Drive API V3. It allows users to upload and download files to their google drive. It also compresses files before uploading and decompresses files upon downloading to save disc space. Users are able to add contacts to their contacts list and share drive files with those contacts.

## Getting Started

All files must be placed in the same folder/directory. Running Main.py will open the User interface and run the application. This aplication is known to work in visual studio code on WIndows 10 and Linux using python 3.8. The file can be run using the terminal command: "python3 ./Main.py".

### Installations needed

You will need a version of python 3.x installed on your device. The project was built using python 3.8. This would be the recommended version for using this application.
A number of 3rd party python modules are needed. These include PyQt5, googleapiclient, google_auth_oauthlib, shuthil, and pickle. All modules are imported at the top of the files so you can see which ones you need if you are unsure. The google drive api documentation contains information about how to get the google api modules: 
https://developers.google.com/drive/api/v3/quickstart/python


### Running the Application

Once you have the relevent modules installed and you have downloaded the files into the same directory. You can run the application using the terminal command: "python3 ./Main.py". 

The GUI for this application should open. A browser window will open prompting you to allow StudioHub permission to access your google drive. Once you click accept you will be able to upload files to your google drive, add contacts, share those files with those contacts, and download files from your drive.


## Authors

* **Conor Fennell** - [StudioHub](https://github.com/Conor-Fennell/StudioHub/)




