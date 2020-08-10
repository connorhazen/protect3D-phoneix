def saveConfigFile(fileName = "output.txt", mseThresh = .0001, rotMin = -3.1416, transMin = -0.5, trimFrac = 0.0, distTransSize = 300, distTransExpandFactor = 2 ):
    f = open(fileName, 'w')

    f.write("MSEThresh=" + str(mseThresh) + "\n")


    f.write("rotMinX="+str(rotMin)+ "\n")
    f.write("rotMinY="+str(rotMin)+ "\n")
    f.write("rotMinZ="+str(rotMin)+ "\n")
    f.write("rotWidth="+ str((-2*rotMin))+ "\n")


    f.write("transMinX="+str(transMin)+ "\n")
    f.write("transMinY="+str(transMin)+ "\n")
    f.write("transMinZ="+str(transMin)+ "\n")
    f.write("transWidth="+ str((-2*transMin))+ "\n")


    f.write("trimFraction="+str(trimFrac)+ "\n")


    f.write("distTransSize="+str(distTransSize)+ "\n")
    f.write("distTransExpandFactor="+str(distTransExpandFactor)+ "\n")


    f.close()
