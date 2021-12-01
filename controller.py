"""
Clase controlador, obtiene el input, lo procesa, y manda los mensajes
a los modelos.
"""

import glfw
import sys
from modelos import Body, Bodies
import numpy as np

class Controller(object):

    def __init__(self):
        self.camera_theta = np.pi/4
        self.camera_phi = 2
        self.camera_rho = 2
        self.ModoVisualizacion = 0

        self.moveSpeed = 3
        self.sel = 0
        self.selMax = 0
        

    def on_key(self, window, key, scancode, action, mods):
        
        if key == glfw.KEY_ESCAPE:
            sys.exit()

        elif key == glfw.KEY_V and action == glfw.PRESS:
            self.ModoVisualizacion = not self.ModoVisualizacion

        # Cambiar selección
        if (self.ModoVisualizacion == 1):
            if key == glfw.KEY_RIGHT and action == glfw.PRESS:
                self.sel += 1
                if self.sel >= self.selMax:
                    self.sel = 0
            # Cambiar selección
            elif key == glfw.KEY_LEFT and action == glfw.PRESS:
                self.sel -= 1
                if self.sel < 0:
                    self.sel = self.selMax - 1

    def update(self):
        pass