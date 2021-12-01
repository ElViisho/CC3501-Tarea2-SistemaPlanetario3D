"""
Esta es la clase vista. Contiene el ciclo de la aplicación y ensambla
las llamadas para obtener el dibujo de la escena.
"""

import glfw
from OpenGL.GL import *
import sys
import easy_shaders as es
import basic_shapes as bs
import transformations as tr
import numpy as np
import lighting_shaders as ls

from modelos import *
from controller import Controller

archivo = sys.argv[1]

if __name__ == '__main__':

    # Initialize glfw
    if not glfw.init():
        sys.exit()

    width = 1200
    height = 700

    window = glfw.create_window(width, height, 'Sistema Planetario 3D', None, None)

    if not window:
        glfw.terminate()
        sys.exit()

    glfw.make_context_current(window)

    controlador = Controller()

    # Connecting the callback function 'on_key' to handle keyboard events
    glfw.set_key_callback(window, controlador.on_key)

    # Assembling the shader program (pipeline) with both shaders
    pipelineFiguras = ls.SimplePhongShaderProgram()
    pipelineTexturas = es.SimpleTextureTransformShaderProgram()
    pipelineTexturas3D = es.SimpleTextureModelViewProjectionShaderProgram()

    # Setting up the clear screen color
    glClearColor(0.25, 0.25, 0.25, 1.0)

    # As we work in 3D, we need to check which part is in front,
    # and which one is at the back
    glEnable(GL_DEPTH_TEST)
    # Enabling transparencies
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

    bodies = Bodies()

    with open(archivo) as bodyData:
        bData = json.load(bodyData)

    bodies.createBodies(bData, None)
    
    CantidadAsteroides = 20 ###Cambiar para ver más asteroides, si se ponen 150 ya se ve un cinturón
    bodies.createAsteroides(CantidadAsteroides)

    t0 = glfw.get_time()

    controlador.selMax = bodies.bodyCount
    camera_theta = np.pi/4
    camera_h = 2
    maxH = 4
    camera_rho = 4
    minRho = 0.5
    maxRho = 7

    skyBox = bs.createTextureCube('Texturas\\fondoEstrellado.png')
    GPUSkyBox = es.toGPUShape(skyBox, GL_REPEAT, GL_LINEAR)
    
    gpuBaseInfo = es.toGPUShape(bs.createTextureQuad("Texturas\\BaseInfo.png"), GL_REPEAT, GL_NEAREST)
    barritasFrames = ['', '','', '','', '','', '']
    for i in range(8):
        barritasFrames[i] = ("Texturas\\animacionBarritas\\frame" + str(i+1) + ".png")

    skybox_transform = tr.uniformScale(20)

    controlador.selMax = bodies.bodyCount
    info = False


    while not glfw.window_should_close(window):  # Dibujando --> 1. obtener el input
        
        # Using GLFW to check for input events
        glfw.poll_events()  # OBTIENE EL INPUT --> CONTROLADOR --> MODELOS

        # Clearing the screen in both, color and depth
        glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        controlador.update()

        # Theta para la rotacion
        theta = -10 * glfw.get_time()

        projection = tr.perspective(45, float(width)/float(height), 0.1, 100)

        # Getting the time difference from the previous iteration
        t1 = glfw.get_time()
        dt = t1 - t0
        t0 = t1

        if (controlador.ModoVisualizacion == 0):
        # Vista global
            info = False
            if (glfw.get_key(window, glfw.KEY_D) == glfw.PRESS):
                camera_theta -= 2 * dt
            if (glfw.get_key(window, glfw.KEY_A) == glfw.PRESS):
                camera_theta += 2* dt
            if (glfw.get_key(window, glfw.KEY_S) == glfw.PRESS):
                camera_h -= 2 * dt
            if (glfw.get_key(window, glfw.KEY_W) == glfw.PRESS):
                camera_h += 2* dt
            if (abs(camera_h) > maxH): camera_h = maxH*np.sign(camera_h)
            if (glfw.get_key(window, glfw.KEY_Z) == glfw.PRESS):
                camera_rho -= 2 * dt
            if (glfw.get_key(window, glfw.KEY_X) == glfw.PRESS):
                camera_rho += 2* dt
            if (camera_rho < minRho): camera_rho = minRho
            if (camera_rho > maxRho): camera_rho = maxRho

            camX = camera_rho * np.sin(camera_theta)
            camY = camera_rho * np.cos(camera_theta)
            camZ = camera_h

            viewPos = np.array([camX,camY,camZ])

            view = tr.lookAt(
                viewPos,
                np.array([0,0,0]),
                np.array([0,0,1])
            )
        else:
        # Vista por cuerpo
            info = True
            viewPos = bodies.bodies[controlador.sel].getPos(theta)
            NombrePlaneta = bodies.bodies[controlador.sel].gpuNombre
            radioPlaneta = 15*bodies.bodies[controlador.sel].radio
            viewPos[0] -= radioPlaneta
            viewPos[1] -= radioPlaneta
            viewPos[2] += radioPlaneta

            lookAt = bodies.bodies[controlador.sel].getPos(theta)

            view = tr.lookAt(
                viewPos,
                lookAt,
                np.array([0,0,1])
            )
            

        rotation_theta = glfw.get_time()

        axis = np.array([1,-1,1])
        axis = axis / np.linalg.norm(axis)
        model = tr.rotationA(rotation_theta, axis)
        model = tr.identity()

        # Drawing skybox. This shader doesn't use lights, it is not affected by lights.
        glUseProgram(pipelineTexturas3D.shaderProgram)
        glUniformMatrix4fv(glGetUniformLocation(pipelineTexturas3D.shaderProgram, "model"), 1, GL_TRUE, skybox_transform)
        glUniformMatrix4fv(glGetUniformLocation(pipelineTexturas3D.shaderProgram, "projection"), 1, GL_TRUE, projection)
        glUniformMatrix4fv(glGetUniformLocation(pipelineTexturas3D.shaderProgram, "view"), 1, GL_TRUE, view)
        pipelineTexturas3D.drawShape(GPUSkyBox)

        # Telling OpenGL to use our shader program
        glUseProgram(pipelineFiguras.shaderProgram)

        bodies.draw(pipelineFiguras, projection, view, theta, viewPos)

        # Desplegar la informacion
        if (info):
            glUseProgram(pipelineTexturas.shaderProgram)
            # Barritas
            i = round(theta)%8
            gpuBarras = es.toGPUShape(bs.createTextureQuad(barritasFrames[i]), GL_REPEAT, GL_NEAREST)
            glUniformMatrix4fv(glGetUniformLocation(pipelineTexturas.shaderProgram, "transform"), 
                    1, GL_TRUE, tr.matmul([tr.translate(.725, .35, 0), tr.uniformScale(0.2)]))
            pipelineTexturas.drawShape(gpuBarras)

            glUniformMatrix4fv(glGetUniformLocation(pipelineTexturas.shaderProgram, "transform"), 
                    1, GL_TRUE, tr.matmul([tr.translate(.6, -0.2, 0),
                    tr.scale(0.67, 0.92, 1),
                    tr.uniformScale(0.7)]))
            pipelineTexturas.drawShape(NombrePlaneta)

            # Base
            glUniformMatrix4fv(glGetUniformLocation(pipelineTexturas.shaderProgram, "transform"), 1, GL_TRUE, tr.matmul([
                tr.translate(0.6, 0, 0),
                tr.scale(2/3,1.24,1),
                tr.uniformScale(0.9)
                ]))
            pipelineTexturas.drawShape(gpuBaseInfo)

        # Once the render is done, buffers are swapped, showing only the complete scene.
        glfw.swap_buffers(window)

    glfw.terminate()
