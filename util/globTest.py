import glob
import os

vFileDir = '/Users/htullis/OneDrive - Accenture/1Accenture/2Client/3USA/Vistra/Marcus_Hank/eSP_Prod'
vHostDir = 'escp_output_dc1sdeexa2dbn03_20240214'
vFilePath = vFileDir + '/' + vHostDir
vFileSearch = vFilePath + '/' + 'escp*.zip'
vFileList = glob.glob(vFileSearch)

print (vFileList)
