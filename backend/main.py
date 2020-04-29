from asyncio import Queue
from typing import List, Dict, Literal, Union
from urllib.parse import urlsplit

import requests
import uvicorn
from aiocache import caches, Cache
from bs4 import BeautifulSoup, Tag
from fastapi import FastAPI, WebSocket
from fastapi.encoders import jsonable_encoder
from fastapi.responses import Response

app = FastAPI()
queue: Queue = None
caches.set_config({
    'default': {
        'cache': "aiocache.SimpleMemoryCache",
        'serializer': {
            'class': "aiocache.serializers.PickleSerializer"
        }
    }
})
cache = Cache(Cache.MEMORY)

Mutations = Union[Literal["PREVIOUS_NODE"], Literal["NEXT_NODE"], Literal["CLICK_NODE"], Literal["PUSH_ROUTE"]]

from pydantic import BaseModel


class Navigation(BaseModel):
    mutation: Mutations
    data: dict


@app.post("/navigate")
async def post(navigation: Navigation):
    resp = {
        'namespace': 'navigate',
        'action': 'onNavigate',
        'data': navigation
    }
    await queue.put(jsonable_encoder(resp))
    return Response(status_code=200)


@app.get("/note")
async def get(note: str):
    resp = {
        'namespace': 'note',
        'mutation': 'onNote',
        'data': note,
    }
    await queue.put(resp)
    return Response(status_code=200)


Songs = Dict[str, str]
Games = Dict[str, Songs]


@app.get("/pdf")
async def get(path: str):
    print(path)
    resp: requests.Response = requests.get(f'https://www.ninsheetmusic.org{path}')
    return Response(content=resp.content, media_type="application/pdf")


@app.get("/games")
async def get(url: str):
    games_cache = await cache.get(url)
    if games_cache is not None:
        return games_cache

    resp: requests.Response = requests.get(url)
    soup = BeautifulSoup(resp.text, features='lxml')
    games: Games = {}
    games_div: List[Tag] = soup.find_all('div', class_='contentBox')
    for div in games_div:
        name = div.find('h3').contents[0]
        songs: Songs = {}
        for song in div.find_all('li'):
            song_title = song.find('div', class_='tableList-cell--sheetTitle').string
            pdf_url = song.find('a', class_='tableList-buttonCell--sheetPdf').attrs['href']
            songs[song_title] = urlsplit(pdf_url)[2]

        games[name] = songs

    await cache.set(url, games)

    return games


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    global queue
    queue = Queue()
    while True:
        msg = await queue.get()
        await websocket.send_json(msg)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
