from __future__ import print_function

import numpy as np

import os 

from .errors import FireflyError,FireflyWarning,warnings
from .json_utils import write_to_json,load_from_json

class Settings(object):
    """
    This is a class for organizing the various settings you can pass to 
    Firefly to customize how the app is initialized and what features 
    the user has access to. It is easiest to use when instances of 
    Settings are passed to a Reader instance when it is initialized.
    """
    def __getitem__(self,key):
        """
        Implementation of builtin function  __getitem__ 
        """
        attr = self.findWhichSettingsDict(key)
        return getattr(self,attr)[key]
        
    def __setitem__(self,key,value):
        """
        Implementation of builtin function __setitem__ 
        """
        attr = self.findWhichSettingsDict(key)
        ## set that dictonary's value
        getattr(self,attr)[key]=value

    def findWhichSettingsDict(self,key):
        """
        Find which sub-dictionary a key belongs to
        """
        for attr in self.__dict__.keys():
            if '_settings' in attr:
                if key in getattr(self,attr).keys():
                    return attr
        raise KeyError("Invalid option key %s"%key)
        
    def listKeys(self,values=True):
        """ 
        Pretty-prints the settings according to sub-dictionary.
        Input:  
            values=True - flag to print what the settings are set to, in addition to the key
        """
        for attr in self.__dict__.keys():
            if '_settings' in attr:
                print('--',attr,'--')
                if values:
                    for key in list(getattr(self,attr).keys()):
                        print(key,self[key],)
                else:
                    print(list(getattr(self,attr).keys()))

    def keys(self):
        """ 
        Returns a list of keys for all the different settings sub-dictionaries
        """
        this_keys = [] 
        for attr in self.__dict__.keys():
            if '_settings' in attr:
                this_keys += list(getattr(self,attr).keys())
        return this_keys

    def __init__(self,
        settings_filename = 'Settings.json',
        **kwargs):
        """
        Input:
            settings_filename='Settings.json' - what to call the settings file if you output it
                to json
            **kwargs - settings keyword arguments, should be among: 
                'stereoSep','stereo','camera','center','maxVrange','startFly','decimate','friction',
                'cameraRotation','filterVals','filterLims','colormapVals','colormapLims',
                'UIsnapshot','UIfullscreen','UI','UIloadNewData',
                'UIcameraControls','UIsavePreset','UIreset','UIdecimation','UIcolorPicker','UIdropdown',
                'UIparticle','loaded','title','showVel','sizeMult','color','showParts','plotNmax','velType'
        """

        ## where should this be saved if it's outputToJSON
        self.settings_filename = settings_filename

        self.window_settings = {
            'title':'Firefly', #set the title of the webpage
            ########################
            #this should not be modified
            'loaded':True, #used in the web app to check if the settings have been read in
            'annotation':None # adds some text at the very top
        }

        ## flags for enabling different elements of the UI
        self.UI_settings = {
            ########################
            #these settings are to turn on/off different bits of the user interface
            'UI':True, #do you want to show the UI?
            'UIfullscreen':True, #do you want to show the fullscreen button?
            'UIsnapshot':True, #do you want to show the snapshot button?
            'UIreset':True, #do you want to show the reset button?
            'UIsavePreset':True, #do you want to show the save preset button?
            'UIloadNewData':True, #do you want to show the load new data button?
            'UIcameraControls':True, #do you want to show the camera controls
            'UIdecimation':True, #do you want to show the decimation slider
            ########################
        }

        ## flags that control how the UI for each particle group looks like
        self.particle_UI_settings = {
            'UIparticle':dict(), #do you want to show the particles 
            #    in the user interface (default = True). This is a dict 
            #    with keys of the particle swapnames (as defined in self.names),
            #     and is boolean.
            'UIdropdown':dict(), #do you want to enable the dropdown menus for 
            #    particles in the user interface (default = True).This is a 
            #    dict with keys of the particle UInames, 
            #    and is boolean.
            'UIcolorPicker':dict(), #do you want to allow the user to change 
            #    the color (default = True).This is a dict with keys of the 
            #    particle UInames, and is boolean.
        }
            
        ## settings that will define the initial camera view
        self.startup_settings = {
            #these settings affect how the data are displayed
            'center':np.zeros(3), #do you want to define the initial camera center 
            #    (if not, the WebGL app will calculate the center as the mean 
            #    of the coordinates of the first particle set loaded in) 
            #    (should be an np.array of length 3: x,y,z)
            'camera':None, #initial camera location, NOTE: the magnitude must 
            #    be >0 (should be an np.array of length 3: x,y,z)
            'cameraRotation':None, #can set camera rotation if you want 
            #    (should be an np.array of length 3: xrot, yrot, zrot, in radians)
            'maxVrange':2000., #maximum range in velocities to use in deciding 
            #    the length of the velocity vectors (making maxVrange 
            #    larger will enhance the difference between small and large velocities)
            'startFly':False, #start in Fly controls? (if False, then 
            #    start in the default Trackball controls)
            'friction':None, #set the initial friction for the controls (default is 0.1)
            'stereo':False, #start in stereo mode?
            'stereoSep':None, #camera (eye) separation in the stereo 
            #    mode (default is 0.06, should be < 1)
            'decimate':None, #set the initial decimation (e.g, 
            #    you could load in all the data by setting self.decimate to 
            #    1 above, but only display some fraction by setting 
            #    self.settings.decimate > 1 here).  This is a single value (not a dict)
        }
        
        ## settings that will define the initial values of the particle UI panes
        self.particle_startup_settings = {
            'plotNmax':dict(), #maximum initial number of particles to plot 
            #    (can be used to decimate on a per particle basis).  This is 
            #    a dict with keys of the particle swapnames (as defined in self.names)
            'showVel':dict(), #start by showing the velocity vectors?  
            #    This is a dict with keys of the particle UInames
            #    , and is boolean
            'velType':dict(), #default type of velocity vectors to plot.  
            #    This is a dict with keys of the particle UInames, 
            #    and must be either 'line', 'arrow', or 'triangle'.  (default is 'line')
            'color':dict(), #set the default color, This is a dict with keys 
            #    of the particle UInames, must contain 
            #    4-element lists with rgba. (default is random colors with a = 1)
            'sizeMult':dict(), #set the default point size multiplier. This is a 
            #    dict with keys of the particle UInames,
            #     default for all sizes is 1.
            'showParts':dict(), #show particles by default. This is a dict with 
            #    keys of the particle UInames, 
            #    boolean, default is true.
        }
        
        ## settings that will define the initial values of the /filters/ in the particle UI panes
        ##  and consequently what particles are filtered at startup.
        self.particle_filter_settings = {
            'filterVals':dict(), #initial filtering selection. This is a dict 
            #    with initial keys of the particle UInames, 
            #    then for each filter the [min, max] range 
            #    (e.g., 'filter':{'Gas':{'log10Density':[0,1],'magVelocities':[20, 100]}} )
            'filterLims':dict(), #initial [min, max] limits to the filters. 
            #    This is a dict with initial keys of the UInames 
            #    , then for each filter the [min, max] range 
            #    (e.g., 'filter':{'Gas':{'log10Density':[0,1],'magVelocities':[20, 100]}} )
        }

        ## settings that will define the initial values of the /colormap/ in the particle UI panes
        ##  and consequently what particles are colored at startup.
        self.particle_colormap_settings = {
            'colormapVals':dict(), #initial coloring selection. This is a dict 
            #    with initial keys of the particle UInames, 
            #    then for each color the [min, max] range 
            #    (e.g., 'colormapVals':{'Gas':{'log10Density':[0,1],'magVelocities':[20, 100]}} )
            'colormapLims':dict(), #initial [min, max] limits to the colors. 
            #    This is a dict with initial keys of the UInames 
            #    , then for each color the [min, max] range 
            #    (e.g., 'colormapLims':{'Gas':{'log10Density':[0,1],'magVelocities':[20, 100]}} )
            'colormap':dict(), # which colormap to use for each gas particle, defined by 
            # the index of the row of a grid of colors that should be posted online TODO
            # (index + 0.5) * (8/256)
            # (e.g. 'colormap':{'Gas':0.015625, 'Stars':0.015625}
            'colormapVariable':dict(), #index in arrays_to_track of array to colormap by 
            # (e.g. 'colormapVariable':{'Gas':0, 'Stars':0}
            'showColormap':dict(), # flags for whether the colormap should be initialized at startup
            # (e.g. 'showColormap':{'Gas':False, 'Stars':False}
        }

    def addToSettings(
        self,
        particleGroup):
        """
        Adds a particle group's settings_default to the settings that require 
        dictionaries for each particle group.
        Input:
            particleGroup - the ParticleGroup instance that you want to add to this
                Settings instance.
        """
        for key in [
            'UIparticle','UIdropdown','UIcolorPicker',
            'color','sizeMult','showParts',
            'filterVals','filterLims','colormapVals','colormapLims','showVel','plotNmax','velType','colormap','colormapVariable','showColormap']:
            self[key][particleGroup.UIname]=particleGroup.settings_default[key]
        
        ## and link this particle group to this Settings instance, for better or worse.
        particleGroup.linked_settings = self

    def outputToDict(
        self):
        """
        Concatenates all the settings dicts into a single dictionary.
        Input:
            None
        """

        all_settings_dict = {}
        for attr in self.__dict__.keys():
            if '_settings' in attr:
                all_settings_dict.update(getattr(self,attr))
        return all_settings_dict

    def outputToJSON(
        self,
        JSONdir,
        filename=None,
        JSON_prefix='',
        loud=1,
        write_jsons_to_disk=True):
        """
        Saves the current settings to a JSON file.
        Input:
            JSONdir - path for this file to get saved to
            prefix='' - string to prepend to self.settings_filename
            loud=1 - flag for whether warnings should be shown
        """
        filename = self.settings_filename if filename is None else filename
        all_settings_dict = self.outputToDict()


        filename = os.path.join(JSONdir,JSON_prefix+filename)

        if loud:
            warnings.warn(FireflyWarning(
                "You will need to add this settings filename to"+
                " filenames.json if this was not called by a Reader instance."))

        ## convert dictionary to a JSON
        return filename,write_to_json(
            all_settings_dict,
            filename if write_jsons_to_disk else None) ## None -> string

    def loadFromJSON(self,
        filename,loud=1):
        """
        Replaces the current settings with those stored in a JSON file.
        Input:
            loud=1 - Flag to print the differences from your current settings file
        """

        if os.path.isfile(filename):
            settings_dict = load_from_json(filename)
        else:
            raise IOError("Settings file: %s doesn't exist."%filename) 

        for key in settings_dict.keys():
            if loud:
                if np.all(settings_dict[key] != self[key]):
                    print("replacing",key)
                    print(self[key],'-->',settings_dict[key])
            self[key]=settings_dict[key]
