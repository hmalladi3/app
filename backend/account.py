class Service:
    def __init__(self, name:str, desc:str, price:float):
        self.name = name
        self.desc = desc
        self.price = price

class Review:
    def __init__(self, title:str, body:str, stars:float, usr:str):
        self.title = title
        self.body = body
        self.stars = stars
        self.usr = usr

class Account():
    # pic:str # profile pic
    isComplete:bool = False
    isVerified:bool = False

    def __init__(self, usr:str, pwd:str):
        self.usr: str = usr # a unique identifier used to query the db
        self.pwd: str = pwd

    def login(usr:str, pwd:str):
        return

    def addPhoto(self, file):
        # if photo exists replace it
        # else add the file as pfp
        self.isComplete = True

    def addService(self):
        # create the service
        # add to db
        return

    def removeService(self):
        # remove the service from the database
        return

    def addReview(self):
        # add the review to the database
        return

    def removeReview(self):
        # remove the review from the database
        return

    def addMedia(self):
        # add the media to the database
        return

    def removeMedia(self):
        # remove the media from the database
        return

