import re
import os
import bpy
import time
import subprocess
from . import mpyq
from .mpyq import *

class WoWFileData():
    def __init__(self, wow_path, blp_path):
        self.wow_path = wow_path
        self.files = self.open_game_resources(self.wow_path)
        self.converter = BLPConverter(blp_path) if blp_path else None

    def __del__(self):
        print("\nUnloading game data...")

    def read_file(self, filepath, force_decompress=False):
        """ Read the latest version of the file from loaded archives and directories. """
        file = None
        for pair in self.files:
            storage = pair[0]
            type = pair[1]

            if type:
                file = storage.read_file(filepath, force_decompress)
            else:
                abs_path = os.path.join(storage, filepath)
                if os.path.exists(abs_path) and os.path.isfile(abs_path):
                    file = open(abs_path, "rb").read()
            if file:
                return file

        print("\nRequested file <<" + filepath + ">> not found in MPQ archives.")
        return None

    def extract_files(self, dir, filenames, force_decompress=False):
        """ Read the latest version of the files from loaded archives and directories and
        extract them to provided working directory. """

        result = False
        for filename in filenames:
            file = self.read_file(filename, force_decompress)
            if not file:
                continue

            abs_path = os.path.join(dir, filename)
            local_dir = os.path.dirname(abs_path)

            if not os.path.exists(local_dir):
                os.makedirs(local_dir)

            f = open(abs_path, 'wb')
            f.write(file or b'')
            f.close()

            result = True

        return result

    def extract_textures_as_png(self, dir, filenames, force_decompress=False):
        """ Read the latest version of the texture files from loaded archives and directories and
        extract them to current working directory as PNG images. """
        if self.converter:
            blp_paths = []

            for filename in filenames:
                abs_path = os.path.join(dir, filename)
                if not os.path.exists(os.path.splitext(abs_path)[0] + ".png"):
                    file = self.read_file(filename, force_decompress)
                    if not file:
                        continue
                    local_dir = os.path.dirname(abs_path)

                    if not os.path.exists(local_dir):
                        os.makedirs(local_dir)

                    f = open(abs_path, 'wb')
                    f.write(file or b'')
                    f.close()

                    blp_paths.append(abs_path)

            self.converter.convert(blp_paths)

            for blp_path in blp_paths:
                os.remove(blp_path)

        else:
            print("\nPNG texture extraction failed. No converter executable specified or found")

    @staticmethod
    def list_game_data_paths(path):
        """List files and directories in a directory that correspond to WoW patch naming rules."""
        dir_files = []
        for f in os.listdir(path):
            cur_path = os.path.join(path, f)

            if os.path.isfile(cur_path) \
            and os.path.splitext(f)[1].lower() == '.mpq' \
            or not os.path.isfile(cur_path) \
            and re.match(r'patch-\w.mpq', f.lower()):
                dir_files.append(cur_path)

        map(lambda x: x.lower(), dir_files)

        dir_files.sort(key=lambda s: os.path.splitext(s)[0])

        return dir_files

    @staticmethod
    def is_wow_path_valid(wow_path):
        """Check if a given path is a path to WoW client."""
        if wow_path and os.path.exists(os.path.join(wow_path, "Wow.exe")):
            return True

        return False

    @staticmethod
    def open_game_resources(wow_path):
        """Open game resources and store links to them in memory"""

        print("\nProcessing available game resources of client: " + wow_path)
        start_time = time.time()

        if WoWFileData.is_wow_path_valid(wow_path):
            data_packages = WoWFileData.list_game_data_paths(os.path.join(wow_path, "Data\\"))
            resource_map = []

            for package in data_packages:
                if os.path.isfile(package):
                    resource_map.append((mpyq.MPQArchive(package, listfile=False), True))
                    print("\nLoaded MPQ: " + os.path.basename(package))
                else:
                    resource_map.append((package, False))
                    print("\nLoaded folder patch: " + os.path.basename(package))

            print("\nDone initializing data packages.")
            print("Total loading time: ", time.strftime("%M minutes %S seconds", time.gmtime(time.time() - start_time)))
            return resource_map
        else:
            print("\nPath to World of Warcraft is empty or invalid. Failed to load game data.")
            return None

class BLPConverter:
    def __init__(self, toolPath):
        if os.path.exists(toolPath):
            self.toolPath = toolPath
            print("\nFound BLP Converter executable: " + toolPath)
        else:
            raise Exception("\nNo BLPConverter found at given path: " + toolPath)

    def convert(self, filepaths, alwaysReplace = False):
        init_length = len(self.toolPath) + 4
        init_command = self.toolPath
        cur_length = 0
        cur_args = []

        for filepath in filepaths:
            if alwaysReplace or not os.path.exists(os.path.splitext(filepath)[0] + ".png"):
                length = len(filepath)

                if 2047 - (cur_length + init_length) < length + 2:
                    final_command = [init_command, '/M']
                    final_command.extend(cur_args)
                    if subprocess.call(final_command):
                        raise Exception("\nBLP convertion failed.")
                    cur_length = 0
                    cur_args = []

                cur_length += length + 3
                cur_args.append(filepath)

        if cur_length:
            final_command = [init_command, '/M']
            final_command.extend(cur_args)
            if subprocess.call(final_command):
                raise Exception("\nBLP convertion failed.")


class WOW_FILESYSTEM_LOAD_OP(bpy.types.Operator):
    bl_idname = 'scene.load_wow_filesystem'
    bl_label = 'Load WoW filesystem'
    bl_description = 'Establish connection to World of Warcraft client files'
    bl_options = {'REGISTER'}

    def execute(self, context):

        if hasattr(bpy, "wow_game_data"):

            delattr(bpy, "wow_game_data")
            self.report({'INFO'}, "WoW game data is unloaded.")

        else:

            preferences = bpy.context.user_preferences.addons.get("io_scene_wmo").preferences

            bpy.wow_game_data = WoWFileData(preferences.wow_path, preferences.blp_path)

            if not bpy.wow_game_data.files:
                self.report({'ERROR'}, "WoW game data is not loaded. Check settings.")
                return {'CANCELLED'}

            self.report({'INFO'}, "WoW game data is loaded.")

        return {'FINISHED'}
