from pathlib import Path

from sqlalchemy import func

from .schema import (
    SongBmsRelation,
    FolderSongRelation,
    Bms, Song, Folder
)

from .utils import (
    session_scope, set_sqlite3_file_path, create_table, check_tables,
)

from .exc import DuplicateKeyError


def _format_bms(bms:Bms) -> dict :
    return {
        "id": bms.id,
        "type": bms.type,
        "file_path": str(Path(bms.file_path)),
        "PLAYER": bms.PLAYER,
        "TITLE": bms.TITLE,
        "ARTIST": bms.ARTIST,
        "GENRE": bms.GENRE,
        "PLAYLEVEL": bms.PLAYLEVEL,
        "RANK": bms.RANK,
        "TOTAL": bms.TOTAL,
        "DIFFICULTY": bms.DIFFICULTY,
        "BPM": bms.BPM,
        "PREVIEW": bms.PREVIEW,
        "MIN_BPM": bms.MIN_BPM,
        "MAX_BPM": bms.MAX_BPM,
    }


def _format_song(song:Song) -> dict :
    return {
        "id": song.id,
        "name": song.name,
        "dir_path": str(Path(song.dir_path)),
    }


def _format_folder(folder:Folder) -> dict :
    return {
        "id": folder.id,
        "name": folder.name,
        "desc": folder.desc,
        "info": folder.info,
    }


def search_bms_list(
        filter_title=None, filter_artist=None, filter_genre=None,
        page=1, page_size=50):
    """query bms table with paging"""
    result = {
        "total": 0,
        "data": [],
    }
    with session_scope() as session:
        query = session.query(Bms)
        if filter_title:
            query = query.filter(Bms.TITLE.like(f"%{filter_title}%"))
        if filter_artist:
            query = query.filter(Bms.ARTIST.like(f"%{filter_artist}%"))
        if filter_genre:
            query = query.filter(Bms.GENRE.like(f"%{filter_genre}%"))
        result["total"] = query.count()
        query = query.limit(page_size).offset((page-1)*page_size)
        for item in query:
            result["data"].append(_format_bms(item))

    return result


def search_song_list(filter_name=None, page=1, page_size=50):
    """query song table with paging"""
    result = {
        "total": 0,
        "data": [],
    }
    with session_scope() as session:
        query = session.query(Song)
        if filter_name:
            query = query.filter(Song.title.like(f"%{filter_name}%"))
        result["total"] = query.count()
        query = query.limit(page_size).offset((page-1)*page_size)
        for item in query:
            result["data"].append(_format_song(item))

    return result


def search_folder_list(filter_name=None, page=1, page_size=50):
    """query folder table with paging"""
    result = {
        "total": 0,
        "data": [],
    }
    with session_scope() as session:
        query = session.query(Folder)
        if filter_name:
            query = query.filter(Folder.name.like(f"%{filter_name}%"))
        result["total"] = query.count()
        query = query.limit(page_size).offset((page-1)*page_size)
        for item in query:
            result["data"].append(_format_folder(item))

    return result


def add_bms(file_path:Path, bms_info:dict, on_error_raise_exc=True) -> Bms :
    bms = Bms(
        type=1,
        file_path=file_path.as_posix(),
        PLAYER=bms_info.get("PLAYER"),
        TITLE=bms_info.get("TITLE"),
        ARTIST=bms_info.get("ARTIST"),
        GENRE=bms_info.get("GENRE"),
        PLAYLEVEL=bms_info.get("PLAYLEVEL"),
        RANK=bms_info.get("RANK"),
        TOTAL=bms_info.get("TOTAL"),
        DIFFICULTY=bms_info.get("DIFFICULTY"),
        BPM=bms_info.get("BPM"),
        PREVIEW=bms_info.get("PREVIEW"),
        MIN_BPM=bms_info.get("MIN_BPM"),
        MAX_BPM=bms_info.get("MAX_BPM"),
    )
    with session_scope() as session:
        query_result = session.query(Bms).filter(
            Bms.file_path == file_path.as_posix()
        ).first()
        if query_result:
            if on_error_raise_exc:
                raise DuplicateKeyError(query_result.id)
            return query_result

        session.add(bms)
    return bms


def add_song(name:str, dir_path:Path, on_error_raise_exc=True) -> Song :
    song = Song(
        name=name,
        dir_path=dir_path.as_posix(),
    )
    with session_scope() as session:
        query_result = session.query(Song).filter(
            Song.name == name
        ).first()
        if query_result:
            if on_error_raise_exc:
                raise DuplicateKeyError(query_result.id)
            return query_result

        session.add(song)
    return song


def add_song_bms_relation(song_obj:Song, bms_obj:Bms):
    with session_scope() as session:
        song_obj = session.merge(song_obj)
        bms_obj = session.merge(bms_obj)
        if song_obj and bms_obj:
            if bms_obj not in song_obj.bmses:
                song_obj.bmses.append(bms_obj)


def add_folder_song_relation(folder_obj:Folder, song_obj:Song):
    with session_scope() as session:
        folder_obj = session.merge(folder_obj)
        song_obj = session.merge(song_obj)
        if folder_obj and song_obj:
            if song_obj not in folder_obj.songs:
                folder_obj.songs.append(song_obj)


def add_folder(name:str, desc:str, info:str) -> Folder :
    folder = Folder(
        name=name,
        desc=desc,
        info=info,
    )
    with session_scope() as session:
        query_result = session.query(Folder).filter(
            Folder.name == name
        ).first()
        if query_result:
            raise DuplicateKeyError(query_result.id)

        session.add(folder)
    return folder


def prepare_sqlite3_db(file_path:Path) -> None :
    print(f"prepare sqlite3 db: {file_path}")
    set_sqlite3_file_path(file_path)
    if file_path.exists():
        check_tables()
    else:
        create_table()
