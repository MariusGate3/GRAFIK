import pygame as pg
from OpenGL.GL import *
import numpy as np
from OpenGL.GL.shaders import compileProgram, compileShader
import pyrr

class Cube:
    def __init__(self, position, eulers):
        self.position = np.array(position, dtype=np.float32)
        self.eulers = np.array(eulers, dtype=np.float32)

class Light:
    def __init__(self, position, color, strength):
        self.position = np.array(position, dtype=np.float32)
        self.color = np.array(color, dtype=np.float32)
        self.strength = strength
        
class App:

    def __init__(self):
        
        pg.init()
        pg.display.set_mode((640, 480), pg.OPENGL | pg.DOUBLEBUF)
        self.clock = pg.time.Clock()

        glClearColor(0.1, 0.2, 0.2, 1)
        glEnable(GL_BLEND)
        glEnable(GL_DEPTH_TEST)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        self.shader = self.createShader("A2/shaders/vertex.txt", "A2/shaders/fragment.txt")
        glUseProgram(self.shader)
        glUniform1i(glGetUniformLocation(self.shader, "imageTexture"), 0)
        self.cube = Cube(position=[0,0,-3], eulers=[0,0,0])
        self.cubeMesh = CubeMesh()
        self.woodTexture = Material("A2/img/wood.jpeg")

        projection_transform = pyrr.matrix44.create_perspective_projection_matrix(
            fovy=45, aspect=640/480,
            near=0.1, far=10, dtype= np.float32
        )
        glUniformMatrix4fv(
            glGetUniformLocation(self.shader, "projection"), 1, GL_FALSE,
            projection_transform
        )

        self.modelMatrixLocation = glGetUniformLocation(self.shader, "model")

        # Create a light
        self.light = Light(position=[2, 2, 2], color=[1, 1, 1], strength=1.0)
        
        # Get Uniform Locations
        self.modelMatrixLocation = glGetUniformLocation(self.shader, "model")
        self.viewPosLocation = glGetUniformLocation(self.shader, "viewPos")

        self.useTextureLoc = glGetUniformLocation(self.shader, "useTexture")
        self.objectColorLoc = glGetUniformLocation(self.shader, "objectColor")
        
        # Light Uniform Locations (Structs must be located individually)
        self.lightPosLoc = glGetUniformLocation(self.shader, "Light.position")
        self.lightColorLoc = glGetUniformLocation(self.shader, "Light.color")
        self.lightStrengthLoc = glGetUniformLocation(self.shader, "Light.strength")

        self.mainLoop()
    
    def createShader(self, vertexFilepath, fragmentFilepath):

        with open(vertexFilepath, "r") as f:
            vertex_src = f.readlines()
        
        with open(fragmentFilepath, "r") as f:
            fragment_src = f.readlines()
        
        shader = compileProgram(compileShader(vertex_src, GL_VERTEX_SHADER),
                                compileShader(fragment_src, GL_FRAGMENT_SHADER))
        return shader

    def mainLoop(self):
            running = True
            while running:
                # --- 1. RESTORED EVENT HANDLING ---
                for event in pg.event.get():
                    if event.type == pg.QUIT:
                        running = False
                
                # --- 2. RESTORED ROTATION LOGIC ---
                self.cube.eulers[2] += 0.2
                if (self.cube.eulers[2] >= 360):
                    self.cube.eulers[2] -= 360

                # --- 3. RENDERING ---
                glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
                glUseProgram(self.shader)

                # Common Uniforms
                glUniform3f(self.viewPosLocation, 0.0, 0.0, 0.0) 
                glUniform3fv(self.lightPosLoc, 1, self.light.position)
                glUniform3fv(self.lightColorLoc, 1, self.light.color)
                glUniform1f(self.lightStrengthLoc, self.light.strength)
                
                # Update Model Matrix
                model_transform = pyrr.matrix44.create_identity(dtype=np.float32)
                model_transform = pyrr.matrix44.multiply(
                    m1=model_transform, 
                    m2=pyrr.matrix44.create_from_eulers(eulers=np.radians(self.cube.eulers), dtype=np.float32)
                )
                model_transform = pyrr.matrix44.multiply(
                    m1=model_transform, 
                    m2=pyrr.matrix44.create_from_translation(vec=self.cube.position, dtype=np.float32)
                )
                glUniformMatrix4fv(self.modelMatrixLocation, 1, GL_FALSE, model_transform)

                glBindVertexArray(self.cubeMesh.vao)

                # ==========================================================
                # PASS 1: SOLID RED CUBE
                # ==========================================================
                glEnable(GL_POLYGON_OFFSET_FILL)
                glPolygonOffset(1.0, 1.0) 
                glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
                
                # Use Solid Color (Red)
                glUniform1i(self.useTextureLoc, 0) 
                glUniform3f(self.objectColorLoc, 1.0, 0.0, 0.0) 
                
                glDrawArrays(GL_TRIANGLES, 0, self.cubeMesh.vertexCount)
                glDisable(GL_POLYGON_OFFSET_FILL)

                # ==========================================================
                # PASS 2: BLACK WIREFRAME
                # ==========================================================
                glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
                
                # Use Solid Color (Black)
                glUniform1i(self.useTextureLoc, 0)
                glUniform3f(self.objectColorLoc, 0.0, 0.0, 0.0) 
                
                glDrawArrays(GL_TRIANGLES, 0, self.cubeMesh.vertexCount)

                # ==========================================================
                # RESET & FLIP
                # ==========================================================
                glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)

                pg.display.flip()
                self.clock.tick(60)
                
            self.quit()
    
    def quit(self):
        self.cubeMesh.destroy()
        self.woodTexture.destroy()
        glDeleteProgram(self.shader)
        pg.quit()

class CubeMesh:
    def __init__(self):
                            # x, y, z, s, t
        self.vertices = (
                -0.5, -0.5, -0.5, 0, 0, 0, 0, -1,
                -0.5,  0.5, -0.5, 1, 0, 0, 0, -1,
                 0.5,  0.5, -0.5, 1, 1, 0, 0, -1,

                 0.5,  0.5, -0.5, 1, 1, 0, 0, -1,
                 0.5, -0.5, -0.5, 0, 1, 0, 0, -1,
                -0.5, -0.5, -0.5, 0, 0, 0, 0, -1,

                 0.5,  0.5,  0.5, 0, 0, 0, 0,  1,
                -0.5,  0.5,  0.5, 1, 0, 0, 0,  1,
                -0.5, -0.5,  0.5, 1, 1, 0, 0,  1,

                -0.5, -0.5,  0.5, 1, 1, 0, 0,  1,
                 0.5, -0.5,  0.5, 0, 1, 0, 0,  1,
                 0.5,  0.5,  0.5, 0, 0, 0, 0,  1,

                -0.5, -0.5,  0.5, 1, 0, -1, 0,  0,
                -0.5,  0.5,  0.5, 1, 1, -1, 0,  0,
                -0.5,  0.5, -0.5, 0, 1, -1, 0,  0,

                -0.5,  0.5, -0.5, 0, 1, -1, 0,  0,
                -0.5, -0.5, -0.5, 0, 0, -1, 0,  0,
                -0.5, -0.5,  0.5, 1, 0, -1, 0,  0,

                 0.5, -0.5, -0.5, 1, 0, 1, 0,  0,
                 0.5,  0.5, -0.5, 1, 1, 1, 0,  0,
                 0.5,  0.5,  0.5, 0, 1, 1, 0,  0,

                 0.5,  0.5,  0.5, 0, 1, 1, 0,  0,
                 0.5, -0.5,  0.5, 0, 0, 1, 0,  0,
                 0.5, -0.5, -0.5, 1, 0, 1, 0,  0,

                 0.5, -0.5,  0.5, 0, 1, 0, -1,  0,
                -0.5, -0.5,  0.5, 1, 1, 0, -1,  0,
                -0.5, -0.5, -0.5, 1, 0, 0, -1,  0,

                -0.5, -0.5, -0.5, 1, 0, 0, -1,  0,
                 0.5, -0.5, -0.5, 0, 0, 0, -1,  0,
                 0.5, -0.5,  0.5, 0, 1, 0, -1,  0,

                 0.5,  0.5, -0.5, 0, 1, 0, 1,  0,
                -0.5,  0.5, -0.5, 1, 1, 0, 1,  0,
                -0.5,  0.5,  0.5, 1, 0, 0, 1,  0,

                -0.5,  0.5,  0.5, 1, 0, 0, 1,  0,
                 0.5,  0.5,  0.5, 0, 0, 0, 1,  0,
                 0.5,  0.5, -0.5, 0, 1, 0, 1,  0
            )


        self.vertices = np.array(self.vertices, dtype = np.float32)
        self.vertexCount = len(self.vertices) // 8

        self.vao = glGenVertexArrays(1)
        glBindVertexArray(self.vao)
        self.vbo = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
        glBufferData(GL_ARRAY_BUFFER, self.vertices.nbytes, self.vertices, GL_STATIC_DRAW)
        glEnableVertexAttribArray(0)
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 32, ctypes.c_void_p(0))
        glEnableVertexAttribArray(1)
        glVertexAttribPointer(1, 2, GL_FLOAT, GL_FALSE, 32, ctypes.c_void_p(12))
        glEnableVertexAttribArray(2)
        glVertexAttribPointer(2, 3, GL_FLOAT, GL_FALSE, 32, ctypes.c_void_p(20))

    def destroy(self):
        glDeleteVertexArrays(1, (self.vao,))
        glDeleteBuffers(1, (self.vbo,))

class Material:
    def __init__(self, filepath):
        self.texture = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, self.texture)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        image = pg.image.load(filepath).convert_alpha()
        image_width, image_height = image.get_rect().size
        image_data = pg.image.tostring(image, "RGBA")
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, image_width, image_height, 0,
                     GL_RGBA, GL_UNSIGNED_BYTE, image_data)
        glGenerateMipmap(GL_TEXTURE_2D)
    
    def use(self):
        glActiveTexture(GL_TEXTURE0)
        glBindTexture(GL_TEXTURE_2D, self.texture)
    
    def destroy(self):
        glDeleteTextures(1, (self.texture,))



if __name__ == "__main__":
    myApp = App()