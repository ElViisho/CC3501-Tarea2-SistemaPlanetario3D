"""

"""

import glfw
from OpenGL.GL import *

import transformations as tr
import basic_shapes as bs
import scene_graph as sg
import easy_shaders as es
import numpy as np
import lighting_shaders as ls
import model
import random

from OpenGL.GL import glClearColor
from typing import List

import json

class Body(object):
    listaSat: List['Body']
    
    def __init__(self, data, parent):
        # Figuras básicas
        self.nombre = data[" Nombre"]
        self.color = data[" Color"]
        self.radio = data[" Radius"]
        self.dist = data[" Distance"]
        self.velocity = data[" Velocity"]
        self.modelo = data[" Model"]
        self.inclination = data[" Inclination"]
        if data[" Satellites"] != " Null":
            self.sateliteData = []
            for i in data[" Satellites"]:
                self.sateliteData.append(i)
        else:
            self.sateliteData = " Null"

        self.parent = parent

        if self.modelo != " Null":
            gpu_body = es.toGPUShape(bs.readOBJ(self.modelo, (self.color[0], self.color[1], self.color[2])))
        else:
            if self.parent == None:
                gpu_body = es.toGPUShape(model.generateSun(20, 20, self.color))
            else:
                gpu_body = es.toGPUShape(model.generateSphereShapeNormals(20, 20, self.color))
        
        cuerpo = sg.SceneGraphNode('cuerpo')
        cuerpo.childs += [gpu_body]
        
        self.model = cuerpo

        self.gpuNombre = es.toGPUShape(bs.createTextureQuad("Texturas\\Nombres\\"+self.nombre+".png"), GL_REPEAT, GL_NEAREST)

    def draw(self, pipeline, projection, view, theta, viewPos):
        model = self.update(theta)
        if self.parent == None:
            pipeline = es.SimpleModelViewProjectionShaderProgram()
            glUseProgram(pipeline.shaderProgram)
            glUniformMatrix4fv(glGetUniformLocation(pipeline.shaderProgram, 'projection'), 1, GL_TRUE, projection)
            glUniformMatrix4fv(glGetUniformLocation(pipeline.shaderProgram, 'view'), 1, GL_TRUE, view)
            glUniformMatrix4fv(glGetUniformLocation(pipeline.shaderProgram, "model"), 1, GL_TRUE, model)
            sg.drawSceneGraphNode(self.model, pipeline, 'transform')
        else:
            glUseProgram(pipeline.shaderProgram)
            # Drawing the shapes
            # White light in all components: ambient, diffuse and specular.
            glUniform3f(glGetUniformLocation(pipeline.shaderProgram, "La"), 1.0, 1.0, 1.0)
            glUniform3f(glGetUniformLocation(pipeline.shaderProgram, "Ld"), 0.5, 0.5, 0.4)
            glUniform3f(glGetUniformLocation(pipeline.shaderProgram, "Ls"), 0.5, 0.5, 0.4)

            glUniform3f(glGetUniformLocation(pipeline.shaderProgram, "Ka"), 0.2, 0.2, 0.2)
            glUniform3f(glGetUniformLocation(pipeline.shaderProgram, "Kd"), 0.3, 0.3, 0.3)
            glUniform3f(glGetUniformLocation(pipeline.shaderProgram, "Ks"), 0.5, 0.5, 0.5)

            # TO DO: Explore different parameter combinations to understand their effect!

            glUniform3f(glGetUniformLocation(pipeline.shaderProgram, "lightPosition"), 0, 0, 0)
            glUniform3f(glGetUniformLocation(pipeline.shaderProgram, "viewPosition"), viewPos[0], viewPos[1], viewPos[2])
            glUniform1ui(glGetUniformLocation(pipeline.shaderProgram, "shininess"), 1)
            
            glUniform1f(glGetUniformLocation(pipeline.shaderProgram, "constantAttenuation"), 0.0001)
            glUniform1f(glGetUniformLocation(pipeline.shaderProgram, "linearAttenuation"), 0.01)
            glUniform1f(glGetUniformLocation(pipeline.shaderProgram, "quadraticAttenuation"), 0.01)  
            glUniformMatrix4fv(glGetUniformLocation(pipeline.shaderProgram, 'projection'), 1, GL_TRUE, projection)
            glUniformMatrix4fv(glGetUniformLocation(pipeline.shaderProgram, 'view'), 1, GL_TRUE, view)
            glUniformMatrix4fv(glGetUniformLocation(pipeline.shaderProgram, 'model'), 1, GL_TRUE, model)
            sg.drawSceneGraphNode(self.model, pipeline, 'transform')

    def update(self, theta):
        if self.parent == None:
            return tr.uniformScale(self.radio)
        
        return tr.matmul([tr.translate(self.dist*np.cos(self.velocity*theta), 
                            self.dist*np.sin(self.velocity*theta), 
                            0),
                        tr.translate(self.parent.dist*np.cos(self.parent.velocity*theta), 
                            self.parent.dist*np.sin(self.parent.velocity*theta), 0),

                        tr.translate(0,0,self.dist*self.inclination*np.sin(self.velocity*theta)),
                        tr.translate(0,0,self.parent.dist*self.parent.inclination*np.sin(self.parent.velocity*theta)),
                        tr.uniformScale(self.radio)
                        ]) 

    def getPos(self, theta):
        if self.parent == None:
            return np.array([0,0,0])
        x = self.dist*np.cos(self.velocity*theta) + self.parent.dist*np.cos(self.parent.velocity*theta)
        y = self.dist*np.sin(self.velocity*theta) + self.parent.dist*np.sin(self.parent.velocity*theta)
        z = self.dist*self.inclination*np.sin(self.velocity*theta) + self.parent.dist*self.parent.inclination*np.sin(self.parent.velocity*theta)
        return np.array([x,y,z])



class Orbita(object):
    def __init__(self, radio, x0, y0, vel, inclination, inclinationP):

        self.radio = radio
        self.velocity = vel
        self.inclination = inclination
        self.inclinationP = inclinationP
        self.x0 = x0

        gpu_orbit = es.toGPUShape(bs.createOrbit(self.radio, x0, y0))
        
        orbita = sg.SceneGraphNode('orbita')
        orbita.childs += [gpu_orbit]

        orbitaTR = sg.SceneGraphNode('orbitaTR')
        orbitaTR.childs += [orbita]

        self.model = orbitaTR

    def draw(self, pipeline, projection, view, theta):
        model = tr.matmul([tr.translate(-self.x0+self.x0*np.cos(self.velocity*theta), 
                            self.x0*np.sin(self.velocity*theta), 0),
                            tr.translate(0,0,self.inclinationP*self.x0*np.sin(self.velocity*theta)),
                            tr.shearing(0,0,0,0,0,self.inclination)
                        ])
        glUseProgram(pipeline.shaderProgram)
        glUniformMatrix4fv(glGetUniformLocation(pipeline.shaderProgram, 'projection'), 1, GL_TRUE, projection)
        glUniformMatrix4fv(glGetUniformLocation(pipeline.shaderProgram, 'view'), 1, GL_TRUE, view)
        glUniformMatrix4fv(glGetUniformLocation(pipeline.shaderProgram, "model"), 1, GL_TRUE, model)
        sg.drawSceneGraphNode(self.model, pipeline, 'transform')

    


class Bodies(object):
    bodies: List['Body']

    def __init__(self):
        self.bodies = []
        self.orbits = []
        self.asteroides = []
        self.bodyCount = 0

    def createBodies(self, data, parent):
        self.bodies.append(Body(data, parent))
        self.bodyCount += 1
        ThisBody = Body(data, parent)
        n = len(ThisBody.sateliteData)
        i = 0
        while i<n:
            if ThisBody.sateliteData[i] != " Null":
                if isinstance(ThisBody.sateliteData[i], str):
                    return
                NewBody = ThisBody.sateliteData[i]
                self.orbits.append(Orbita(NewBody[" Distance"], ThisBody.dist, 0, ThisBody.velocity, NewBody[" Inclination"], ThisBody.inclination))
                Bodies.createBodies(self, NewBody, ThisBody)
            i += 1
        

        todo = sg.SceneGraphNode('todo')
        for i in self.bodies:
            todo.childs += [i] 

    def createAsteroides(self, n):
        #Asteroides
        f = 0
        while f < n:
            scaleX = random.randint(100, 800)/1000
            scaleY = random.randint(100, 800)/1000
            scaleZ = random.randint(100, 800)/1000
            rotateX = random.randint(1, 180)
            rotateY = random.randint(1, 180)
            rotateZ = random.randint(1, 180)
            self.asteroides.append(Asteroide(scaleX, scaleY, scaleZ, (360/n)*f, rotateX, rotateY, rotateZ))
            f += 1

    def draw(self, pipeline, projection, view, theta, viewPos):
        for k in self.bodies:
            k.draw(pipeline, projection, view, theta, viewPos)
        for l in self.asteroides:
            l.draw(pipeline, projection, view, theta, viewPos)
        for j in self.orbits:
            pipeline = es.SimpleModelViewProjectionShaderProgram()
            j.draw(pipeline, projection, view, theta)
        




class Asteroide(object):
    def __init__(self, scaleX, scaleY, scaleZ, offset, rotateX, rotateY, rotateZ):
        
        self.dist = 3
        self.velocity = 0.005
        self.scaleX = scaleX
        self.scaleY = scaleY
        self.scaleZ = scaleZ
        self.offset = offset
        self.rotateX = rotateX
        self.rotateY = rotateY
        self.rotateZ = rotateZ

        gpu_body = es.toGPUShape(bs.readOBJ("Cuerpos\\Asteroide.obj", (0.6, 0.6, 0.65)))

        cuerpo = sg.SceneGraphNode('cuerpo')
        cuerpo.childs += [gpu_body]
        
        self.model = cuerpo
        

    def draw(self, pipeline, projection, view, theta, viewPos):
        model = self.update(theta)
        
        glUseProgram(pipeline.shaderProgram)
        # Drawing the shapes
        # White light in all components: ambient, diffuse and specular.
        glUniform3f(glGetUniformLocation(pipeline.shaderProgram, "La"), 1.0, 1.0, 1.0)
        glUniform3f(glGetUniformLocation(pipeline.shaderProgram, "Ld"), 0.5, 0.5, 0.4)
        glUniform3f(glGetUniformLocation(pipeline.shaderProgram, "Ls"), 0.5, 0.5, 0.4)

        glUniform3f(glGetUniformLocation(pipeline.shaderProgram, "Ka"), 0.2, 0.2, 0.2)
        glUniform3f(glGetUniformLocation(pipeline.shaderProgram, "Kd"), 0.3, 0.3, 0.3)
        glUniform3f(glGetUniformLocation(pipeline.shaderProgram, "Ks"), 0.5, 0.5, 0.5)

        # TO DO: Explore different parameter combinations to understand their effect!

        glUniform3f(glGetUniformLocation(pipeline.shaderProgram, "lightPosition"), 0, 0, 0)
        glUniform3f(glGetUniformLocation(pipeline.shaderProgram, "viewPosition"), viewPos[0], viewPos[1], viewPos[2])
        glUniform1ui(glGetUniformLocation(pipeline.shaderProgram, "shininess"), 1)
        
        glUniform1f(glGetUniformLocation(pipeline.shaderProgram, "constantAttenuation"), 0.0001)
        glUniform1f(glGetUniformLocation(pipeline.shaderProgram, "linearAttenuation"), 0.01)
        glUniform1f(glGetUniformLocation(pipeline.shaderProgram, "quadraticAttenuation"), 0.01)  
        glUniformMatrix4fv(glGetUniformLocation(pipeline.shaderProgram, 'projection'), 1, GL_TRUE, projection)
        glUniformMatrix4fv(glGetUniformLocation(pipeline.shaderProgram, 'view'), 1, GL_TRUE, view)
        glUniformMatrix4fv(glGetUniformLocation(pipeline.shaderProgram, 'model'), 1, GL_TRUE, model)
        sg.drawSceneGraphNode(self.model, pipeline, 'transform')

    def update(self, theta):
        return tr.matmul([tr.translate(self.dist*np.cos(self.velocity*theta+self.offset), 
                            self.dist*np.sin(self.velocity*theta+self.offset), 0), 
                            tr.uniformScale(0.05), 
                            tr.scale(self.scaleX, self.scaleY, self.scaleZ),
                            tr.rotationX(self.rotateX),
                            tr.rotationY(self.rotateY),
                            tr.rotationZ(self.rotateZ)])

    