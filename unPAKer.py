import os

# Setup an offset global pointer to keep track of where we're reading
offset=0

def readString(data,length):
    global offset
    # Read a string by reading 'length' bytes from left to right starting from offset
    # Return string and seek the offset pointer to its end.
    return data[offset:(offset:=offset+length)]

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

with open('res.pak','rb+') as f:
    data = f.read()
    readString(data,4) # Skip first 4 bytes for PAK null terminated Header
    dataOffset = readValueLittle(data,4) # Read the data offset value
    readValueLittle(data,4) # Skip fileSize long value
    
    # Make sure there is an empty 'output' directory to populate
    if(os.path.exists('./output')):
        import shutil
        shutil.rmtree('./output')
    os.mkdir('./output')
    
    # Start recursively filling in the output folder
    unpackFolder(data,dataOffset,'./output')