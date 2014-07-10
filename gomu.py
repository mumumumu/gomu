#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
from collections import namedtuple

import click
from gmusicapi import Mobileclient


#class Playlist(object):

    #def __init__(self, name=None, tracks=None):
        #self.name = name
        #self.tracks = tracks
Playlist = namedtuple('Playlist', 'name tracks')


class Player(object):

    def __init__(self):
        self.queue = []

    def enqueue(self, song):
        self.queue.append(song)


class GoogleMusicClient(object):

    def __init__(self, email, password, device_id):
        self.api = Mobileclient()
        self.api.login(email, password)
        self.device_id = device_id

        self.playlists = []
        self.songs = {}

        self.player = Player()

    def update_library(self):
        self.songs = {song.get('nid'): song for song in self.api.get_all_songs()}

        self.playlists = [
            Playlist(name=playlist['name'].encode('utf-8'),
                     tracks=[track['trackId'] for track in playlist['tracks']])
            for playlist in self.api.get_all_user_playlist_contents()
        ]

    def play(self, item_type, item_index):
        if item_type == 'playlist':
            click.echo('playing {} {}'.format(item_type, self.playlists[int(item_index)].name))

    def queue(self, item_type, item_index):
        if item_type == 'playlist':
            for song in self.playlists[int(item_index)]:
                self.player.enqueue(song)

    def show(self, item_type, item_index):
        if item_type == 'playlist':
            playlist = self.playlists[int(item_index)]
            click.echo('showing {} {}'.format(item_type, playlist.name))
            for song in playlist.tracks:
                click.echo(self.songs[song])
        elif item_type == 'queue':
            for song in self.player.queue:
                click.echo(song)

    def list(self, item_type):
        if item_type == 'playlist':
            for i, playlist in enumerate(self.playlists):
                click.echo("[{}]\t{} ({})".format(i, playlist.name, len(playlist.tracks)))
        elif item_type == 'songs':
            click.echo(self.songs)


@click.group(invoke_without_command=True)
@click.pass_context
@click.option('--config', '-c', default='~/.gomu', help='')
def gomu(ctx, config):
    config_data = {}
    try:
        with open(os.path.expanduser(config)) as conf_file:
            for line in conf_file.readlines():
                data = line.split('=')
                config_data[data[0]] = data[1].strip()
    except IOError:
        click.echo("Couldn't find config file ~/.gomu")
        sys.exit(1)

    ctx.obj = GoogleMusicClient(**config_data)
    click.echo("Initial library update")
    ctx.invoke(getattr(ctx.obj, 'update_library'))

    while True:
        try:
            _input = click.prompt('>', type=str)
            cmd = _input.split(' ')[0]
            args = _input.split(' ')[1:]
            #getattr(ctx.obj, cmd)(*args)
            ctx.invoke(getattr(ctx.obj, cmd), *args)
        except SystemExit as e:
            if e.code:
                break


if __name__ == '__main__':
    gomu()
