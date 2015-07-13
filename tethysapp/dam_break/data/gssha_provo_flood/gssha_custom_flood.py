#-------------------------------------------------------------------------------
# Name:        module1
# Purpose:
#
# Author:      mscott90
#
# Created:     21/02/2014
# Copyright:   (c) mscott90 2014
# Licence:     <your licence>
#-------------------------------------------------------------------------------
import shutil, sys, re, subprocess, time, os

GSSHA_EXE = 'gssha.exe'

def main(prj, lineNum):
    #editReplaceLine(prj, lineNum)
    runGSSHA(prj)
    reformat(prj)
    #renameOutput(prj,lineNum)


def editReplaceLine(prj,lineNum):

    f = open(prj,'r+')
    text = f.read()
    text = re.sub('REPLACE_LINE.*','REPLACE_LINE             {0}'.format(lineNum), text )
    f.seek(0)
    f.write(text)
    f.close()

def runGSSHA(prjFile):
    outFile = "run.out"
    out = open(outFile, 'w')
    process = subprocess.Popen([GSSHA_EXE, prjFile], stdout = out, stderr = out, cwd='gssha_provo_flood')
    process.wait()
    out.close()

def reformat(prj):
    projectName = re.sub('.prj','',prj)
    gfl = projectName + '_StochOutput/' + projectName + '.gfl'
    reformatGFL(gfl)

def renameOutput(prj,pre):
    projectName = re.sub('.prj','',prj)
    outputDir = projectName + '_StochOutput/'
    baseFilePath = os.getcwd()
    cwd = os.path.join(baseFilePath, outputDir)
    os.chdir(cwd)
    files = os.listdir(cwd)
    for f in files:
        shutil.move(f,str(pre).zfill(4) + '_' + f)


def reformatGFL(gfl, threshold=0.03):
    HEADER = """ncols 	122
nrows 	96
xllcenter 437269.78
yllcenter 4450221.00
cellsize     90.00
NODATA_value -9999.99
    """

    HEADER = """north: 4458816.000000
south: 4450176.000000
east: 448204.778793
west: 437224.778793
rows: 96
cols: 122
    """
    NCOLS = 122
    START_VALUES = 11720

    output = open(gfl, 'r')
    lines = output.readlines()
    if len(lines) > 7:
        with open('max_flood.txt', 'w') as f:
            f.write(HEADER)
            values = lines[START_VALUES:-1]
            col = 0
            for value in values:
                col += 1
                value = float(value)
                value = '1' if value > threshold else '0'
                if(col % NCOLS == 0):
                    value += '\n'
                else:
                    value += '\t'
                f.write(value)

if __name__ == '__main__':
    if len(sys.argv) == 3:
        prj = sys.argv[1]
        lineNum = int(sys.argv[2]) + 1
    else:
        prj = 'ProvoStochastic.prj'
        lineNum = 1
    main(prj, lineNum)
