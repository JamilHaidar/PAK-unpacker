# Creating a PAK extractor

For the "Evolution's Parable" game, I unpack the "Evoland" res.pack file into all of its assets including graphics and audio.

---
# Acknowledgement and Background

This short game was inspired by a much more polished game called "Evoland". I had already played both Evoland and Evoland 2. For my Game Programming course I had to create a short game, and I thought I'd recreate something close to it.

# Assets
I needed sprites for characters, animation, objects, etc. I also needed tilemaps and other graphics. So since this was just a demo project, I decided to get all my assets from the game I based my short game on.
I opened the Evoland game .apk file and looked around for a folde that could contain game assets. Instead, I found a PAK file named "res.pak". It was large enough for me to suspect it contained all game assets.
According to the Quake Wiki website:
>It is an exceedingly simple uncompressed archive format which preserves file paths and that's about it

So .PAK files are uncompressed. We just have to know how to extract them. I looked up the format and it's pretty simple. However, it would seem that this file doesn't follow the format Quake Wiki provides. I messed around with the bytes and came to an understanding of the current res.pak format.

>The file is in little-endian format.
ID: 4 byte string > null terminated 'PAK' string</br>
DataOffset: 4 byte integer value > The offset (from the beginning of the pak file) to the beginning of this file's contents.<br/>
FileSize: 4 byte integer value > The size of this file.<br/><br/>
Here is where the format strays from the original format. The structure is now in the form of:<br/>
NameLength: 1 byte value > The number of bytes the file/folder name is.<br/>
Name: NameLength byte string > The file/folder name.<br/>
Type: 1 byte value > If type is 0 then the path is a file. If type is 1 then the path is a folder.<br/><br/>

    If type is 0 (if file):
        Offset: 4 byte value > offset to be added to the DataOffset value to get this file's data
        Size: 4 byte value > size of the file in bytes
        Dummy: 4 byte value: Not sure what this represents. It did not affect unpacking the data.
    If type is 1 (if folder):
        NumSubdir: 4 byte value > Number of subdirs/files within this folder 

Now I'm done figuring out how the .PAK file works. Since I already coded a Java program that extracts images from the MNIST dataset, I thought I'd use Python this time. I wrote a Python script that would automatically decompress and unpack all folders and files recursively.

First to read a string:

    def readString(data,length):
        global offset
        # Read a string by reading 'length' bytes from left to right starting from offset
        # Return string and seek the offset pointer to its end.
        return data[offset:(offset:=offset+length)]
Then to read an n byte value in little endian:

    def readValueLittle(data,length):
        global offset
        # Read the last byte (reading from right to left)
        res = data[offset+length-1]
        
        # Create an array of all bytes excluding the last byte and then reverse it
        # Then for every byte, logic shift left the current result by 8 bits(1 byte) and OR it with the read byte 
        for byte in data[offset:offset+length-1][::-1]:res = (res<<8)|byte
        
        # Seek the offset pointer to the end of the read value.
        offset+=length
        return res

Now the recursive unpacking function:

    def unpackFolder(data,dataOffset,parent):
        
        # Read the length of folder/file name in bytes
        nameLen = readValueLittle(data,1)
        
        # Read the name of the file/folder
        path=readString(data,nameLen)
        
        # Get the type of path. 
        # If type is 0, path is a file.
        # If type is 1, path is a folder.
        mType = readValueLittle(data,1)
    
        if mType==0:
            # Get the offset for file data and add it to the dataOffset constant
            mOffset = readValueLittle(data,4) + dataOffset
            # Get the size of the file in bytes
            size = readValueLittle(data,4)
            # Skip not needed data
            dummy = readValueLittle(data,4) # End of File
            
            # Create a file to be populated by a byte array
            with open(parent+path.decode(),'w+b') as f:
                # Dump data onto file
                f.write(data[mOffset:mOffset+size])
        elif mType==1:
            # Get the number of subdirectories/files within this folder
            numEntry = readValueLittle(data,4)
            # The first folder has no name (root folder) so skip it
            if(path.decode()!=''):
                os.mkdir(parent+path.decode()+'/')
            # Recursively unpack every path within current folder
            for i in range(numEntry):
                unpackFolder(data,dataOffset,parent+path.decode()+'/')
And finally, the main function:

    with open('res.pak','rb+') as f:
        data = f.read()
        readString(data,4) # Skip first 4 bytes for PAK null terminated Header
        dataOffset = readValueLittle(data,4) # Read the data offset value
        readValueLittle(data,4) # Skip fileSize value
        
        # Make sure there is an empty 'output' directory to populate
        if(os.path.exists('./output')):
            import shutil
            shutil.rmtree('./output')
        os.mkdir('./output')
        
        # Start recursively filling in the output folder
        unpackFolder(data,dataOffset,'./output')
---
# Final Note
I have included the Python script and res.pak file in this repo. If you're interested in understanding how all the bytes fit together, I urge you to download both files and try to run the script. To view the res.pak binary, I opened the file in Sublime Text and toggled the HexViewer package I installed for Sublime Text.
