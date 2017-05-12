import os, re
from os import listdir
from os.path import isfile, join
import string


RENDER = True
PRINT_DEBUG = True


letters = tuple(string.ascii_letters)

def change(x):
    if x.endswith(letters):
        return float(x[:len(x) -1])
    else:
        return float(x)


def writeToFile(fileHandle, textToWrite, PRINT_DEBUG):
    fileHandle.write(textToWrite)
    
    if PRINT_DEBUG:
        print textToWrite


def HexToByte( hexStr ):
    bytes = []

    hexStr = ''.join( hexStr.split(" ") )

    for i in range(0, len(hexStr), 2):
        bytes.append( chr( int (hexStr[i:i+2], 16 ) ) )

    return ''.join( bytes )

def ByteToHex( byteStr ):
    return ''.join( [ "%02X" % ord( x ) for x in byteStr ] ).strip()


if __name__ == '__main__':
    ############################
    #Step 1: Create output files
    ############################
    logFile = "ImageAnalysisResult.txt"
    fileHandle = open(logFile, 'a+')

    bmpFileOutput = 'bitmapLibrary.txt'    
    fontDataFileOutput = 'fontDataFileOutput.txt'
    fontHeaderFileOutput = 'fontHeaderFileOutput.txt'    
    fontBinFile = 'FontBinaryFile.txt'
    

    
    textToWrite = ""

    #######################################################
    #Step 2: Access the current directory and get all files
    #######################################################
    mypath = os.curdir    
    onlyfiles = [ f for f in listdir(mypath) if isfile(join(mypath,f)) ]
    validFile = "(.*)" + "." + "bmp"

    convertFont = False
    convertImage = True
    

    #If its a font, we need to sort the letters via their filenames
    if convertFont:
        
    
        #Sort!
        sortedFiles = c = []
        for i in onlyfiles:
            match = re.search(r'\.(.*)', i, re.M|re.I)
            if match:
                if match.group() <> '.bmp':
                    break    
                else:
                    #remove '_'
                    i = i.replace('_', '.')
                    #remove '.bmp'
                    i = i.replace('.bmp', '')
                    c.append(i)
    
        sortedFiles = sorted(c, key = lambda k: change(k))
        #print sortedFiles
    
        for i in sortedFiles:
            i = i.replace('.','_') + '.bmp'
            onlyfiles.append(i)    
        #print onlyfiles    

    headerLength = 12   #this variable is used for font parameters (for FT961 FW)
    currentAddress = len(onlyfiles) * headerLength



    
    ################################################
    #Step 3: Retrieve only the bmp files and analyze
    ################################################
    filename = ''
    print onlyfiles
    for filename in onlyfiles:
        if os.path.isfile(filename):
            match = re.search(r'\.(.*)', filename, re.M|re.I)
            if match:
                if match.group() == '.bmp':
                    f = open(filename, 'rb')
        
                    print "\n====================================================="
                    b = f.readlines()
        
                    #1/13/2016: I had observed that some images are clipped off.
                    #The reason is because some images sometimes have multiple arrays of data after f.readlines().
                    #Previously, I was only doing commented below.
                    #b = f.readlines()[0]
                    
                    b = "".join(b)                    
                    #print "\nBYTE  : %s" % b   #'h' is a byte
                    
                    ############################
                    #Step 4: Convert byte to hex
                    ############################
                    h = ByteToHex(b)
                    #print "\nRaw Data in Hex : %s\n" % h

                    ##########################################################################
                    #Step 5: 'h' is a hex but formatted as a string, let's get the damn hexes!
                    ##########################################################################
                    actualImageHex = []
                    tempByte = ''
                    count = 0
                    for i in h:
                        if count < 2:
                            if count == 0:
                                tempByte = ''
                                
                            tempByte += i
                            count += 1
                        else:        
                            #actualImageHex.insert(0, tempByte)
                            actualImageHex.append(tempByte)
                            
                            count = 1
                            tempByte = '' + i


                    ###########################################################################################################################################
                    #Step 6: Due to byte order (endianness) of bitmap: 'h' here is little-endian. The least significant byte is stored first.
                    #Our FW require us to store the bytes in big endian order (most significant byte stored first) so let's reverse it!
                    ###########################################################################################################################################
                    
                    reversedImageHex = list(reversed(actualImageHex))
                    
                    #textToWrite = "\nACTUAL : \n%s" % actualImageHex
                    #print textToWrite                    
                    #textToWrite = "\nREVERSED: \n%s" % reversedImageHex
                    #print textToWrite

                    ###############################################
                    #Step 7: Understand the bytes. Get the headers.
                    ###############################################
                    textToWrite = "\n--- Bitmap Information ---\n"
                    writeToFile(fileHandle, textToWrite, PRINT_DEBUG)
                    textToWrite = "\tFilename : %s\n" % f.name
                    writeToFile(fileHandle, textToWrite, PRINT_DEBUG)        
        
                    bmpIndicator = HexToByte(''.join(reversed(reversedImageHex[-2:])))
                    textToWrite = "\nBMP Indicator : %s\n" % bmpIndicator
                    writeToFile(fileHandle, textToWrite, PRINT_DEBUG)
        
                    bmpFileSize = int(''.join((reversedImageHex[-6:-2])), 16)
                    textToWrite = "\nBMP File Size : %s\n" % bmpFileSize
                    writeToFile(fileHandle, textToWrite, PRINT_DEBUG)
                    
                    startActualImageByteAddress = int(''.join((reversedImageHex[-14:-10])), 16)
                    textToWrite = "\nStart Address of Actual Image : %s\n" % startActualImageByteAddress
                    writeToFile(fileHandle, textToWrite, PRINT_DEBUG)
                    
                    widthInPixels = int(''.join((reversedImageHex[-22:-18])), 16)
                    textToWrite = "\tWidth (pixels) : %s\n" % widthInPixels
                    writeToFile(fileHandle, textToWrite, PRINT_DEBUG)
                    
                    heightInPixels= int(''.join((reversedImageHex[-26:-22])), 16)
                    textToWrite = "\tHeight (pixels) : %s\n" % heightInPixels
                    writeToFile(fileHandle, textToWrite, PRINT_DEBUG)
                    
                    numColorPlanes= int(''.join((reversedImageHex[-28:-26])), 16)
                    textToWrite = "\tNumber of Color Planes : %s\n" % numColorPlanes
                    writeToFile(fileHandle, textToWrite, PRINT_DEBUG)
                    
                    numBitsPerPixel= int(''.join((reversedImageHex[-30:-28])), 16)
                    textToWrite = "\tNumber of Bits per pixel : %s\n" % numBitsPerPixel
                    writeToFile(fileHandle, textToWrite, PRINT_DEBUG)
                    
                    compressionMethod= int(''.join((reversedImageHex[-34:-30])), 16)
                    textToWrite = "\tCompression Method : %s\n" % compressionMethod
                    writeToFile(fileHandle, textToWrite, PRINT_DEBUG)
                    
                    imageSize = int(''.join((reversedImageHex[-38:-34])), 16)
                    textToWrite = "\tImage Size : %s\n" % imageSize
                    writeToFile(fileHandle, textToWrite, PRINT_DEBUG)
                            
                    horizontalResolution = int(''.join((reversedImageHex[-42:-38])), 16)
                    textToWrite = "\tHorizontal Resolution : %s\n" % horizontalResolution
                    writeToFile(fileHandle, textToWrite, PRINT_DEBUG)
                    
                    verticalResolution = int(''.join((reversedImageHex[-46:-42])), 16)
                    textToWrite = "\tVertical Resolution : %s\n" % verticalResolution
                    writeToFile(fileHandle, textToWrite, PRINT_DEBUG)
        
                    numberOfColorsPalette = int(''.join((reversedImageHex[-50:-46])), 16)
                    textToWrite = "\tNumber of Color Palette : %s\n" % numberOfColorsPalette
                    writeToFile(fileHandle, textToWrite, PRINT_DEBUG)
                    
                    numberOfImptColors = int(''.join((reversedImageHex[-54:-50])), 16)
                    textToWrite = "\tNumber of Important Colors : %s\n" % numberOfImptColors
                    writeToFile(fileHandle, textToWrite, PRINT_DEBUG)

                    ##############################
                    #Step 8: GET ACTUAL IMAGE DATA
                    ##############################
                    actualReversedImage = ''.join(actualImageHex[startActualImageByteAddress:])
                    textToWrite = "\nActual Reversed Image data (in hex) : \n%s\n" % actualReversedImage
                    #writeToFile(fileHandle, textToWrite, PRINT_DEBUG)

                    


                    actualUnreversedImage = ''.join(reversedImageHex[:-startActualImageByteAddress])
                    textToWrite = "\nActual Unreversed Image data (in hex) : \n%s\n" % actualUnreversedImage
                    #writeToFile(fileHandle, textToWrite, PRINT_DEBUG)

                    print textToWrite

                    #####################
                    #Step 9: RENDER IMAGE
                    #####################


                    ceiling_factor_8 = 0
            
                    if widthInPixels > 0 and widthInPixels <= 32:     
                        ceiling_factor_8 = 32
                    elif widthInPixels > 32 and widthInPixels <= 64:  
                        ceiling_factor_8 = 64   
                    elif widthInPixels > 64 and widthInPixels <= 128:  
                        ceiling_factor_8 = 128   
                    elif widthInPixels > 128 and widthInPixels <= 256:  
                        ceiling_factor_8 = 256            
                        
                    paddingInPixelsToRemove = ceiling_factor_8 - widthInPixels
            
                    textToWrite = "\nPadding in pixels to remove from actual image : %s\n" % paddingInPixelsToRemove
                    writeToFile(fileHandle, textToWrite, PRINT_DEBUG)            
            
                    #To Make It Divisible By Eight
                    if widthInPixels > 0 and widthInPixels <= 8:     #8 x 1
                        ceiling_factor_8 = 8
                    elif widthInPixels > 8 and widthInPixels <= 16:  #8 x 2
                        ceiling_factor_8 = 16
                    elif widthInPixels > 16 and widthInPixels <= 24: #8 x 3
                        ceiling_factor_8 = 24
                    elif widthInPixels > 24 and widthInPixels <= 32: #8 x 4
                        ceiling_factor_8 = 32
                    elif widthInPixels > 32 and widthInPixels <= 40: #8 x 5
                        ceiling_factor_8 = 40
                    elif widthInPixels > 40 and widthInPixels <= 48: #8 x 6
                        ceiling_factor_8 = 48
                    elif widthInPixels > 48 and widthInPixels <= 56: #8 x 7
                        ceiling_factor_8 = 56
                    elif widthInPixels > 56 and widthInPixels <= 64: #8 x 8
                        ceiling_factor_8 = 64
                    elif widthInPixels > 64 and widthInPixels <= 72: #8 x 9
                        ceiling_factor_8 = 72
                    elif widthInPixels > 72 and widthInPixels <= 80: #8 x 10
                        ceiling_factor_8 = 80
                    elif widthInPixels > 80 and widthInPixels <= 88: #8 x 10
                        ceiling_factor_8 = 88
                    elif widthInPixels > 88 and widthInPixels <= 96: #8 x 10
                        ceiling_factor_8 = 96
                    elif widthInPixels > 96 and widthInPixels <= 104: #8 x 10
                        ceiling_factor_8 = 104
                    elif widthInPixels > 104 and widthInPixels <= 112: #8 x 10
                        ceiling_factor_8 = 112
                    elif widthInPixels > 112 and widthInPixels <= 120: #8 x 10
                        ceiling_factor_8 = 120
                    elif widthInPixels > 120 and widthInPixels <= 128: #8 x 10
                        ceiling_factor_8 = 128
            
                    paddingInPixelsToAdd = ceiling_factor_8 - widthInPixels
            
                    #textToWrite = "\nPadding in pixels to add for FT962 format: %s\n" % paddingInPixelsToAdd
                    #writeToFile(fileHandle, textToWrite, PRINT_DEBUG)

                    print "\nPadding in pixels to add for FT962 format: %s\n" % paddingInPixelsToAdd

                    
                    if numBitsPerPixel == 16:
                        #Group in 2 bytes!
                        actualReversedImageWord = []
                        tempWord = ''
                        count = 0   
                        
                        for i in actualReversedImage:
                            if count < 4:
                                if count == 0:
                                    tempWord = ''
                                
                                tempWord += i
                                count += 1
                            else:        
                                #actualImageHex.insert(0, tempByte)
                                actualReversedImageWord.append(tempWord)
                            
                                count = 1
                                tempWord = i
                        
                            
                        #########################################################
                        #RENDER THE IMAGE
                        #########################################################

                        nextIsPadding = False
                        paddingCounter = count = 0
                        cleanData = ''
                        rowDis = ''
                        padding = ''
                        
                        
                        for i in actualReversedImageWord:
                            #Let us not include the padding bits in the process
                            if nextIsPadding == True:
                                if paddingCounter < paddingInPixelsToRemove:
                                    padding += i
                                    paddingCounter += 1
                                else:
                                    padding = ''
                                    paddingCounter = 0
                        
                                    #Store first padding bit!
                                    nextIsPadding = False
                                    count = 1
                                    rowDis += i
                            else:
                                
                                if count < widthInPixels:
                                        rowDis += i
                                        count += 1
                                else:
                                        paddingBits = ''
                                        j = 0
                                        while j < paddingInPixelsToAdd:
                                            paddingBits = paddingBits + '0'
                                            j += 1
                                            
                                        #textToWrite = "\nPadding Bits > %s" % paddingBits                                
                                        #rowDis = '0000000' + rowDis
                                        rowDis = paddingBits + rowDis
                                        textToWrite = rowDis + '\n'
                                        #writeToFile(fileHandle, textToWrite, PRINT_DEBUG)

                                        print textToWrite
                        
                                        cleanData += rowDis
                                        
                                        rowDis = ''
                                        count = 0
                        
                                        #Store first padding bit!
                                        paddingCounter = 1
                                        nextIsPadding = True
                                        padding += i



                            

                    else:
                    
                        actualReversedImageBin = bin(int('1'+actualReversedImage,16))[3:]
                        actualUnreversedImageBin = bin(int('1'+actualUnreversedImage,16))[3:]
    
                        textToWrite = "\n--IMAGE RENDER--\n"
                        writeToFile(fileHandle, textToWrite, PRINT_DEBUG)
                        count = paddingCounter = 0
                        rowDis = ""
                        padding = ""
                        
                                     
                        if RENDER is True:
                            nextIsPadding = False
                            paddingCounter = 0
                            cleanData = ''
                            for i in actualReversedImageBin: 
                                #Let us not include the padding bits in the process
                                if nextIsPadding == True:
                                    if paddingCounter < paddingInPixelsToRemove:
                                        padding += i
                                        paddingCounter += 1
                                    else:
                                        padding = ""
                                        paddingCounter = 0
                        
                                        #Store first padding bit!
                                        nextIsPadding = False
                                        count = 1
                                        rowDis += i
                                else:
                                    if count < widthInPixels:
                                            rowDis += i
                                            count += 1
                                    else:
                                            paddingBits = ""
                                            j = 0
                                            while j < paddingInPixelsToAdd:
                                                paddingBits = paddingBits + '0'
                                                j += 1
                                                
                                            #textToWrite = "\nPadding Bits > %s" % paddingBits                                
                                            #rowDis = '0000000' + rowDis
                                            rowDis = paddingBits + rowDis
                                            textToWrite = rowDis.replace('1', ' ') + '\n'
                                            writeToFile(fileHandle, textToWrite, PRINT_DEBUG)
                        
                                            cleanData += rowDis
                                            
                                            rowDis = ""
                                            count = 0
                        
                                            #Store first padding bit!
                                            paddingCounter = 1
                                            nextIsPadding = True
                                            padding += i
                        
                            ##textToWrite = "\nCLEAN DATA : \n%s" % cleanData
                        
                            cleanData = ''.join(list(reversed(cleanData)))
                            print "\nBIN : \n%s" % cleanData
                        
                        
                            counter = 0
                            byteString = ''
                            finalHexList = []
                            
                            
                            for bit in cleanData:
                                if counter < 8:
                                    byteString += bit
                                    counter += 1
                                else:
                                    finalHexList.append("0x%02x" % int(byteString, 2))
                                    
                                    byteString = ''
                                    byteString += bit
                                    counter = 1
            
                            finalHexList.append("0x%02x" % int(byteString, 2))
            
            
                            width = hex(paddingInPixelsToAdd + widthInPixels)
                            print "Width: ", width
                        
                            widthInPixels = hex(widthInPixels) #hex(ceiling_factor_8) #
                            heightInPixels = hex(heightInPixels)
                        
            
                            fontHeader = []
                            temp_unicode = '0'
            
                            
                            if convertImage:
                                ##finalHexList = ['0x00','0x00','0x00','0x00','0x00','0x00','0x00','0x00','0x00','0x00','0x00','0x00',widthInPixels,heightInPixels] + finalHexList + ['0x00','0x00','0x00','0x00','0x00']
                                finalHexList = [widthInPixels, heightInPixels] + finalHexList + ['0x00','0x00','0x00','0x00','0x00']
            
                                ##finalHexList = hex(int('1'+cleanData,2))
                                ##finalHexList = finalHexList[:2] + finalHexList[3:]
                                textToWrite = "\nFINAL HEX : \n%s\nSIZE : %s\n" % (finalHexList, len(finalHexList))
                                writeToFile(fileHandle, textToWrite, PRINT_DEBUG)
                        
                                #Write to file
                                f = open(bmpFileOutput, 'w+')                
                                f.write("\n")
            
                                filename = filename.replace('_mirrored', '').replace(' ', '_').replace('_mirror', '')
                            
                                textToWrite = filename[:-4] + "[%s] = {" % len(finalHexList)
                                f.write(textToWrite)
                                for i in finalHexList:
                                    f.write(i)
                                    f.write(',')
                                f.write('};')
                                f.close()
            
            
                            
                            elif convertFont:                    
                                temp = re.search(r'(.*)_', filename[:-4], re.M|re.I)
                                if temp:
                                    temp_unicode = int(temp.group(1))
                                    uni_code = [hex(temp_unicode), hex(0x00)]
                                else:
                                    temp_unicode = 0x00
                                    uni_code = [hex(temp_unicode), hex(0x00)]
            
                                #Note: As per UI designer, this is not needed
                                x_offset = hex(0x00)
                                
                                #Note: y_offset is obtained from filename after the underscore, ex. 65_0 = 65 is unicode for 'A', 0 is the y_offset
                                temp = re.search(r'_(.*)', filename[:-4], re.M|re.I)
                                if temp:
                                    y_offset = hex(int(temp.group(1)))
                                else:
                                    y_offset = hex(0x00)
                                    
                                real_width = widthInPixels
                                #width = paddingInPixelsToAdd + int(widthInPixels,16)
                                height = heightInPixels
                                x_addr = hex(0x00)
            
                                addr_low = [hex(currentAddress & 0xFF), hex(currentAddress >> 8)]
                                addr_high = [hex(0x00), hex(0x00)]
            
                                currentAddress = currentAddress + len(finalHexList)
            
                                #Add headers to finalHexList
                                fontHeader = uni_code + [x_offset, y_offset, real_width, width, height, x_addr] + addr_low + addr_high
            
                                fontHeaderList += fontHeader
            
                                fontDataList += finalHexList
            
                                
                                textToWrite = "\nFINAL HEX : \n%s\nSIZE : %s\n" % (fontHeader, len(fontHeader))
                                writeToFile(fileHandle, textToWrite, PRINT_DEBUG)
                        
                                #Write to font header file
                                fh = open(fontHeaderFileOutput, 'a+')                
                                fh.write("\n")
            
                                filename = filename.replace('_mirrored', '').replace(' ', '_').replace('_mirror', '')
            
                                textToWrite = '/*' + str(int(temp_unicode)) + '*/'
                                fh.write(textToWrite)
                                for i in fontHeader:
                                    fh.write(i)
                                    fh.write(',')
                                fh.close()
                              
            
            
                                #Write to font data file
                                fd = open(fontDataFileOutput, 'a+')                
                                fd.write("\n")
            
                                filename = filename.replace('_mirrored', '').replace(' ', '_').replace('_mirror', '')
                            
                                textToWrite = '/*' + str(int(temp_unicode)) + "[%s]*/" % len(finalHexList)
                                fd.write(textToWrite)
                                for i in finalHexList:
                                    fd.write(i)
                                    fd.write(',')
                                fd.close()
                
                        else:
                            textToWrite = "\nREVERSED: \n%s\n" % actualReversedImageBin.replace('1', ' ')
                            writeToFile(fileHandle, textToWrite, PRINT_DEBUG)
                            textToWrite = "\nUNREVERSED: \n%s\n" % actualUnreversedImageBin.replace('1', ' ')
                            writeToFile(fileHandle, textToWrite, PRINT_DEBUG)
    
                    
        
            if convertFont:
                filenames = [fontHeaderFileOutput, fontDataFileOutput]
                with open(fontBinFile, 'w') as outfile:
                    for fname in filenames:
                        with open(fname) as infile:
                            for line in infile:
                                outfile.write(line)
    
    fileHandle.close()
    
    print "\nTAKE NOTE OF THIS LAST ADDRESS > ", currentAddress + 255
    raw_input("\n\nSCROLL UP to view IMAGE ANALYSIS RESULT/S or press <ENTER> to QUIT: ")
            
            
            
            
            
            
            
            
            
            
            
            
            
                
                
            
            
