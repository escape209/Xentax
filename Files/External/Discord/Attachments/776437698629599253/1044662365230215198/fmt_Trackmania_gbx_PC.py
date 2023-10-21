from inc_noesis import *
import noesis
#import rapi

def registerNoesisTypes():
	handle = noesis.register("Trackmania",".gbx")
	noesis.setHandlerTypeCheck(handle, noepyCheckType)
	noesis.setHandlerLoadModel(handle, noepyLoadModel)
	return 1
	
NOEPY_HEADER = "GBX"

def noepyCheckType(data):
   bs = NoeBitStream(data)
   if len(data) < 3:
      return 0
   if bs.readBytes(3).decode("ASCII") != NOEPY_HEADER:
      print("'gbx' not found!")
      return 0
   return 1  	

def noepyLoadModel(data, mdlList):
	ctx = rapi.rpgCreateContext()
	bs = NoeBitStream(data)

	texList = []
	matList = []
	TexNames = []

	bs.seek(0x89, NOESEEK_REL)
	NumMeshes = bs.readUInt()

	for i in range(50):
		addr=bs.tell()
		fileBuff = bs.data[addr:bs.dataSize]
		addr1= fileBuff.find(b'\x0E\x60\x00\x09\x38\x00\x00')
		addr += addr1
		bs.seek(addr)
		bs.seek(-0x48, NOESEEK_REL)
		MaterialName = (bs.readBytes(8).decode("ASCII").lstrip("\0"))
		bs.seek(0x4C, NOESEEK_REL)
		VCount = bs.readUInt()
		bs.seek(0x8, NOESEEK_REL)
		UVAddress = bs.tell()
		UVsize = VCount*8
		UVBuff = bs.readBytes(UVsize)
		rapi.rpgBindUV1BufferOfs(UVBuff, noesis.RPGEODATA_FLOAT, 8, 0)
		bs.seek(0x28, NOESEEK_REL)			
		VAddress= bs.tell()
		FVFsize = int(40)
		VBuff = bs.readBytes(VCount*FVFsize)
		rapi.rpgBindPositionBufferOfs(VBuff, noesis.RPGEODATA_FLOAT, FVFsize, 0)
		bs.seek(0x18, NOESEEK_REL)
		FCount = bs.readUInt()
		FAddress= bs.tell()
		FBuff = bs.readBytes(FCount*2)
		rapi.rpgCommitTriangles(FBuff, noesis.RPGEODATA_USHORT, FCount, noesis.RPGEO_TRIANGLE, 1)
		material = NoeMaterial(MaterialName,"")
		matList.append(material)
		rapi.rpgSetMaterial(MaterialName)
		bs.seek(addr+1, NOESEEK_ABS)

	mdl = rapi.rpgConstructModel()
	mdl.setModelMaterials(NoeModelMaterials(texList, matList))
	mdlList.append(mdl)
	rapi.rpgClearBufferBinds()
	return 1