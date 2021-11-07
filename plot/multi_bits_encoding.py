import sys
import os
import argparse
import re

from mpl_toolkits.mplot3d import Axes3D
from matplotlib import cm
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.ticker as mtick

from strsimpy.levenshtein import Levenshtein



colors=['blue','darkgreen','red','gold','k','deeppink','fuchsia','lightpink','orangered']

class MyFont:
	fontaxes={}
	def __init__(self,size=3):
		fontaxes = {
			'family': 'Arial',
			'color':  'black',
			'weight': 'bold',
			'size': size,
		}
	def setSize(self,size):
		self.fontaxes['size'] = size
	def setColor(self,color):
		self.fontaxes['color'] = color

def fileRead(path,returnType='list'):
	if(not os.path.isfile(path)):
		print("file not found")
		return 
	text=[]
	try:
		with open(path,'r') as fr:
			lines=fr.readlines()
		
		if returnType == 'list':
			text=[]
			for line in lines:
				line  = line.strip()
				if not (line.isspace() or len(line)==0):
					text.append(line)
		elif returnType == 'str':
			text=''
			for line in lines:
				if not (line.isspace() or len(line)==0):
					text=text+line	
	except IOError:
		print("Failed to read")
		return
	else:
		return text

def fileAppend(path,text):
    if(not os.path.isfile(path)):
        print("file not found,create the new file: "+path)
    try :
        with open(path,'a+') as fw:
            if isinstance(text,str):
                fw.write(text)
            elif isinstance(text,list):
                fw.writelines([line+'\n' for line in text])
    except IOError:
        print("Failed to write")
        return False
    else:
        return True


def walkFiles(path,suffix=None):
    filesPath=[]  
    for root, dirs, files in os.walk(path): 
        for file in files:
            if not suffix or os.path.splitext(file)[1] == suffix: 
                filesPath.append(os.path.join(root, file)) 
    return filesPath

def getValue(lines,ls):
    fin=[]
    for line in lines:
        res={}
        for value in ls:	
            patternText=value+'='+'([0-9.]{1,20})'
            # pattern =re.compile(patternText)	
            if re.search(patternText,line) !=None:
                res[value] = re.search(patternText,line).groups()[0]
                # print(res)
        if res:
            fin.append(res)
    return fin

def sortSame(ls1,ls2):
		ls = list(zip(ls1, ls2))
		ls.sort()
		ls1, ls2 = zip(*ls)
		return ls1,ls2

def plotGrid(currentAx=None,figName='test',xRange=None,yRange=None,xInterval=None,yInterval=None,currentMaloc=None,currentMiloc=None,
    currentStyle='-.',currentWidth=0.6,currentColor='black',gridDir='both'):

    if not currentAx:
        currentAx=plt.gca()
        

    if xInterval:
        xMaloc = mtick.FixedLocator(np.arange(xRange[0],xRange[1]+1,xInterval))
        currentAx.xaxis.set_major_locator(xMaloc)
        currentAx.xaxis.grid(which='major',ls='-.',color="black",linewidth=0.2)
    if yInterval:
        yMaloc = mtick.FixedLocator(np.arange(yRange[0],yRange[1]+1,yInterval))
        currentAx.yaxis.set_major_locator(yMaloc)
        currentAx.yaxis.grid(which='major',ls=currentStyle,color=currentColor,linewidth=0.1)

def plotThresHold(thre,length,currentAx=None):
    for i in range(0,len(thre),1):
        thresHold_y = [thre[i]]*(length+1)
        thresHold_x = np.arange(0,len(thresHold_y),1)
        currentAx.plot(thresHold_x,thresHold_y,'-.',color=colors[i],
            markersize=1, markeredgewidth=0.1,lineWidth=0.2)


def getColorXY(yy,thres):
    sepX=[]
    sepY=[]
    for i in range(0,len(thres)+1,1):
        sepX.append([])
        sepY.append([])

    for i in range(0,len(yy),1):
        for j in range(0,len(thres),1):
            if(yy[i]<thres[j]):
                sepX[j].append(i+0.5)
                sepY[j].append(yy[i])
                break 
            elif (j==len(thres)-1):
                sepX[len(thres)].append(i+0.5)
                sepY[len(thres)].append(yy[i])
    return sepX,sepY

def getStart(filePath):

    figName = os.path.split(filePath)[1].split(".")[0]
    recName = figName.split('_')
    recName[1]=int(recName[1].split('=')[1])

    comp=['00','01','10','11']

    lines = fileRead(filePath)
    sta=300
    end = sta+3000
    sub_lines = lines[sta:end]
    ThresHold=[125,157,181]

    yy=''

    for sub_line in sub_lines:
        if (int(sub_line.split()[1])<ThresHold[0]):
            yy+='00' 
        elif (int(sub_line.split()[1])<ThresHold[1]):
            yy+='01'
        elif (int(sub_line.split()[1])<ThresHold[2]):
            yy+='10'
        else:
            yy+='11'

    
    ind = yy.find('0010001011011101')
    if(ind==-1):
        ind = 0
    elif ind>3000:
        ind = 0
    
    return int(300+ind/2)

def plotTwoBits(filePath,figName):
    
    
    thres=[125,155,185]

    sta=getStart(filePath)
    font=MyFont(6)
    plt.switch_backend('Agg')
    fig = plt.figure(num=None, figsize=(3,1.7), dpi=1200, facecolor='w')
    plt.subplots_adjust(right = 0.98, top = 0.96, bottom=0.1,left=0.1)

    drawLen=128
    xLimit=[0,drawLen]
    yLimit=[0,260]
    plt.subplots_adjust(hspace = 0.3)
    ax=plt.subplot(211)
    
    lines = fileRead(filePath)
    sub_lines = lines[sta:sta+drawLen]

    yy=[]
    for sub_line in sub_lines:
        yy.append(int(sub_line.split()[1]))
    xx = np.arange(0.5,drawLen,1)

    ax.vlines(x=xx, ymin=0, ymax=yy, color='k', alpha=1, linewidth=0.1)
    ax.scatter(x=xx, y=yy, s=0.2, color='k', alpha=1)

    plotThresHold(thres,drawLen,ax)

    font.setSize(5)
    plt.xlabel('Receiver\'s Observation Sequence',fontdict = font.fontaxes,labelpad=1.5)
    plt.ylabel('Latency(Cycles)',fontdict = font.fontaxes,labelpad=1.5)
    plt.gca().set_xlim(xLimit)
    plt.gca().set_ylim(yLimit)

    plt.tick_params(labelsize=4,width=0.2,length=1.5,pad =0.5)
    dirValue=['top','bottom','left','right']
    [plt.gca().spines[dir].set_linewidth(0.3) for dir in dirValue]
    


    ax=plt.subplot(212)
    drawLen=8
    xLimit=[0,drawLen]
    yLimit=[60,240]
    textSta=220
    calibration=[0,2,0,2,3,1,3,1]
    
    lines = fileRead(filePath)
    sub_lines = lines[sta:sta+drawLen]
    yy=[]
    
    for sub_line in sub_lines:
        yy.append(int(sub_line.split()[1]))
        
    subX,subY=getColorXY(yy,thres)

    ax.plot(subX[0],subY[0],'o',markersize=2, markeredgewidth=0.1,color='b')
    ax.plot(subX[1],subY[1],'o',markersize=2, markeredgewidth=0.1,color='g')
    ax.plot(subX[2],subY[2],'o',markersize=2, markeredgewidth=0.1,color='k')
    ax.plot(subX[3],subY[3],'o',markersize=2, markeredgewidth=0.1,color='r')

    for i in range(0,drawLen,1):
        ax.text(i+0.4,textSta,'{0:02b}'.format(calibration[i]),fontdict={'size':'4','color':'black','weight': 'bold'})
    plotGrid(currentAx=ax,xRange=xLimit,yRange=yLimit,xInterval=1)
    plotThresHold(thres,drawLen,ax)

    font.setSize(5)
    plt.xlabel('Receiver\'s Observation Sequence',fontdict = font.fontaxes,labelpad=1.5)
    plt.ylabel('Latency(Cycles)',fontdict = font.fontaxes,labelpad=1.5)
    plt.gca().set_xlim(xLimit)
    plt.gca().set_ylim(yLimit)
    plt.tick_params(labelsize=4,width=0.2,length=1.5,pad =0.5)
    dirValue=['top','bottom','left','right']
    [plt.gca().spines[dir].set_linewidth(0.3) for dir in dirValue]
    plt.savefig(figName+'.png')


def getTwoBitsErrorRates(filePath):
    cpu_freq = 10**9*2.2
    ThresHold=[125,157,181]
    filename = os.path.split(filePath)[1]
    T_s = int(filename.split('_')[1].split('=')[1])
    
    levenshtein = Levenshtein()

    comp=['00','01','10','11']
    binary_str=''
    
# The first 16 bits of the random sequence are set to a fixed value
# for the receiver to identify. The 256-bit random sequence is sent 
# at least 45 times to obtain the average bit error rates.

    correct_str='02023131331010102300031200302133001131030131102032031111102021322031130103320123323030111313101300023133021033021321302033303033'

    for i in range(0,len(correct_str),1):
        binary_str=binary_str+comp[int(correct_str[i])]

    binary_str=binary_str*(45)


    lines = fileRead(filePath)
    sta=300
    end = sta+len(binary_str)+3000
    sub_lines = lines[sta:end]

    yy=''
    for sub_line in sub_lines:
        if (int(sub_line.split()[1])<ThresHold[0]):
            yy+='00' 
        elif (int(sub_line.split()[1])<ThresHold[1]):
            yy+='01'
        elif (int(sub_line.split()[1])<ThresHold[2]):
            yy+='10'
        else:
            yy+='11'
            
    ind = yy.find('0010001011011101')
    if(ind==-1):
        ind = 0
    elif ind>3000:
        ind = 0
        
    yy=yy[ind:ind+len(binary_str)]
    assert(len(yy)==len(binary_str))

    rate = (levenshtein.distance(binary_str, yy))/len(binary_str)

    text='transmit rate='+str(int(cpu_freq)*2/int(T_s)/1000)+' kbps'+' '+ 'error rate='+str(rate)+' thresHold='+",".join('%s' %id for id in ThresHold)+'\n'
    return text

def plotTwoBitsRate(filepath,figName):
    plt.switch_backend('Agg')
    font =MyFont(6)
    lines = fileRead(filepath)

    d_x=[]
    d_y=[]

    ls=['transmit rate','error rate']
    fin = getValue(lines,ls)
    for line in fin :
        d_x.append(float(line['transmit rate']))
        d_y.append(float(line['error rate'])*100)


    ax = None
    fig = plt.figure(num=None, figsize=(3, 1.2), dpi=600, facecolor='w')
    plt.subplots_adjust(right = 0.98, top = 0.9, bottom=0.25,left=0.15,wspace=1, hspace=2)
    ax = plt.gca()

    xx,yy = sortSame(d_x,d_y)
    ax.plot(xx,yy,color=colors[0],linestyle='-',linewidth=0.3,marker='o',
        markeredgecolor=colors[0],markersize='0.3',markeredgewidth=2)
    
    font.setSize(5)
    plt.xlabel('Transmission Rate (Kbps)',fontdict = font.fontaxes,labelpad=1.5)
    plt.ylabel('Error Rate',fontdict = font.fontaxes,labelpad=1.5)
    plt.gca().set_xlim([0,6000])
    plt.gca().set_ylim([0,10])
    plt.tick_params(labelsize=4)
    plt.gca().yaxis.set_major_formatter(mtick.FormatStrFormatter('%.2f%%'))
    plt.savefig(figName)

if __name__=="__main__":
    
    parser = argparse.ArgumentParser()
    parser.add_argument('--file_path','-f',  default=None, help='The path where the data is located.')
    parser.add_argument('--draw_fig', '-d',action='store_true', default=False, help='Plot the delay sequence observed by the receiver.')
    parser.add_argument('--error_rate', '-e',action='store_true', default=False, help='Measure the bit error rate of the covert channel.')
    parser.add_argument('--fig_name', '-n', default=None, help='The name of the drawn picture.')
    parser.add_argument('--dir', default=None, help='The directory where the data is located.')
    parser.add_argument('--dest_file', default=None, help='The file to which the results are written.')
    parser.add_argument('--draw_error_rates', action='store_true', default=False, help='Plot the relationship between bit error rate and transmission rate.')
    
    args = parser.parse_args()
    
    
    if not args.fig_name and (args.draw_fig or args.draw_error_rates):
        args.fig_name = args.file_path.split("/")[-1].split(".")[0]
        
    if args.draw_fig:
        plotTwoBits(args.file_path,args.fig_name)

        
    if args.error_rate:
        if args.file_path:
            text=getTwoBitsErrorRates(args.file_path)
            print(text)
            if args.dest_file:
                fileAppend(args.dest_file, text)


        if args.dir:
            for path in walkFiles(args.dir):
                text=getTwoBitsErrorRates(path)
                print(text)
                if args.dest_file:
                    fileAppend(args.dest_file, text)

                    
                    
    if args.draw_error_rates:
        plotTwoBitsRate(args.file_path,args.fig_name)
        print("draw "+str(args.fig_name))