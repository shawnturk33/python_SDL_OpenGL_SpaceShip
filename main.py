from ctypes import *
from sdl2 import *
from sdl2.keycode import *
from sdl2.sdlmixer import *
from gl import *
from glconstants import *
import globs
from Program import *
from Buffer import *
import random
import traceback
import os.path
from Bullet import *
from math3d import *
from Ship import *
from Background import *
from Texture import *
from Text import *
from Constants import *
from Camera import *
#from Powerups import *
from Mesh import *

def debugCallback( source, msgType, msgId, severity, length,
    message, param ):
    if(msgId == 131204):
        return
    print(msgId,":",message)
    if severity == GL_DEBUG_SEVERITY_HIGH:
        for x in traceback.format_stack():
            print(x,end="")

def makeStars():
    starPoints = []
    for i in range(3*globs.numStars):
        starPoints.append(random.uniform(-1,1))
    buff = Buffer( array.array("f",starPoints) )
    
    tmp = array.array("I",[0])
    glGenVertexArrays(1,tmp)
    starVao = tmp[0]
    glBindVertexArray(starVao)
    buff.bind(GL_ARRAY_BUFFER)
    glEnableVertexAttribArray(0)
    glVertexAttribPointer( 0, 3, GL_FLOAT, False, 3*4, 0 )
    glBindVertexArray(0)
    return starVao


def setup():
    globs.camera = Camera(vec3(0, 0, 1), vec3(0,0,0), vec3(0, 1, 0), 3.14/4, 0.1, 1000)

    globs.pewSound = Mix_LoadWAV(os.path.join( "assets",
        "pew.ogg").encode() )
        
    glEnable(GL_MULTISAMPLE)
    glEnable(GL_DEPTH_TEST)
    glDepthFunc(GL_LEQUAL)
    glClearColor(0,0,0,0)
    globs.starProg = Program("starvs.txt","starfs.txt")
    globs.mainProg = Program("vs.txt","fs.txt")
    globs.shipProg = Program("shipvs.txt","shipfs.txt")

    globs.boss = Mesh(os.path.join("assets", "toothyjaws.obj.mesh"))
    globs.boss.pos = vec3(3.5,0,0)

    globs.starVao = makeStars()
    
    glEnable(GL_PROGRAM_POINT_SIZE)
    globs.player = Ship()
    globs.enemyShips.append(EnemyShip())
    globs.enemySins.append(EnemySin())

    #drawBackground()

    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA,GL_ONE_MINUS_SRC_ALPHA)
    Program.setUniform("screenSize",globs.screenSize)
    Program.updateUniforms()
    globs.charge = Text("Roboto-Black.ttf", 26)
    globs.chargeCount = 0;

    global lightPositions
    #change x*4 to suit num lights
    lightPositions = array.array("f", [0]*1*4)
    lightColors = array.array("f", [0]*1*4)
    idx = 0
    lightPositions[idx] = 0 #x
    lightPositions[idx+1] = 1 #y
    lightPositions[idx+2] = 1 #z
    lightPositions[idx+3] = 0 #w, 0-directional or 1-positional
    lightColors[idx] = 1.5
    lightColors[idx+1] = 0
    lightColors[idx+2] = 0
    Program.setUniform("lightPositions[0]", lightPositions)
    Program.setUniform("lightColors[0]", lightColors)


def handleEvents(elapsed):
    ev = SDL_Event()
    while 1:
        if not SDL_PollEvent(byref(ev)):
            break
        if ev.type == SDL_QUIT:
            SDL_Quit()
            sys.exit(0)
        elif ev.type == SDL_KEYDOWN:
            k = ev.key.keysym.sym
            globs.keyset.add(k)
            if k == SDLK_q:
                SDL_Quit()
                sys.exit(0)
        elif ev.type == SDL_KEYUP:
            k = ev.key.keysym.sym
            globs.keyset.discard(k)
            #if the spacebar has just been released, spawn
            #a bullet
            if k == SDLK_SPACE:
                Mix_PlayChannel(-1,globs.pewSound, 0 )
                globs.bullets.append(Bullet(vec3(globs.player.pos.x, globs.player.pos.y, globs.player.pos.z)))
        elif ev.type == SDL_MOUSEBUTTONDOWN:
            print("mouse down:",ev.button.button,ev.button.x,ev.button.y)
        elif ev.type == SDL_MOUSEBUTTONUP:
            print("mouse up:",ev.button.button,ev.button.x,ev.button.y)
        elif ev.type == SDL_MOUSEMOTION:
            pass
            #print("mouse move:",ev.motion.x,ev.motion.y)
    
def update(elapsed):
    
    handleEvents(elapsed)
    '''if globs.camera.coi.x < 2:
        globs.player.pos.x += globs.panSpeed
        globs.camera.strafe(globs.panSpeed, 0, 0)
    elif globs.boss.pos.x > 2.0:
        globs.boss.pos.x -= 0.001'''
    globs.player.update(elapsed)
    globs.camera.lookAt(
        (globs.player.pos - globs.player.facing),
        globs.player.pos,
        globs.player.up)
    #go over each bullet, reducing its remaining life by
    #the time elapsed. If a bullet's life drops to zero or
    #negative, discard it from the array.
    i=0
    while i < len(globs.bullets):
        globs.bullets[i].update(elapsed)
        for en in globs.enemyShips:
            if globs.bullets[i].collidesWith(en):
                en.state = DYING
                globs.bullets[i].state = DEAD
        for en in globs.enemySins:
            if globs.bullets[i].collidesWith(en):
                en.state = DYING
                globs.bullets[i].state = DEAD
        if globs.bullets[i].life < 0:
            #swap bullet i (our dead bullet) with the
            #last bullet in the list. Exception:
            #if i is the index of the final bullet in
            #the list, just drop the bullet
            tmp = globs.bullets.pop()
            if i < len(globs.bullets):
                globs.bullets[i] = tmp
        elif globs.bullets[i].state == DEAD:
            tmp = globs.bullets.pop()
            if i < len(globs.bullets):
                globs.bullets[i] = tmp
        else:
            i+=1

    #if shift is down, TURBO
    if SDLK_LSHIFT in globs.keyset:
        globs.panSpeed = 0.0035
    else:
        globs.panSpeed = 0.0007

    #if spacebar is down, charge the blasters
    if SDLK_SPACE in globs.keyset:
        #go from black -> red relatively slowly
        globs.chargeCount += 0.02*elapsed
        if globs.chargeCount > 100:
            globs.chargeCount = 100
    else:
        #drop from red -> black rather quickly
        globs.chargeCount -= 0.04*elapsed
        if globs.chargeCount < 0:
            globs.chargeCount = 0
    globs.charge.setText(vec2(100,100), str(int(globs.chargeCount)))


    #enemy ships
    i=0
    while  i < len(globs.enemyShips):
        globs.enemyShips[i].update(elapsed)
        if globs.enemyShips[i].pos.x <= -1:
            tmp = globs.enemyShips.pop()
            if i < len(globs.enemyShips):
                globs.enemyShips[i] = tmp
        elif globs.enemyShips[i].state == DEAD:
            tmp = globs.enemyShips  .pop()
            if i < len(globs.enemyShips):
                globs.enemyShips[i] = tmp
        else:
            i+=1
    if len(globs.enemyShips) == 0:
        globs.enemyShips.append(EnemyShip())
    elif globs.enemyShips[len(globs.enemyShips)-1].nextSpawnTime <= 0:
        globs.enemyShips.append(EnemyShip())
    i = 0
    while i < len(globs.enemySins):
        globs.enemySins[i].update(elapsed)
        if globs.enemySins[i].pos.x <= -1:
            tmp = globs.enemySins.pop()
            if i < len(globs.enemySins):
                globs.enemySins[i] = tmp
        elif globs.enemySins[i].state == DEAD:
            tmp = globs.enemySins.pop()
            if i < len(globs.enemySins):
                globs.enemySins[i] = tmp
        else:
            i += 1
    if len(globs.enemySins) == 0:
        globs.enemySins.append(EnemySin())
    elif globs.enemySins[len(globs.enemySins) - 1].nextSpawnTime <= 0:
        globs.enemySins.append(EnemySin())
            
def draw():
    glClearColor(globs.bulletCharge, 0, 0, 0)
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    globs.camera.setUniforms()

    #draw the starfield

    globs.starProg.use()
    glBindVertexArray(globs.starVao)
    glDrawArrays(GL_POINTS,0,globs.numStars)

    # draw the bullets
    globs.mainProg.use()
    for bull in globs.bullets:
        bull.draw()

    #draw the ship
    globs.shipProg.use()
    globs.player.draw()
    globs.boss.drawWithPos()

    #draw enemy ships
    for enemies in globs.enemyShips:
        enemies.draw()
    for sins in globs.enemySins:
        sins.draw()

    globs.charge.draw()


def main():
    SDL_Init(SDL_INIT_VIDEO|SDL_INIT_AUDIO)
    Mix_Init(MIX_INIT_OGG|MIX_INIT_MP3)
    Mix_OpenAudio(22050,MIX_DEFAULT_FORMAT,1,4096)
    SDL_GL_SetAttribute(SDL_GL_CONTEXT_PROFILE_MASK, SDL_GL_CONTEXT_PROFILE_CORE)
    SDL_GL_SetAttribute(SDL_GL_DEPTH_SIZE, 24)
    SDL_GL_SetAttribute(SDL_GL_STENCIL_SIZE, 8)
    SDL_GL_SetAttribute(SDL_GL_CONTEXT_MAJOR_VERSION,4)
    SDL_GL_SetAttribute(SDL_GL_CONTEXT_MINOR_VERSION,3)
    SDL_GL_SetAttribute(SDL_GL_CONTEXT_FLAGS,SDL_GL_CONTEXT_DEBUG_FLAG)
    SDL_GL_SetAttribute(SDL_GL_CONTEXT_PROFILE_MASK, SDL_GL_CONTEXT_PROFILE_CORE)
    SDL_GL_SetAttribute(SDL_GL_MULTISAMPLEBUFFERS,1)
    SDL_GL_SetAttribute(SDL_GL_MULTISAMPLESAMPLES,4)

    screenWidth = 512
    screenHeight = 512
    globs.screenSize = vec4(screenWidth,screenHeight,1/screenWidth,1/screenHeight)
    win = SDL_CreateWindow( b"ETGG",20,20, screenWidth,screenHeight, SDL_WINDOW_OPENGL)
    if not win: 
        print("Could not create window")
        return

    rc = SDL_GL_CreateContext(win)
    if not rc:
        print("Cannot create GL context")
        raise RuntimeError()
        
    glDebugMessageCallback( debugCallback, None )
    
    # Source, type, severity, count, ids, enabled
    #glDebugMessageControl(GL_DONT_CARE, GL_DONT_CARE, GL_DONT_CARE,
    #    0, None, True )
        
    glEnable(GL_DEBUG_OUTPUT_SYNCHRONOUS)
    glEnable(GL_DEBUG_OUTPUT)

    #This was hinted at in class: We can disable some messages
    #selectively. Here, just to show the syntax,
    #we turn off the excessively chatty
    #buffer messages that nVidia drivers like to give
    tmp = array.array("I",[131185])
    glDebugMessageControl(
        GL_DEBUG_SOURCE_API,
        GL_DEBUG_TYPE_OTHER, 
        GL_DONT_CARE,
        1, tmp, 0 )

    setup()
    
    DESIRED_FRAMES_PER_SEC = 60
    DESIRED_SEC_PER_FRAME = 1/DESIRED_FRAMES_PER_SEC
    DESIRED_MSEC_PER_FRAME = int(DESIRED_SEC_PER_FRAME * 1000)
    TICKS_PER_SECOND = SDL_GetPerformanceFrequency()
    UPDATE_QUANTUM_MSEC = 5
    
    lastTicks = SDL_GetPerformanceCounter()
    accumElapsedMsec = 0
    while 1:
        nowTicks = SDL_GetPerformanceCounter()
        elapsedTicks = nowTicks - lastTicks
        lastTicks = nowTicks
        elapsedMsec = int(1000 * elapsedTicks / TICKS_PER_SECOND)
        accumElapsedMsec += elapsedMsec
        while accumElapsedMsec >= UPDATE_QUANTUM_MSEC:
            update(UPDATE_QUANTUM_MSEC)
            accumElapsedMsec -= UPDATE_QUANTUM_MSEC
        draw()
        SDL_GL_SwapWindow(win)
        endTicks = SDL_GetPerformanceCounter()
        frameTicks = endTicks - nowTicks
        frameMsec = int(1000*frameTicks / TICKS_PER_SECOND)
        leftoverMsec = DESIRED_MSEC_PER_FRAME - frameMsec
        if leftoverMsec > 0:
            SDL_Delay(leftoverMsec)
        


main()
