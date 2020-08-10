# Protect3d-Phoenx
###2020 Phoenix project
#Dependencies
* Numpy
* Numpy-stl
* py-goicp  
    *   (https://github.com/aalavandhaann/go-icp_cython). Download from pip or you can manually compile.
    * Issue on mac pip install requires manual compiling. 
    
# Quick Start
Included are scripts pertaining to realignment. 

An example run looks like **'python protectRunner.py meshes/AnkleMesh_1_L_Input.stl AnkleAtlasL.stl'**
* **meshes/AnkleMesh_1_L_Input.stl** is the input file
* **AnkleAtlasL.stl** is the current atlas. 
* The output is saved to **meshes/AnkleMesh_1_L_Input_reoriented.stl**

#GO Icp Params
* mseUnscaled: default = .04
    * This is the threshold for defining correct alignment. 
    A lower value means longer runtime but more precise output
* pruneAmount: default = 200
    * Number of data points to use in atlas. Lower value decreases runtime but could affect accuracy. 
* trimFraction: default = .15
    * Percentage of atlas data points to be considered outliers during go-icp. Useful if region of atlas
    does not exist in input (input scan has shorter shin length etc.). Setting to 0 can help for many input 
    scans. Small increase in runtime for some examples, for others it is faster. 
* dtSize: default = 150
    * Used to specify size of closest point framework. Higher value means more precise error measurement 
    but much longer runtime. I would recommend changing after other values and not going beyond 300. 