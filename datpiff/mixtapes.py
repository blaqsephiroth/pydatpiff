import re
from functools import wraps
from .urls import Urls
from .utils.request import Session
from .errors import MixtapesError
<<<<<<< HEAD:datpiff/mixtapes.py
=======
from .frontend.display import Print,Verbose
from .backend.config import User,Datatype
from .backend.mixsetup import Pages
from .backend.webhandler import Html

>>>>>>> eca77c0... Refactor code, Change files name and method names in backup folder, Optimized speed of media.findSong function:pydatpiff/mixtapes.py

class Mixtapes(object):
    def __new__(cls, *args, **kwargs):
        cls._category = Urls.category
        return super(Mixtapes, cls).__new__(cls)


    def __init__(self, category=None,search=None,*args,**kwargs):
        '''
        Mixtapes Initialize 

        @@params: category:  -- see Mixtapes.category
        '''
        super(Mixtapes,self).__init__(*args,**kwargs)
        self._session = Session()
        self._Start(category,search)
        self._setup()

    def __str__(self):
        category = "'new','hot','top','celebrated'"
        return "%s(category)  argument: category --> %s"%(self.__class__.__name__, category)


    def __repr__(self):
        return "%s('hot')"%self.__class__.__name__

    def __len__(self):
        if hasattr(self,'_artists'):
            return len(self._artists)
        else:
            return 0

    def search(self,artist):
        """search for an artist mixtapes."""
        artist = str(artist).strip()
        if not artist: 
            return 

        Verbose('\nSearching for %s mixtapes ...'%artist)
        url = Urls.url['search']
        return  self._session.method('POST',url,data=Urls.payload(artist))


    def _Start(self,category='hot', search=None):
        '''
        Starts the web page from category selected by user
        (see Mixtapes.__init__)
        '''
        # return the url page request by user
        if search:
            body = self.search(search)
<<<<<<< HEAD:datpiff/mixtapes.py
            if not body or body is None: 
                 # if the search requests fails then get default page 
                # discard search then we recalls the _Start 
=======
            if not body or body is None: # on failure return response from a category 
>>>>>>> 9677925... implemented method for more mixtapes, Added backend/mixsetup.py:pydatpiff/mixtapes.py
                return self._Start('hot')
<<<<<<< HEAD:datpiff/mixtapes.py
        else:
            _filter = self._parseCategory 
            category_url = self._category.get(_filter(category))
            if not category_url: # user mistake, then correct it
                category_url = self._category.get('hot')

            body = self._session.method('GET',category_url)
=======
        else: # Select from category instead of searching 
            select = User.choice_is_str
            choice = select(category,self._category) or select('hot',self._category)
            body = self._session.method('GET',choice)
>>>>>>> eca77c0... Refactor code, Change files name and method names in backup folder, Optimized speed of media.findSong function:pydatpiff/mixtapes.py
        self._responses = body
        return body


   
    def _setup(self):
        """Initial variable and set attributes on page load up."""
        # all method below are property setter method 
        # each "re string" get pass to the corresponding html response text

        self.artists = '<div class\="artist">(.*[.\w\s]*)</div>'
        self.mixtapes  = '"\stitle\="listen to ([^"]*)">[\r\n\t\s]?.*img'
        self.links   = 'title"><a href\=\"(.*[\w\s]*\.html)"'
        self.views   = '<div class\="text">Listens: <span>([\d,]*)</span>'
<<<<<<< HEAD:datpiff/mixtapes.py

    def _parseCategory(self,index):
        """Helper function for selecting a category on startup
        @@params: index - category to search for. 
                (See --> "Mixtapes.category" for all category)
        """
        chosen = list(filter(lambda x: str(index) in x,self._category))
        if chosen:
            return min(chosen)
=======
        Verbose('Found %s Mixtapes'%len(self))
>>>>>>> eca77c0... Refactor code, Change files name and method names in backup folder, Optimized speed of media.findSong function:pydatpiff/mixtapes.py


    @property
    def category(self):
        """All category of Mixtapes that users can choose from."""
        print("\n--- AVAILABLE CATEGORY ---")
        for key, val in self._category.items():
            print("%s" % (key))



    def _searchTree(f):
        '''
        Wrapper function that parse and filter all requests response content.
        After parsing and filtering the responses text, it then creates a 
        dunder variable from the parent function name. 
        
        @@params: f  (wrapper function) 
         #----------------------------------------------------------
         example: "function()" will create an attribute "_function"
         #----------------------------------------------------------
        '''
        @wraps(f) 
        def inner(self, *args,**kwargs):
            response_text  = self._responses.text
            name = f.__name__
            path = f(self,*args,**kwargs)
            pattern = re.compile(path)
<<<<<<< HEAD:datpiff/mixtapes.py
<<<<<<< HEAD:datpiff/mixtapes.py
            data = list( re.sub('amp;','',pat.group(1))\
=======
            data = list(Html.remove_ampersands(pat.group(1))[0]\
>>>>>>> eca77c0... Refactor code, Change files name and method names in backup folder, Optimized speed of media.findSong function:pydatpiff/mixtapes.py
                    for pat in pattern.finditer(response_text)\
                    if pat is not None)

=======
            data = Pages(response_text).getReData(pattern)
>>>>>>> 9677925... implemented method for more mixtapes, Added backend/mixsetup.py:pydatpiff/mixtapes.py
            if hasattr(self,'_artists'):
                # we map all attributes length to _artists length 
                data = data[:len(self._artists)]
            dunder = '_' + name
            setattr(self,dunder,data)
            return data
        return inner


    @property
    def artists(self):
        ''' return all Mixtapes artists name'''
        if hasattr(self,'_artists'):
            return self._artists

    @artists.setter
    @_searchTree
    def artists(self,path):
        return path


    @property
    def mixtapes(self):
        if hasattr(self,'_mixtapes'):
            return self._mixtapes

    @mixtapes.setter 
    @_searchTree
    def mixtapes(self,path):
        ''' return all the mixtapes titles from web page'''
        return path

    @property
    def links(self):
        """Return all of the Mixtapes url links"""
        if hasattr(self,'_links'):
            return self._links

    @links.setter
    @_searchTree
    def links(self,path):
        ''' return all the album links from web page'''
        return path
    

    @property
    def views(self):
        """Return the view count of each mixtapes"""
        if hasattr(self,'_views'):
            return self._views

    @views.setter
    @_searchTree
    def views(self,path):
        return path

    @property
    def display(self):
        ''' Prettify all Mixtapes information  
            and display it to screen 
        '''
        links = self._links
        data = zip(self._artists, self._mixtapes, links, self._views)
        for count,(a, t, l, v) in list(enumerate(data,start=1)):
<<<<<<< HEAD:datpiff/mixtapes.py
            display = print
            display("# %s\nArtist: %s\nAlbum: %s\nLinks: %s\nViews: %s\n%s"
=======
            Print("# %s\nArtist: %s\nAlbum: %s\nLinks: %s\nViews: %s\n%s"
>>>>>>> eca77c0... Refactor code, Change files name and method names in backup folder, Optimized speed of media.findSong function:pydatpiff/mixtapes.py
                    % (count, a, t, l[1:], v, "-"*40))


    def _select(self,select):
        '''
        User select function that queue an ablum to the media player
        
        @@params:: select - (int) user selection by indexing an artist name or album name
                            (str)
        '''
        try:
<<<<<<< HEAD:datpiff/mixtapes.py
            combine = list(zip(self.artists,self.mixtapes))
            mixtapes  = dict(enumerate(combine,start=1))

            # checking from index 
            if isinstance(select,int):
                select-=1
                length = len(self.artists) + 1
                # catch index errors if user choose a mixtape out of range
                select = 0 if (0 >= select or select > len(self)) else select
                return self._links[select],select

            #checking from words
            select = str(select).lower().strip()
            choice = list(filter(lambda x: select in x[1][0].lower()
                                or select in x[1][1].lower(),(mixtapes.items())
                             ))
            if choice:
                index = (min(choice)[0]) - 1
                return self._links[index],index
        except MixtapesError as e:
=======
            # Return the user select by either integer or str
            # we map the integer to artists and str to mixtapes 
            return User.selection(select,self.artists,self.mixtapes)

        except MixtapesError as e:
            Print(e)
>>>>>>> eca77c0... Refactor code, Change files name and method names in backup folder, Optimized speed of media.findSong function:pydatpiff/mixtapes.py
            raise MixtapesError(1)

