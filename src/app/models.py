from sqlalchemy import Boolean, Column, String
from database.db import Base, session_factory, engine

class Game(Base):
    __tablename__ = "games"

    game_id = Column(String, nullable=False, primary_key=True)
    finished = Column(Boolean, default=False, nullable=False)

    def __init__(self, game_id, finished=False):
        self.game_id = game_id
        self.finished = finished

    @classmethod
    def createOrUpdate(cls, game_id, finished=False):
        game = cls(game_id, finished)

        session = session_factory()
        session.merge(game)
        session.commit()
        session.close()

        return game

Base.metadata.create_all(engine)
