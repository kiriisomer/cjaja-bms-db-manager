from enum import unique
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import relationship
from sqlalchemy import (
    Column, Index, ForeignKey,
    Integer, Float, String, Date, DateTime, text
)

Base = declarative_base()


class STATUS_MAP:
    NORMAL = 1
    HIDE = 2


class SongBmsRelation(Base):
    __tablename__ = 'song_bms_relation'
    song_id = Column(Integer, ForeignKey("song.id"), primary_key=True)
    bms_id = Column(Integer, ForeignKey("bms.id"), primary_key=True)


class FolderSongRelation(Base):
    __tablename__ = 'folder_song_relation'
    folder_id = Column(Integer, ForeignKey("folder.id"), primary_key=True)
    song_id = Column(Integer, ForeignKey("song.id"), primary_key=True)


class Bms(Base):
    """bms file record"""
    __tablename__ = 'bms'
    id = Column(Integer, autoincrement=True, primary_key=True)
    type = Column(Integer, server_default="1")
    status = Column(Integer, server_default="1")
    file_path = Column(String(512), nullable=False)
    add_time = Column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    # below column are infomations in bms file metadata.
    PLAYER = Column(String(32), nullable=False)
    TITLE = Column(String(128), nullable=False)
    ARTIST = Column(String(128), nullable=False)
    GENRE = Column(String(128), nullable=False)
    PLAYLEVEL = Column(Integer, nullable=False)
    RANK = Column(String(32), nullable=False)
    TOTAL = Column(String(32), nullable=False)
    DIFFICULTY = Column(String, nullable=False)
    BPM = Column(Float(precision=2), nullable=False)
    PREVIEW = Column(String(256), nullable=False)
    MIN_BPM = Column(Float(precision=2), nullable=True)
    MAX_BPM = Column(Float(precision=2), nullable=True)
    song = relationship("Song", secondary="song_bms_relation", back_populates="bmses")

class Song(Base):
    """Song include one or more bms"""
    __tablename__ = 'song'
    id = Column(Integer, autoincrement=True, primary_key=True)
    type = Column(Integer, server_default="1")
    status = Column(Integer, server_default="1")
    name = Column(String(128), nullable=False)
    dir_path = Column(String(512), nullable=False)
    folder = relationship("Folder", secondary="folder_song_relation", back_populates="song")
    bmses = relationship("Bms", secondary="song_bms_relation", back_populates="song")


class Folder(Base):
    """folder store a series of songs"""
    __tablename__ = 'folder'
    id = Column(Integer, autoincrement=True, primary_key=True)
    type = Column(Integer, server_default="1")
    status = Column(Integer, server_default="1")
    name = Column(String(128), nullable=False, unique=True)
    desc = Column(String(4096), nullable=True, server_default="")
    info = Column(String(4096), nullable=True, server_default="")
    song = relationship("Song", secondary="folder_song_relation", back_populates="folder")
