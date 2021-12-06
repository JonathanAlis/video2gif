# img_viewer.py

import PySimpleGUI as sg
import os.path
from moviepy.editor import *
import cv2
import time

# First the window layout in 2 columns

INITIAL_HEIGHT = 240
transforms = [
    [
        sg.Text("Select a video:"),
        sg.In(size=(25, 1), enable_events=True, key="-VIDEO-SELECTED-"),
        sg.FilesBrowse(file_types=[("Video Files", "*.mp4")]),
        sg.Button("Load/Reload Video")
    ],
    [   sg.Text("Height:"),
        sg.Slider(range = (30, 600), resolution=1, tick_interval=50, enable_events = True, orientation= 'horizontal',size=(50,30), key='scale_slider'),
    ],
    [   sg.Text("Start:"),
        sg.Slider(range = (0, 10), resolution=1, tick_interval=10, enable_events = True, orientation= 'horizontal',size=(50,30), key='start_slider'),
    ],
    [   sg.Text("Ending:"),
        sg.Slider(range = (0, 10), resolution=1, tick_interval=10, enable_events = True, orientation= 'horizontal',size=(50,30), key='end_slider'),
    ],
# TODO: change speed
#    [   sg.Text("Speed:"),
#        sg.Slider(range = (0.25, 4), resolution=0.25, tick_interval=10, enable_events = True, orientation= #'horizontal',size=(50,30), key='end_slider'),
#    ],
    [sg.Text("Cut video:"), sg.Button("Cut inside") , sg.Button("Cut outside")],
    [sg.Button("Flip x"), sg.Button("Flip y"), sg.Button("Rotate 90"), sg.Button("Rotate -90")],
# TODO: select a rectangle
#   [sg.Text("Select retangle:"), sg.Button("Retangle", disabled=True)],
    [sg.Button("Undo",disabled=True), sg.Button("Redo",disabled=True)],
]

# For now will only show the name of the file that was chosen
image_viewer_column = [
    [sg.Text(size=(40, 1), key="-TOUT-")],    
    [sg.Image(key="-IMAGE-")],
    [sg.Slider(range = (0, 10), resolution=1, tick_interval=10, enable_events = True, orientation= 'horizontal',size=(50,30), key='trackbar')],
    [sg.Button("Play"),
    #sg.Button("Pause"), 
    sg.Button("Stop"),
    sg.In(size=(25, 1), enable_events=True, visible=False, key="Save GIF"),
    sg.FileSaveAs(button_text = "Save GIF", initial_folder='./', file_types = (('GIF', '*.gif'),)),
    sg.In(size=(25, 1), enable_events=True, visible=False, key="Save PNG"),
    sg.FileSaveAs(button_text = "Save PNG", initial_folder='./', file_types = (('PNG', '*.png'),))
    ]
]

# ----- Full layout -----
layout = [
    
    [
        sg.Column(transforms),
        sg.VSeperator(),
        sg.Column(image_viewer_column),
    ]
]


def image_2_bytes(image):    
    return cv2.imencode('.png', image[...,::-1])[1].tobytes()
def clip_image(clip,time):
    image=clip.get_frame(time)
    return cv2.imencode('.png', image[...,::-1])[1].tobytes()


window = sg.Window("Video to GIF", layout, return_keyboard_events=True, )
'''
window.bind("<Control-KeyPress-z>", "CTRL-Z")
window.bind("<Control-KeyPress-Z>", "CTRL-Z")
window.bind("<Control-KeyRelease-z>", "Release-Z")
window.bind("<Control-KeyRelease-Z>", "Release-Z")
window.bind("<Control-KeyPress-y>", "CTRL-Y")
window.bind("<Control-KeyPress-Y>", "CTRL-Y")
window.bind("<Control-KeyRelease-y>", "Release-Y")
window.bind("<Control-KeyRelease-Y>", "Release-Y")

ctrl_z_on = False
ctrl_y_on = False
'''

class Gif:
    def __init__(self, file):
        self.fullclip = VideoFileClip(file)
        self.original_shape=self.fullclip.get_frame(0).shape        
        
        self.init_clip()

        self.is_video_loaded=True
        self.transforms=[]
        self.transform_index=0
        self.current_time=0

    def init_clip(self):
        self.clip=self.fullclip.copy()
        if self.original_shape[0]>INITIAL_HEIGHT:
            self.clip=self.clip.resize(height=INITIAL_HEIGHT)
        self.image = self.clip.get_frame(0)        
        self.current_shape=self.image.shape
        self.dur = self.clip.duration
        self.fps=self.clip.fps
        self.play_range=(0,self.dur)

            
    def save_gif(self,filename):
        if filename:
            print('saving:', filename)
            self.clip.write_gif(filename)
            try:
                from pygifsicle import optimize
                optimize(filename)
            except:
                raise Warning('Error in pyfigsicle, not optimizing gif.')

    def save_png(self,filename):
        if filename:
            print('saving:', filename)
            self.clip.save_frame(filename, self.current_time)

    
    def change_scale(self,value, release=None):
        transform=('scale change',value)      
        if len(self.transforms)>0 and self.transforms[-1][0] == 'scale change': #only save last change
                self.transforms[-1]=transform
        else:
            self.add_transform(transform)
        self.apply_transform(transform)
        self.current_shape=self.clip.get_frame(self.current_time).shape
        #self.image=self.clip.get_frame(self.current_time)

    
    def cut(self,start, end, inside=True):
        if inside:
            transform = ('cut inside',start, end)
        else: 
            transform = ('cut outside',start, end)
        self.apply_transform(transform)        
        self.add_transform(transform)

    def flip(self,axis = 'x'):
        transform = ('flip',axis)
        self.apply_transform(transform)
        self.add_transform(transform)

    def rotate(self, positive = True):
        if positive:
            transform = ('rotate','90')
        else:
            transform = ('rotate','-90')
        self.apply_transform(transform)
        self.add_transform(transform)

    
    def add_transform(self,transform):
        self.transforms=self.transforms[0:self.transform_index]
        self.transforms.append(transform)
        self.transform_index+=1
        print('TRANSFOR INDEX' ,gif.transform_index, gif.transforms)


    def apply_transform(self,t):
        if t[0]=='flip':
            if t[1]=='x':
                self.clip = self.clip.fx( vfx.mirror_x)
            elif t[1]=='y':
                self.clip = self.clip.fx( vfx.mirror_y)
            else:
                raise Error('Invalid transform')

        elif t[0]=='rotate':
            if t[1]=='90':
                self.clip = self.clip.rotate(90)   
            elif t[1]=='-90':
                self.clip = self.clip.rotate(90)   
            else:
                raise Error('Invalid transform')
        
        elif t[0] == 'scale change':
            self.clip=self.fullclip.resize(height=t[1])
            
        elif t[0] == 'cut inside':
            self.clip=self.clip.subclip(t[1], t[2]) 
            self.dur = self.clip.duration
            self.play_range=(0,self.dur)
       

        elif t[0] == 'cut outside':
            clip1=self.clip.subclip(0, t[1])
            clip2=self.clip.subclip(t[2], self.clip.duration)
            self.clip=concatenate_videoclips([clip1,clip2], method='compose')
            self.dur = self.clip.duration
            self.play_range=(0,self.dur)
       

    def apply_transform_list(self):        
        #clip=fullclip.copy()
        self.init_clip()
        if len(self.transforms)<=0:            
            return
        # the only scaling applied is the last one
        scale_change_indexes=[loc for loc, t in enumerate(self.transforms) if t[0] == 'scale change']
        if len(scale_change_indexes)>0:
            last_scale_index = max(scale_change_indexes)
            self.apply_transform(self.transforms[last_scale_index])
        else:
            self.init_clip()
        
        trans = [t for t in self.transforms[0:self.transform_index] if t[0] != 'scale change'] 
        print(trans)
        for t in trans:
            print(t)
            self.apply_transform(t)
    
    def undo(self):
        self.transform_index=max(self.transform_index-1,0)
        self.apply_transform_list()
        print('TRANSFOR INDEX', gif.transform_index, gif.transforms)


    def redo(self):
        self.transform_index=min(self.transform_index+1,len(self.transforms))
        self.apply_transform_list()
        print('TRANSFOR INDEX', gif.transform_index, gif.transforms)

    
    def display(self):
        return clip_image(self.clip,self.current_time)        

def update_bars(gif, window):
    window.Element("scale_slider").Update(range=(30,gif.original_shape[0]), value=0)
    window["scale_slider"].update(value=gif.current_shape[0])
    window.Element("start_slider").Update(range=(0,gif.dur), value=0)#, tick_interval=dur/10)
    window["start_slider"].update(value=0)
    window.Element("end_slider").Update(range=(0,gif.dur), value=0)#, tick_interval=dur/10)
    window["end_slider"].update(value=gif.dur)  
    window.Element("trackbar").Update(range=(0,gif.dur), value=0)#, tick_interval=dur/10)
    window["trackbar"].update(value=0)      
    window["-IMAGE-"].update(gif.display())
    

playing = False
paused=False
play_time = 0.0
play_start_time = 0.0
is_video_loaded=False
square=(0,0,0,0)
#list of tuples
transforms=[]
transform_index=0
# Run the Event Loop
while True:
    # Timeout set only when playing the video.
    if not playing:
        event, values = window.read()
    else:
        if is_video_loaded:
            event, values = window.read(timeout = 1000/gif.fps)

    if event == "Exit" or event == sg.WIN_CLOSED:
        break
        
    # Load video
    if event == "Load/Reload Video" and values["-VIDEO-SELECTED-"].endswith('.mp4'):
        playing=False
        window['Play'].update('Play')
        file = values["-VIDEO-SELECTED-"]       

        try:
            gif=Gif(file)    
            is_video_loaded=gif.is_video_loaded
        except:
            raise Warning("Error loading the file")
            break
        update_bars(gif,window)
    
    elif event == 'Save GIF' and is_video_loaded:
        filename = values['Save GIF']
        gif.save_gif(filename)
                
    elif event == 'Save PNG' and is_video_loaded:
        filename = values['Save PNG']
        gif.save_png(filename)

    # change scale
    elif event == "scale_slider" and is_video_loaded: 
        gif.change_scale(values['scale_slider'])        
        window["-IMAGE-"].update(gif.display())
        

    elif event == "start_slider" and is_video_loaded: 
        playing=False
        window['Play'].update('Play')
        gif.current_time=values['start_slider']
        gif.play_range=(gif.current_time,values['end_slider'])
        if gif.current_time >  values["end_slider"]:
            window["end_slider"].update(value=gif.current_time)    
        window["-IMAGE-"].update(gif.display())
        

    elif event == "end_slider" and is_video_loaded: 
        playing=False
        window['Play'].update('Play')
        gif.current_time=values['end_slider']
        gif.play_range=(values['start_slider'],gif.current_time)
        if gif.current_time <  values["start_slider"]:
            window["start_slider"].update(value=gif.current_time) 
        window["-IMAGE-"].update(gif.display())

    elif event == "trackbar" and is_video_loaded: 
        gif.current_time=values['trackbar']
        window["-IMAGE-"].update(gif.display())         
        if playing:
            playing=False   
            window['Play'].update('Play')
    
    elif event == 'Cut inside' and is_video_loaded:
        gif.cut(values['start_slider'],values['end_slider'], inside=True)        
        update_bars(gif, window)        
    
    elif event == 'Cut outside' and is_video_loaded:
        gif.cut(values['start_slider'],values['end_slider'], inside=False)
        update_bars(gif, window)

    elif event == 'Flip x' and is_video_loaded:
        gif.flip(axis = 'x')
        window["-IMAGE-"].update(gif.display())
    
    elif event == 'Flip y' and is_video_loaded:
        gif.flip(axis = 'y')
        window["-IMAGE-"].update(gif.display())
    
    elif event == 'Rotate 90' and is_video_loaded:
        gif.rotate(positive=True)
        window["-IMAGE-"].update(gif.display())

    elif event == 'Rotate -90' and is_video_loaded:
        gif.rotate(positive=False)
        window["-IMAGE-"].update(gif.display())
    
    # TODO: solve to correctly disable undo button
    elif event == 'Undo' and gif.transform_index > 0 and is_video_loaded:
        #window['Undo'].update(disabled = (transform_index == 0) ) 
        #window['Redo'].update(disabled = (transform_index == len(transforms)-1) or len(transforms) == 0)
        gif.undo()
        update_bars(gif, window)
        window["-IMAGE-"].update(gif.display())

    elif event == 'Redo' and gif.transform_index < len(gif.transforms) and is_video_loaded:
        #window['Undo'].update(disabled = (transform_index == 0) ) 
        #window['Redo'].update(disabled = (transform_index == len(transforms)-1) or len(transforms) == 0)
        gif.redo()
        gif.display()
        update_bars(gif, window)
        window["-IMAGE-"].update(gif.display())

        

    elif event == 'Play' and is_video_loaded:
        if playing:
            window['Play'].update('Play')
            playing=False
        else:
            window['Play'].update('Pause')      
            playing=True
            play_time=time.time()
            play_start_time=values['trackbar']
            paused=False
    
    elif event == 'Stop' and is_video_loaded:
        window['Play'].update('Play')
        playing=False
        window["-IMAGE-"].update(gif.display())
        window["trackbar"].update(0)

#print(event,values)
    if not event=='__TIMEOUT__' and is_video_loaded:
        window['Undo'].update(disabled = (gif.transform_index == 0) ) 
        window['Redo'].update(disabled = (gif.transform_index >= len(gif.transforms)))
    
    ''' TODO: control Z
        elif (event == "CTRL-B" and not ctrl_z_on):
            ctrl_z_on == True

        elif event == "Release-B":
            ctrl_z_on = False
    '''
    ''' TODO: pause button
    elif event == 'Pause':
        if playing:
            playing=False
            paused=True
        if paused:
            playing=True
            paused=False
    '''
    #play the video        
    if is_video_loaded and playing:        
        trackbar_time=(time.time()-play_time)+play_start_time
        if trackbar_time < gif.play_range[1]:
            window["trackbar"].update(value=trackbar_time) 
            window["-IMAGE-"].update(gif.display())
            gif.current_time=trackbar_time
        else:
            playing=False
            window['Play'].update('Play')
    
    #window['Pause'].update(disabled=paused)
    #print(transforms)

window.close()
