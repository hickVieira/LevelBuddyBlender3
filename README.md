# Level Buddy for Blender 3.0

**Level Buddy** is a Blender add-on originally written by Matt Lucas.

[old version available on itch.io](https://matt-lucas.itch.io/level-buddy).

## Features
- Doom-inspired sector-based level editor
- Sectors can have up to 3 materials: floor + wall + ceiling
- '3D' Sectors (behave like brushes but are auto-uv)
- Brushes (Add + Subtract, manual-uv)
- Auto texture
- Custom material scale (per sector face)

## Notes
- TextureBuddy no longer exists (got merged to main file)
- Addon still has some bugs
- Yes I removed some old features
- But I also added some better features
- Haven't tested everything out yet
- Give feedback and bug reports

## Installing
- Download repo and unzip
- Blender -> Edit -> Preferences -> Addons -> Install -> Select LevelBuddy.py
- Enable the addon
- Make sure you delete/remove old versions

## State of the Code
Overall the code is pretty bad all around, I have done my best to keep it bug free and readable. Honestly, this addon needs total rewrite, it's got to a point where it can no longer scale without causing bugs and pain.

Also, no offense but, Python is a really ugly language, no matter what I do, the code is just ugly and hard to read. The Blender API doesn't help either, it's just a gigantic mess full of gotachas at every step you take... worst API I have touched so far.

## License
This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
