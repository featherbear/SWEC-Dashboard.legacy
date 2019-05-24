from ..connectors import Database
from ..auth import PEM, User
from tornado.escape import json_encode


class NoticeModel():
    id: int = -1

    title: str
    description: str
    author: id  # rID of User

    date: int  # actually timeContainer object
    endDate: int

    priority: int
    added: int
    approved: bool

    active: int  # is the notice active


class Notice(NoticeModel):

    def __init__(self, title, description, author, date, endDate, priority, added, approved, active):
        self.title, self.description, self.author = map(lambda o: o.decode() if type(o) == bytes else o,
                                                        [title, description, author])
        self.date = date
        self.endDate = endDate

        self.added = int(added)
        self.priority = int(priority)
        self.approved = int(approved) == 1
        self.active = int(active) == 1

    @property
    def dict(self):
        return dict(
            id=self.id,
            title=self.title,
            description=self.description,
            author=self.author,
            date=self.date,
            endDate=self.endDate,
            priority=self.priority,
            added=self.added,
            approved=self.approved,
            active=self.active
        )

    @property
    def json(self):
        return json_encode(self.dict)

    def getAuthor(self) -> User:
        return User(self.author)

    SQLCreateQuery = """CREATE TABLE IF NOT EXISTS notices (
                                            id INTEGER PRIMARY KEY AUTOINCREMENT,
    
                                            title TEXT NOT NULL,
                                            description TEXT NOT NULL,
                                            author INTEGER NOT NULL,

                                            date DATETIME NOT NULL,
                                            endDate DATETIME,
    
                                            priority INTEGER NOT NULL,
                                            added DATETIME NOT NULL,
                                            approved BOOLEAN NOT NULL, 
                                            
                                            active BOOLEAN NOT NULL,
                                                
                                            FOREIGN KEY (author) REFERENCES users (id)
                                        );"""
