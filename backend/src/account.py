from db import db

class Service: # TODO
    def __init__(self, name:str, desc:str, price:float, usr:str):
        # add to db
        # ensure the name is unique within the user
        return

    def getService(self):
        # get the service from the database
        return
    
    def updateService(self):
        # update the service in the database
        # if name is changed, ensure the new name is unique within the user
        return

    def removeService(self):
        # remove the service from the database
        return

class Review: # TODO
    def __init__(self, title:str, body:str, stars:float, usr:str):
        # add to db
        return
    
    def getReview(self):
        # get the review from the database
        return
    
    def updateReview(self):
        # update the review in the database
        return
    
    def removeReview(self):
        # remove the review from the database
        return

class Account():
    # pfp stored in ../media/<self.usr>/pfp.jpg
    # media stored in ../media/<self.usr>/media folder

    def __init__(self, usr:str, pwd:str):
        # add to db
        # ensure the username is unique
        return

    def getAccount(self) -> dict:
        # get the account info from the database
        return
    
    def updateUsername(self, newUsr:str):
        # update the username in the database
        # ensure the new username is unique
        return

    def updatePassword(self, newPwd:str):
        # update the password in the database
        return
    
    def removeAccount(self):
        # remove the account from the database
        return

    def login(usr:str, pwd:str) -> bool:
        # check if the username and password are correct
        return

    def addPhoto(self, file):
        # add/replace the file as pfp
        # completed=True in the db
        return

    def addMedia(self):
        # add/replace the media to the media folder
        return

    def removeMedia(self):
        # remove the media from the media folder
        return

