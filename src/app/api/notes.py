from typing import List

from fastapi import APIRouter, HTTPException, Path

from app.models.notes import NoteDB, NoteSchema
from app.db import notes, database

router = APIRouter()


async def post_note(payload: NoteSchema):
    query = notes.insert().values(title=payload.title, description=payload.description)
    return await database.execute(query=query)


async def get_note(id: int):
    query = notes.select().where(id == notes.c.id)
    return await database.fetch_one(query=query)


async def get_all_notes():
    query = notes.select()
    return await database.fetch_all(query=query)


async def delete_note(id: int):
    query = notes.delete().where(id == notes.c.id)
    return await database.execute(query=query)


@router.get("/", response_model=List[NoteDB])
async def read_all_notes():
    return await get_all_notes()


@router.post("/", response_model=NoteDB, status_code=201)
async def create_note(payload: NoteSchema):
    note_id = await post_note(payload)

    response_object = {
        "id": note_id,
        "title": payload.title,
        "description": payload.description,
    }
    return response_object


@router.get("/{id}/", response_model=NoteDB)
async def read_note(id: int = Path(..., gt=0), ):
    note = await get_note(id)
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    return note


async def put_note(id: int, payload: NoteSchema):
    query = (
        notes
        .update()
        .where(id == notes.c.id)
        .values(title=payload.title, description=payload.description)
        .returning(notes.c.id)
    )
    return await database.execute(query=query)


@router.put("/{id}/", response_model=NoteDB)
async def update_note(payload: NoteSchema, id: int = Path(..., gt=0)):
    note = await get_note(id)
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")

    note_id = await put_note(id, payload)

    response_object = {
        "id": note_id,
        "title": payload.title,
        "description": payload.description,
    }
    return response_object


@router.delete("/{id}/", response_model=NoteDB)
async def delete_note(id: int = Path(..., gt=0)):
    note = await get_note(id)
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")

    await delete_note(id)

    return note
