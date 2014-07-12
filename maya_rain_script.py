
import maya.cmds as cmds
import random

""" Project 3 Script

    Script coded up by Iheanyi Ekechukwu, enjoy it!

    Creates a plane that will add rain to the entire environment

"""

class ProjectLayout(object):

    def __init__(self):
        self.width = 10
        self.height = 10

    def reset_environment(self, *args):

        cmds.select(all=True)
        cmds.delete()
        print "Environment has been reset!"

    def show(self):
        self.createGUI()

    def createGUI(self):

        if cmds.window("scriptWindow", exists=True):
            cmds.deleteUI("scriptWindow")

        # Create the window, awwww yiss
        self.window = cmds.window("scriptWindow", title="Iheanyi Ekechukwu Rain Generator Script", wh=(500,270), sizeable=True)

        self.layout = cmds.columnLayout()

        # Maybe let the user designate their surface by typing it in? Awesome.
        all_selected = cmds.ls(selection=True)

        # Get currently selected surface, should be a polygon plane or surface
        if len(all_selected):
            self.selected_surface = all_selected[0]

        else:

            print "Error: Nothing is selected!"

        # Parameters for the GUI include
        # (1) Rain Velocity
        # (2) Resilience/bounciness of the ground

        self.rain_rate = cmds.floatSliderGrp(minValue=1, maxValue = 300, value=100, field=1, label="Rain Rate",step=1)
        self.rain_speed = cmds.floatSliderGrp(minValue=1,maxValue=20,precision=2, value=1.0, field=1, label="Rain Velocity", step=0.1)
        self.surface_resilience = cmds.floatSliderGrp(minValue=0.1, maxValue=0.5, precision=2, value=0.35, field=1, label="Surface Resilience", step=0.01)
        self.turbulence_magnitude = cmds.floatSliderGrp(minValue=5, maxValue=10, precision=1, value=10, field=1, label="Turbulence Magnitude", step=1)
        self.vortex_magnitude = cmds.floatSliderGrp(minValue=5, maxValue=25, value=5, field=1, label="Vortex Magnitude", step=1)


        # Create Rain Field button
        self.rainButton = cmds.button(label='Create Rain Surface', command=self.create_rain)
        self.resetButon = cmds.button(label="Reset Environment", command=self.reset_environment)

        cmds.showWindow(self.window)

    def get_float_value(self, field):
        return cmds.floatSliderGrp(field, q=True, value=True)

    def get_int_value(self, field):
        return cmds.intSliderGrp(field, q=True, value=True)

    def create_rain(self, *args):
        # Create the initial rain surface
        rainSurface = cmds.polyPlane(n="rainSurface", sx=10, sy=10, width=10, height=10)
        cmds.move(10, "rainSurface", y=True)

        # Create the emitter and particles
        rate = self.get_float_value(self.rain_rate)
        _emitter = cmds.emitter(type='omni', r=rate, sro=False)
        emitterName = _emitter[1]
        particleName, particleShape = cmds.particle()

        cmds.select(emitterName)
        emitterConnect = cmds.connectDynamic(particleName, em=emitterName)
        cmds.setAttr(emitterName+".emitterType", 2)

        # Set particle attributes
        cmds.setAttr(particleShape+".lifespanMode", 2)
        cmds.setAttr(particleShape+".lifespanRandom", 5)

        # Select particle for gravity field creation
        cmds.select(particleName)

        _gravity = cmds.gravity(pos=(0,0,0), m=9.8)
        #print _gravity
        gravityName = _gravity[0]

        gravityConnect = cmds.connectDynamic(particleName, f=gravityName)

        # Change particle render type
        cmds.setAttr(particleShape + ".particleRenderType", 6)

        # Create turbulence field
        cmds.select(particleName)
        _turbulence = cmds.turbulence()
        turbulenceName = _turbulence[1]
        cmds.connectDynamic(particleShape, f=turbulenceName)
        turb_magnitude = self.get_float_value(self.turbulence_magnitude)
        cmds.setAttr(turbulenceName+".magnitude", turb_magnitude)
        cmds.setAttr(turbulenceName+".attenuation", 0) # Attenuation at 0 for
        cmds.setAttr(turbulenceName+".frequency", 50)

        # Create vortex field
        cmds.select(particleName)
        vortex = cmds.vortex()
        vortexName = vortex[1]
        vortexConnect = cmds.connectDynamic(particleShape,f=vortexName)

        vort_magnitude = self.get_float_value(self.vortex_magnitude)
        print vort_magnitude

        # Update Vortex Attributes
        cmds.setAttr(vortexName+".magnitude",  vort_magnitude)

        # Make raindrops past the bounds of the surface plane
        cmds.setAttr(emitterName+".minDistance", 1)
        cmds.setAttr(emitterName+".maxDistance", 1)

        # Set raindrops speed
        cmds.setAttr(emitterName+".speedRandom", 0.9)
        cmds.setAttr(emitterName+".tangentSpeed", 1.5)

        wind_speed = self.get_float_value(self.rain_speed)
        cmds.setAttr(emitterName+".speed", wind_speed)

        print "Raindrops speed added."
        # Create surface for collisions (should be selected in the beginning, if not, a new surface will be created)
        #if self.selected_surface is None:
        groundName, groundShape = cmds.polyPlane(n="groundSurface", sx=10, sy=10, width=25, height=25)

        # Set resilience
        resilience = self.get_float_value(self.surface_resilience)
        cmds.select(particleName, r=True)
        cmds.select(groundName, add=True)
        cmds.collision(groundName, particleName, r=resilience)
        cmds.connectDynamic(particleName, c=groundName)
        print "Collisions added."

        # Split the raindrops on collision
        splitName, splitShape = cmds.particle(inherit=0.5, name="splitParticle")
        #print splitName, splitShape

        cmds.event(particleName, split=3, t=splitShape, spread=0.5, random=False)
        cmds.setAttr(splitShape+".inheritFactor", 0.5)
        print "Raindrop splits added."

        # Add the gravity field to newly split particles
        cmds.select(gravityName, r=True)
        cmds.select(splitShape, add=True)
        cmds.connectDynamic(splitShape, f=gravityName)
        print "Gravity field added."

""" Commands:
    polyPlane -w 1 -h 1 -sx 10 -sy 10 -ax 0 1 0 -cuv 2 -ch 1;
    # Move plane upwards. Also, change emitter to surface?
    emitter -type omni -r 100 -sro 0 -nuv 0 -cye none -cyi 1 -spd 1 -srn 0 -nsp 1 -tsp 0 -mxd 0 -mnd 0 -dx 1 -dy 0 -dz 0 -sp 0
    particle;
    connectDynamic -em emitter1 particle1;
    setAttr "emitter1.emitterType" 2;
    setAttr "particleShape1.lifespanMode" 2;
    setAttr "particleShape1.lifespanRandom" 5;
    select -r particle1 ;
    gravity -pos 0 0 0 -m 9.8 -att 0 -dx 0 -dy -1 -dz 0  -mxd -1  -vsh none -vex 0 -vof 0 0 0 -vsw 360 -tsr 0.5 ;
    connectDynamic -f gravityField1  particle1;
    setAttr "particleShape1.particleRenderType" 6;
    setAttr "particleShape1.particleRenderType" 6;

    # Create turbulence field
    turbulence -pos 0 0 0 -m 5 -att 1 -f 1 -phaseX 0 -phaseY 0 -phaseZ 0 -noiseLevel 0 -noiseRatio 0.707  -mxd -1  -vsh none -vex 0 -vof 0 0 0 -vsw 360 -tsr 0.5 ;
    connectDynamic -f turbulenceField1  particleShape1;
    setAttr "turbulenceField1.magnitude" 10;
    setAttr "turbulenceField1.frequency" 50;

    # Create vortex field
    vortex -pos 0 0 0 -m 5 -att 1 -ax 0 -ay 1 -az 0  -mxd -1  -vsh none -vex 0 -vof 0 0 0 -vsw 360 -tsr 0.5 ;
    connectDynamic -f vortexField1  particleShape1;
    setAttr "vortexField1.magnitude" 5;
    setAttr "vortexField1.attenuation" 0.5;

    # Control raindrops speed
    setAttr "emitter1.minDistance" 10;
    setAttr "emitter1.maxDistance" 10;
    setAttr "emitter1.speedRandom" 0.9;
    setAttr "emitter1.tangentSpeed" 1.5;
    setAttr "emitter1.speed" 1;

    # Set collision factor
    collision -r 0.35 -f 0 -o 0.01  pPlane2;
    connectDynamic -c pPlane2  particle1;
    setAttr "geoConnector2.resilience" 0.35;    # Resilience lowers the bounciness of the rain

    # Split raindrops on collide
    particle -i 1.0 ;
    setAttr particleShape2.inheritFactor 0.5;
    event -split 3 -target particleShape2 -spread 0.5 -random 0 -count 0 particle1;

    # Add gravity field to new raindrops
    select -r gravityField1 ;
    select -add particleShape2 ;
    connectDynamic -f gravityField1 particle2; ;





"""

layout = ProjectLayout()
layout.show()
