from math import pi

def format(f): 
    return "%.0f" %f

def change_step(angle):
    step = angle * 4096/360 
    return step

def change_rad(step):
    rad = step * (2*pi)/4096 
    return rad
