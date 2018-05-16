import random
import os
from unreal_engine.classes import Friction
import importlib
from actors.parameters import SkySphereParams, FloorParams
from actors.parameters import LightParams, WallsParams, CameraParams
from unreal_engine import FVector, FRotator
from tools.materials import get_random_material


class SandBox:
    def __init__(self, world, saver=None, is_occluded=False,
                 movement='static'):
        super().__init__(world, saver)
        self.generate_parameters()
        self.world = world
        self.params = {}
        self.saver = saver
        self.generate_parameters()
        self.actors = None
        self.run = 0
        self.last_locations = []
        self.status_header = {
                'name': self.name,
                'type': 'test',
                'is_possible': True if 'Trai' in type(self).__name__ else False
                }

    @property
    def name(self):
        return 'SandBox'

    def generate_parameters(self):
        self.params['Camera'] = CameraParams(
                location=FVector(0, 0, 200),
                rotation=FRotator(0, 0, 0))
        self.params['SkySphere'] = SkySphereParams()
        self.params['Floor'] = FloorParams(
                material=get_random_material('Floor'))
        self.params['Light'] = LightParams(
                type='SkyLight')
        prob_walls = 1  # no walls to avoid luminosity problems
        if random.uniform(0, 1) <= prob_walls:
            self.params['Walls'] = WallsParams(
                    material=get_random_material('Wall'),
                    height=random.uniform(1, 5),
                    length=random.uniform(3000, 5000),
                    depth=random.uniform(1500, 3000))

    def play_run(self):
        self.spawn_actors()
        self.saver.update(self.actors)

    def spawn_actors(self):
        self.actors = {}
        for actor, actor_params in self.params.items():
            if ('magic' in actor):
                continue
            elif ('skysphere' in actor.lower()):
                class_name = 'SkySphere'
            else:
                class_name = actor.split('_')[0].title()
            # dynamically import and instantiate
            # the class corresponding to the actor
            module_path = "actors.{}".format(actor.lower().split('_')[0])
            module = importlib.import_module(module_path)
            self.actors[actor] = getattr(module, class_name)(
                world=self.world, params=actor_params)
            if 'object' in actor.lower():
                # if 'Sphere' in self.actors[actor].mesh_str:
                #    Friction.SetMassScale(self.actors[actor].get_mesh(), 1)
                if 'Cube' in self.actors[actor].mesh_str:
                    Friction.SetMassScale(self.actors[actor].get_mesh(),
                                          0.6155297517867)
                elif 'Cone' in self.actors[actor].mesh_str:
                    Friction.SetMassScale(self.actors[actor].get_mesh(),
                                          1.6962973279499)

    def reset_actors(self):
        if self.actors is None:
            return
        for name, actor in self.actors.items():
            if 'object' in name.lower() or 'occluder' in name.lower():
                actor.reset(self.params[name])

    def del_actors(self):
        if self.actors is not None:
            for actor_name, actor in self.actors.items():
                actor.actor_destroy()
            self.actors = None

    def stop_run(self, scene_index):
        if not self.saver.is_dry_mode:
            self.saver.save(self.get_scene_subdir(scene_index))
            # reset actors if it is the last run
            self.saver.reset(True if self.run == 1 else False)
        self.run += 1
        return True

    def get_scene_subdir(self, scene_index):
        # build the scene sub-directory name, for exemple
        # '027_test_O1/3' or '028_train_O1'
        idx = scene_index + 1
        padded_idx = '0{}'.format(idx)
        scene_name = (
            padded_idx + '_' +
            ('train' if 'Train' in type(self).__name__ else 'test') + '_' +
            self.name)
        out = os.path.join(self.saver.output_dir, scene_name)
        if 'Test' in type(self).__name__:
            # 1, 2, 3 and 4 subdirectories for test scenes
            run_idx = self.run + 1
            out = os.path.join(out, str(run_idx))
        return out

    def tick(self):
        if self.actors is not None:
            for actor_name, actor in self.actors.items():
                if 'object' in actor_name or 'occluder' in actor_name:
                    actor.move()

    def capture(self):
        ignored_actors = []
        self.saver.capture(ignored_actors, self.status_header,
                           self.get_status())

    def set_magic_tick(self):
        self.params['magic']['tick'] = 25

    def is_over(self):
        return True


SandBoxTrain = SandBox
SandBoxTest = SandBox
