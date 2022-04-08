# Blender WMO import/export addon
Actually this addon is much more than a usual import/export Blender plugin. Besides core functionality of importing and saving edited WMOs, this addon is also a powerful editor supporting nearly all features of World of Warcraft World Model Object (WMO) files. Written in Python using Blender API.

# DEPRECATED!!!
This repository is deprecated in favor of WoW Blender Studio, a more recent continuation of this addon. https://gitlab.com/skarnproject/blender-wow-studio.
WoW Blender Studio is intended to be used with the most recent versions of Blender. The code on **this** repository only supports Blender 2.79b. No support for this version will be given.

# What is World Model Object?
World Model Object or just WMO is a special compound 3D structure used in the game World of Warcraft for making buildings, dungeons and other big complicated 3D objects. It does not only contain traditional 3D model parts as geometry, UV maps, materials and so on; but it does also support features like liquids, complex lighting system, portal culling system and much more.

# WARNING: The code on this repo is work in progress
This repo only exists for development purposes, not for deploying versions to users. File corruption may occur if you by chance pull some unfinished or broken code. The last "stable" verson is available on http://model-changing.net (Model Changing Network) and is supplied with how-to documentation. 

# Donation
The provided software is available completely free of charge, however if you want to support me, here is my PayPal account: https://www.paypal.me/sergeishumakov2015

# Currently supported features
- Geometry editing. The script allows the user to edit WMO geometry, UVmaps and create outdoor and indor groups.
- Material editing. The addon supports all features of WoW material system. A user is able to create materials, set textures, change used shaders, blending modes, flags etc.
- Vertex colors. 
- WMO portals. The script addon supports all features of WMO portals, except antiportal creation.
- WMO fogs.
- WMO liquids. The liquid system is fully supported including UV editing for lava and tile flags.
- Collision.
- Render batches.
- Lightmaps.
- Quick WMO panel. A UI interface aimed to ease the process of WMO creation.

# Credits
Developers:
- happyhack (original addon version)
- Miton (portals and other contributions)
- Skarn (current developer)
- Supora (initial vertex color import/export support)
- p620 (multiple help with complicated coding tasks)

Testers:
- Balkron
- Amaroth
- Supora
- Kadzhamit
- gratural
- Vellear
- intra
& others.

Special thanks to Deamon and fallenoak for information on batches and portals and all other http://wowdev.wiki contributors.

# Planned features
- Transport convex volume planes
- Doodadset editing. (If the m2 plugin arrives by that time)

# Installation and usage:
http://www.model-changing.net/files/file/56-wmo-importexport-blender-scripts-updated-25022016/ (relevant to last officially released version)
