import os
import sys
import atexit
import re
import threading 
from subprocess import PIPE,Popen,check_output
from time import time,sleep
from glob import glob
from functools import wraps
from .baseplayer import BasePlayer 

try:
    import eyed3
except:
    #dummy class
    class eyed3():
        pass


class AndroidError(Exception):
    pass


TMP_FILE = '/sdcard/.pydatpiff_tmp'
class Android(BasePlayer):
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        self.song = self.TMP_FILE
        self.state['pause'] = False

    def _am_start(path):
        """ Sets  android java  am-start command  from android sdk"""
        path = path[1:] if path.startswith('/') else path
        start = "am start --user 0 -a android.intent.action.VIEW "
        return  start +"-d file:///%s -t audio/mp3"%path


    def setTrack(name,song):
        if name and song:
            self.is_track_set = True
        else:
            print('No media to play')
            
    def __len__(self):
        return len(self.content)

    def _threader(f):
        @wraps(f)
        def inner(self,*a,**kw):
            t = threading.Thread(target=f,args=(self,))
            t.daemon = True
            t.start()
            return t
        return inner


    def _is_playing(boolean=False):
        """ Return whether a song is being played or paused.
            
            variable state - belongs to BasePlayer
        """
        self.state = dict(playing=bool(boolean),pause=not bool(boolean))



    @property
    def track_size(self):
        return self.eyed3.info.time_secs 


    def _format_time(self,pos=None):
        """Fomrat current song time to clock format """
        pos = self.track_size  if not pos else pos
        mins = int(pos/60)
        secs = int(pos%60)
        return  mins,secs


    @property
    def artist(self):
        """ Artist name"""
        if hasattr(self,"_artist"):
            return self._artist
        
    @artist.setter
    def artist(self,name):
        self._artist = name


    @property
    def album(self):
        """ Album name"""
        if self.tag:
            return self.eyed3.tag.album

    @property
    def title(self):
        """ Song name"""
        return self._title


    @title.setter
    def title(self,name):
        self._title = name


    @staticmethod
    def _splitSong(song,keep=1):
        """Parse song and split by '-' """
        #TODO: remove or refactor this for baseclass
        if "-" in song:
            return song.split("-")[keep]
        return song
        

    def _setTrackInfo(self):
        """Set the artist name  and title of the song"""
        #::TODO refactor this for baseclass
        try:
            song = self.songs[self._index]
            title = re.sub(".mp3","",os.path.basename(song))
            self.artist = self._splitSong(title,0)
            self.title = self._splitSong(title,-1)
        except:
            tag = self.eyed3.tag.title 
            self.artist = self.eyed3.tag.artist
            self.title = self._splitSong(self.eyed3.tag.title,1)


    def _fileCheck(self,path):
        """ 
        Check if file path exists 
        @params:: path - path of song 
        """
        if os.path.isfile(self.song):
            os.remove(self.song)
        if not os.path.isfile(path):
            msg = "Song --> '%s' was  not founded"%path
            raise PlayerError(msg)


    def _load(self,file):
        """
        Open file path  and return its content
        @params:: file - path of the song
        """
        self.state['pause'] = False
        self.eyed3 = eyed3.load(file)
        self.tag = self.eyed3.tag
        f = open(file,'rb')
        self.content = f.read()
        f.close()


    @property
    def __bytes_elaspe(self):
        """Current bytes of the current song"""
        return self.__bytes_per_sec * self.__position

    @property
    def __position(self):
        """Current position of track in seconds"""
        if hasattr(self,'_start_time'):
            return int(time() - self._start_time)
        return 1

    @__position.setter
    def __position(self,spot):
        self._start_time = time()-spot


    @property
    def __bytes_per_sec(self):
        """song bytes per seconds"""
        return len(self) / self.eyed3.info.time_secs


    def __setContent(self,length):
        """Write media content to file"""
        br = self.__bytes_per_sec
        length = int(br* int(self.__position + length))
        if os.path.isfile(self.song):
            os.remove(self.song)
        with open(self.song,'wb') as _tmp:
            _tmp.write(self.content[length:])
        return length


    def play(self,song=None ,pos=1):
        """
        Play media songs

        @params:: song - song  play 
                    type:: int - index of songs  (see Android.songs)
                           str - path of the song to play 
                  pos   - play a song at the given postion (seconds)
        """
        self._fileCheck(self.song)
        self._start_time = time()
        self._load(self.song)

        if self.state['pause']: # detect if player is paused
            # Set the pause position to the current position
            pos = self._paused_pos
        
        self.__setContent(pos)
        self._player = Popen(self._command,shell=True,stdin=PIPE,
                    stdout=PIPE,stderr=PIPE)

        self._is_playing(True)
  

    def volume(self,vol=None):
        """
        Android volume controls
        @params:: vol - set the media volume range 0 - 100 
        """
        os.system('termux-volume music %s'% vol)

   
    @property
    def pause(self):
        """Pause song"""
        # capture the position the media player was pause
        if not self.state['pause']:
            self.stop
            print("Pause")
            self._paused_pos = self.__position
            self._is_playing(False)

        else: # unpause
            self.__position = self._paused_pos
            print("Unpause")
            self.play()
            # Not here play() will handle self._is_playing(True) 


    def _seeker(self,pos=5, rew=True):
        """Control fast forward and rewind function"""
        spot = pos
        if self.state['pause']:
            self.__position = self._paused_pos
            self.state['pause'] = False

        self._start_time+=spot
        self.play(pos=pos)


    def rewind(self,pos=5):
        self._seeker(pos,True)
        

    def ffwd(self,pos=5):
        self._seeker(-pos,False)

    @property
    def stop(self):
        service = "am stopservice "
        cmd = service + "org.videolan.vlc/org.videolan.vlc.PlaybackService"
        results = Popen(cmd,shell=True,stdout=PIPE,stderr=PIPE)


@atexit.register
def remove_file():
    removed = not os.system('rm /sdcard/piper.mp3')
    msg = 'Removed' if removed else "False"
    print(msg)
