# fyb-blender
 A set of blender assets created for the $yb NFT project.

Install just as you would any other Blender Add-on (via Edit->Preferences->Add-ons).

Once installed you will see a ybNFT top level menu. Select 'Export Collections to GLTFs' to export. This will bring up a file dialog where you can select the folder to export to.

The script currently assumes that each set of swappable components is in a top level collection, i.e.:
```
Scene Collection
    |-- Buildings
    |   |-- bui1
    |-- Awnings
    |   |-- awn1
    |   |-- awn2
    |-- Flanges
    |   |-- fla1
    |   |-- fla2
```
etc.

All combinations of the items in the sets will be exported to a file with the same name as the blender file + a 3 digit index, (e.g. crescent_001.glb).
