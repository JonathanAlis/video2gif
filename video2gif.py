# img_viewer.py

import PySimpleGUI as sg
import os.path
from moviepy.editor import *
import cv2
import time

# First the window layout in 2 columns

INITIAL_HEIGHT = 480
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
    [sg.Button("Undo"), sg.Button("Redo")],
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

def apply_transform(clip,t):
    if t[0]=='flip':
        if t[1]=='x':
            clip = clip.fx( vfx.mirror_x)
        elif t[1]=='y':
            clip = clip.fx( vfx.mirror_y)
        else:
            raise Error('Invalid transform')

    elif t[0]=='rotate':
        if t[1]=='90':
            clip = clip.rotate(90)   
        elif t[1]=='-90':
            clip = clip.rotate(90)   
        else:
            raise Error('Invalid transform')
    
    elif t[0] == 'scale change':
        clip=fullclip.resize(height=t[1])
        print(t[1])

    elif t[0] == 'cut inside':
        clip=clip.subclip(t[1], t[2])
        dur = clip.duration
        play_range=(0,dur)
        window.Element("start_slider").Update(range=(0,dur), value=0)#, tick_interval=dur/10)
        window.Element("end_slider").Update(range=(0,dur), value=dur)#, tick_interval=dur/10)
        window.Element("trackbar").Update(range=(0,dur), value=dur)#, tick_interval=dur/10)
        window["end_slider"].update(value=dur)  
        window["trackbar"].update(value=0)  
        window["start_slider"].update(value=0)
        window["-IMAGE-"].update(clip_image(clip,0))
        

    elif t[0] == 'cut outside':
        clip1=clip.subclip(0, t[1])
        clip2=clip.subclip(t[2], clip.duration)
        clip=concatenate_videoclips([clip1,clip2], method='compose')
        dur = clip.duration
        play_range=(0,dur)
        window.Element("start_slider").Update(range=(0,dur), value=0)#, tick_interval=dur/10)
        window.Element("end_slider").Update(range=(0,dur), value=dur)#, tick_interval=dur/10)
        window.Element("trackbar").Update(range=(0,dur), value=dur)#, tick_interval=dur/10)
        window["end_slider"].update(value=dur)  
        window["trackbar"].update(value=0)  
        window["start_slider"].update(value=0)
        window["-IMAGE-"].update(clip_image(clip,0))
        
    return clip

def apply_transforms(initialclip, transforms, idx = None):
    window.Element("start_slider").Update(range=(0,initialclip.duration))
    window.Element("end_slider").Update(range=(0,initialclip.duration))
    window.Element("trackbar").Update(range=(0,initialclip.duration))
    

    if len(transforms)==0:
        return initialclip.resize(height=INITIAL_HEIGHT)
    clip=initialclip
    # the only scaling applied is the last one
    scale_change_indexes=[loc for loc, t in enumerate(transforms) if t[0] == 'scale change']
    print(scale_change_indexes,'___________________________')
    if len(scale_change_indexes)>0:
        last_scale_index = max(scale_change_indexes)
        clip = apply_transform(clip, transforms[last_scale_index])
        print(transforms[last_scale_index],'__________')
    else:
        image=clip.get_frame(0)
        if image.shape[0]>INITIAL_HEIGHT:
            clip=clip.resize(height=INITIAL_HEIGHT)
    trans = [t for t in transforms[0:idx] if t[0] != 'scale change'] 

    for t in trans:
        clip=apply_transform(clip,t)

    window["-IMAGE-"].update(clip_image(clip,current_time))
    return clip


window = sg.Window("Video to GIF", layout)
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
playing = False
paused=False
play_time = 0.0
frame = 0
is_video_loaded=False
scale = 1
current_time=0
trackbar_time=current_time
fps=1
play_range=(0,10)
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
        event, values = window.read(timeout = 1000/fps)

    print(event,values)
    if event == "Exit" or event == sg.WIN_CLOSED:
        break

    # Load video
    print(event)
    if event == "Load/Reload Video" and values["-VIDEO-SELECTED-"].endswith('.mp4'):
        playing=False
        file = values["-VIDEO-SELECTED-"]
        try:
            fullclip = VideoFileClip(file)
            clip=fullclip.copy()
            image = clip.get_frame(0)
            original_shape=image.shape
            current_shape=original_shape
            if image.shape[0]>INITIAL_HEIGHT:
                clip=clip.resize(height=INITIAL_HEIGHT)
                image = clip.get_frame(0)
                current_shape=image.shape

            scale=current_shape[0]/original_shape[0]
            dur = clip.duration
            fps=clip.fps
            is_video_loaded=True
            play_range=(0,dur)
            transforms=[]
            transform_index=0

            window.Element("scale_slider").Update(range=(30,original_shape[0]), value=current_shape[0])
            window.Element("start_slider").Update(range=play_range, value=0)#, tick_interval=dur/10)
            window.Element("end_slider").Update(range=play_range, value=dur)#, tick_interval=dur/10)
            window.Element("trackbar").Update(range=play_range, value=dur)#, tick_interval=dur/10)
            window["end_slider"].update(value=dur)  
            window["trackbar"].update(value=0)  
            window["-IMAGE-"].update(image_2_bytes(image))

        except:
            raise Warning("Error loading the file")
            break
    
    elif event == 'Save GIF' and is_video_loaded:
        filename = values['Save GIF']
        if filename:
            print('saving:', filename)
            clip.write_gif(filename)
            try:
                from pygifsicle import optimize
                optimize(filename)
            except:
                raise Warning('Error in pyfigsicle, not optimizing gif.')
                
    elif event == 'Save PNG' and is_video_loaded:
        filename = values['Save PNG']
        if filename:
            print('saving:', filename)
            clip.save_frame(filename, current_time)

    # change scale
    elif event == "scale_slider" and is_video_loaded: 
        transform=('scale change',values['scale_slider'])      
        if len(transforms)>0 and transforms[-1][0] == 'scale change': #only save last change
                transforms[-1]=transform
        else:
            transforms=transforms[0:transform_index]
            transforms.append(transform)
            transform_index+=1
        
        print(transforms)
        clip=apply_transforms(fullclip,transforms)
        window["-IMAGE-"].update(clip_image(clip,current_time))
        

    elif event == "start_slider" and is_video_loaded: 
        playing=False
        current_time=values['start_slider']
        play_range=(current_time,values['end_slider'])
        if current_time >  values["end_slider"]:
            window["end_slider"].update(value=current_time)    
        window["-IMAGE-"].update(clip_image(clip,current_time))
        

    elif event == "end_slider" and is_video_loaded: 
        playing=False
        current_time=values['end_slider']
        play_range=(values['start_slider'],current_time)
        if current_time <  values["start_slider"]:
            window["start_slider"].update(value=current_time) 
        window["-IMAGE-"].update(clip_image(clip,current_time))

    elif event == "trackbar" and is_video_loaded: 
        current_time=values['trackbar']
        window["-IMAGE-"].update(clip_image(clip,current_time))

    
    
    elif event == 'Cut inside':
        transform = ('cut inside',values['start_slider'],values['end_slider'])
        clip = apply_transform(clip, transform)        
        dur = clip.duration
        transforms=transforms[0:transform_index]
        transforms.append(transform)
        transform_index+=1
        play_range=(0,dur)
        
    
    elif event == 'Cut outside':
        transform = ('cut outside',values['start_slider'],values['end_slider'])
        clip = apply_transform(clip, transform)        
        dur = clip.duration
        play_range=(0,dur)
        transforms=transforms[0:transform_index]
        transforms.append(transform)
        transform_index+=1

    elif event == 'Flip x':
        transform = ('flip','x')
        clip = apply_transform(clip, transform)
        window["-IMAGE-"].update(clip_image(clip,current_time))
        transforms=transforms[0:transform_index]
        transforms.append(transform)
        transform_index+=1
    
    elif event == 'Flip y':
        transform = ('flip','y')
        clip = apply_transform(clip, transform)
        window["-IMAGE-"].update(clip_image(clip,current_time))
        transforms=transforms[0:transform_index]
        transforms.append(transform)
        transform_index+=1

    elif event == 'Rotate 90':
        transform = ('rotate','90')
        clip = apply_transform(clip, transform)
        window["-IMAGE-"].update(clip_image(clip,current_time))
        transforms=transforms[0:transform_index]
        transforms.append(transform)
        transform_index+=1

    elif event == 'Rotate -90':
        transform = ('rotate','-90')
        clip = apply_transform(clip, transform)
        window["-IMAGE-"].update(clip_image(clip,current_time))
        transforms=transforms[0:transform_index]
        transforms.append(transform)
        transform_index+=1
    
    # TODO: solve to correctly disable undo button
    elif event == 'Undo' and transform_index > 0:
        #window['Undo'].update(disabled = (transform_index == 0) ) 
        #window['Redo'].update(disabled = (transform_index == len(transforms)-1) or len(transforms) == 0)
        transform_index-=1
        clip=apply_transforms(fullclip,transforms[:transform_index])
        window["-IMAGE-"].update(clip_image(clip,current_time))


    elif event == 'Redo' and transform_index < len(transforms):
        #window['Undo'].update(disabled = (transform_index == 0) ) 
        #window['Redo'].update(disabled = (transform_index == len(transforms)-1) or len(transforms) == 0)
        transform_index+=1
        clip=apply_transforms(fullclip,transforms[:transform_index])
        window["-IMAGE-"].update(clip_image(clip,current_time))
        
        

    elif event == 'Play':        
        playing=True
        play_time=time.time()
        paused=False
    
    elif event == 'Stop':
        playing=False
        trackbar_time= 0
        window["-IMAGE-"].update(clip_image(clip,current_time))
        window["trackbar"].update(trackbar_time)

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
        trackbar_time=(time.time()-play_time)+play_range[0]
        if trackbar_time < play_range[1]:
            window["trackbar"].update(value=trackbar_time) 
            window["-IMAGE-"].update(clip_image(clip,trackbar_time))
            current_time=trackbar_time
        else:
            playing=False
    
    window['Play'].update(disabled=playing)
    #window['Pause'].update(disabled=paused)
    print('TRANSFOR INDEX' ,transform_index, (transform_index == 0))
    print(transform_index)
    print(transforms)

window.close()
