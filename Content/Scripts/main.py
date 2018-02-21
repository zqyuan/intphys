import importlib
import json
import os
import random
import sys
import math

import unreal_engine as ue
from unreal_engine.classes import KismetSystemLibrary, GameplayStatics
from unreal_engine import FVector, FRotator
from unreal_engine.classes import PhysicalMaterial, StaticMesh

from actors.object import Object
from actors.camera import Camera
from actors.floor import Floor
from actors.wall import Wall
from actors.walls import Walls
from actors.occluder import Occluder
from tools.tick import Tick

# the default screen resolution (in pixels)
width, height = 288, 288

class Main:    
    def init_random_seed(self):
        # init random number generator with a seed
        try:
            seed = os.environ['INTPHYS_SEED']
        except KeyError:
            seed = None

        ue.log('init random numbers generator{}'.format(
            '' if seed is None else ', seed is {}'.format(seed)))

        random.seed(seed)

    def init_resolution(self):
        try:
            resolution = os.environ['INTPHYS_RESOLUTION']
        except KeyError:
            resolution = str(width) + 'x' + str(height)
            ue.log('INTPHYS_RESOLUTION not defined, using default')

        ue.log('set screen resolution to {}'.format(resolution))
        KismetSystemLibrary.ExecuteConsoleCommand(
            self.uobject.get_world(),
            'r.SetRes {}'.format(resolution))

    def init_configuration(self):
        try:
            json_file = os.environ['INTPHYS_CONFIG']
        except KeyError:
            self.exit_ue(
                'fatal error, INTPHYS_CONFIG not defined, exiting')
        ue.log('loading configuration from {}'.format(json_file))

        try:
            output_dir = os.environ['INTPHYS_DATADIR']
        except KeyError:
            self.exit_ue(
                'fatal error, INTPHYS_DATADIR not defined, exiting')
        ue.log('writing data to {}'.format(output_dir))

        config = configuration.Configuration(json_file, output_dir)

        ue.log('generation of {nscenes} scenes ({ntest} for test and '
               '{ntrain} for train), total of {niterations} iterations'.format(
            nscenes=config.nruns_test + config.nruns_train,
            ntest=config.nruns_test,
            ntrain=config.nruns_train,
            niterations=len(config.iterations)))

    # def load_scenes(self):
    #     try:
    #         scenes_file = os.environ['INTPHYS_SCENES']
    #     except KeyError:
    #         self.exit_ue('fatal error, INTPHYS_SCENES not defined, exiting')
    #         return
    #     scene_raw = json.loads(open(scenes_file, 'r').read())

    def exit_ue(self, message=None):
        """Quit the game, optionally displaying an error message"""
        if message:
            ue.log_error(message)
        KismetSystemLibrary.QuitGame(self.world)

    def begin_play(self):
        self.world = self.uobject.get_world()
        ue.log('Raising up new world {}'.format(self.world.get_name()))

        # init the seed for random parameters generation
        self.init_random_seed()

        # init the rendering resolution
        self.init_resolution()

        # spawn the camera
        self.from_above = Camera(self.world, FVector(0, 0, 5000), FRotator(0, -90, 0))
        #self.front = Camera(self.world, FVector(-3000, 0, 100), FRotator(0, 0, 0))
        #self.back = Camera(self.world, FVector(1500, 0, 100), FRotator(0, 0, 180))
        #self.left = Camera(self.world, FVector(-1500, -1500, 100), FRotator(0, 0, 90))
        #self.right = Camera(self.world, FVector(1500, 1500, 100), FRotator(0, 0, 270))
        #self.perspective = Camera(self.world, FVector(-2000, 0, 2000), FRotator(0, -45, 0))
        #self.random_camera = Camera(self.world)
        # spawn an actor
        self.floor = Floor(self.world)#, "/Game/Materials/Floor/M_Ground_Gravel")
        # La ligne ci-dessous parvient load un PhysicalMaterial. Reste plus qu'à l'appliquer sur un material/mesh/actor
        self.object = Object(self.world, Object.shape['Sphere'], FVector(0, 0, 900), FRotator(0, 0, 45), FVector(1, 1, 1), "/Game/Materials/Object/BlackMaterial", 1, FVector(10000000, 0, 0))
        phys = ue.load_object(PhysicalMaterial, "/Game/Materials/PhysicalMaterials/Default")
        actual = self.object.get_material().GetPhysicalMaterial()
        actual = phys
        actual2 = self.floor.get_material().GetPhysicalMaterial()
        actual2 = phys
        
        #self.object2 = Object(self.world, Object.shape['Cube'], FVector(-1000, 0, 150), FRotator(0, 0, 45), FVector(1, 1, 1), "/Game/Materials/Object/GreenMaterial")
        #self.wall_front = Wall(self.world, 'Front')
        #self.wall_left = Wall(self.world, 'Left')
        #self.wall_right = Wall(self.world, 'Right')
        #self.occluder = Occluder(self.world, FVector(500, 0, 0), FRotator(0, 0, 0), FVector(5, 5, 5), "/Game/Materials/Object/GreenMaterial", 1)
        #self.walls = Walls(self.world)
        #self.wall_front = Wall(self.world)
        #self.ticker = Tick()
        #self.ticker.add_hook(self.screenshot.capture, 'slow')
        #self.ticker.add_hook(self.screenshot.save, 'final')
        #self.ticker.add_hook(self.occluder.move(), 'slow')
        #self.ticker.add_hook(self.exit_ue, 'final')
        # run the scene
        #self.ticker.run()
        self.count = 0

    def tick(self, dt):
        self.count = self.count + 1
        if (self.count > 200 and self.count < 210):
            self.object.play_force()
            print("apply_force")
        if (self.count == 300):
            #self.object.__del__()
            self.object.actor_destroy()
        if (self.count == 100):
            self.object.set_material("/Game/Materials/Object/GreenMaterial")
            self.object.set_mesh_str("/Engine/EngineMeshes/Cube.Cube")
            #self.object.set_hidden()
            #self.object.set_scale(FVector(10, 10, 10))
        #self.ticker.tick(dt)
        #self.occluder.move()

