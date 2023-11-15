# Instructions to work with the code
In models, a global iterator is created to avoid issues with numbering clashes. It is now global and only accepts 

## Python version
Originally made for Python 3.5. Currently, 3.8 is used because it's the oldest still available version.
requirements.txt has been updated on the go 

## Packages

### VLC
Newest VLC version is downloaded, if Python is 64 then VLC also needs to be 64 bit otherwise it can't use the DLL
Another issue might be that the DLL is busy, so put the "libvlc.dll" DLL in the DLLs directory next to python.exe of used version