import os
import argparse
import re
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


def get_paras_from_filepath(filepath):
    
    filename = os.path.split(filepath)[1]
    parm_list = filename.split('_')
    dirty_line_num = int(parm_list[1].split('=')[1])
    T_s = int(parm_list[2].split('=')[1])
    default_Thresholds=[113,118,122,127,137,146,152,157]
    ThresHold = default_Thresholds[dirty_line_num-1]
    
    return {"dirty_line_num":dirty_line_num,"T_s":T_s,"ThresHold":ThresHold}

def sortSame(ls1,ls2):
		ls = list(zip(ls1, ls2))
		# random.shuffle(c)
		ls.sort()
		ls1, ls2 = zip(*ls)
		return ls1,ls2

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

def getStart(filePath,ThresHold):
    
    paras_dict = get_paras_from_filepath(filePath)
    if ThresHold==-1:
        ThresHold = paras_dict["ThresHold"]
    
    lines = fileRead(filePath)

    sta=666
    end = sta+3000
    sub_lines = lines[sta:end]
    yy=''
    for sub_line in sub_lines:
        if (int(sub_line.split()[1])<ThresHold):
            yy+='0' 
        else:
            yy+='1'
    ind = yy.find('0000101011110101')
    return ind+sta

def plotOneBit(filePath,sta,figName,thres,textSta):
    paras_dict = get_paras_from_filepath(filePath)
    if thres==-1:
        thres = paras_dict["ThresHold"]
        
    font=MyFont(6)
    plt.switch_backend('Agg')

    fig = plt.figure(num=None, figsize=(3,2), dpi=1200, facecolor='w')
    plt.subplots_adjust(right = 0.98, top = 0.96, bottom=0.1,left=0.1)

    # calibration=[0,0,0,0,1,0,1,0,1,1,1,1,0,1,0,1]
    calibration=[]
# first fig
    drawLen=128
    xLimit=[0,drawLen]
    yLimit=[50,230]
    plt.subplots_adjust(hspace = 0.3)
    ax=plt.subplot(211)
    
    lines = fileRead(filePath)

    sub_lines = lines[sta:sta+drawLen]

    yy=[]
    thresHold_y = [thres]*(drawLen+1)
    thresHold_x = np.arange(0,drawLen+1,1)
    ax.plot(thresHold_x,thresHold_y,'-.',markersize=1, markeredgewidth=0.1,color='r',lineWidth=0.4)


    for sub_line in sub_lines:
        # print(sub_line.split()[1])
        yy.append(int(sub_line.split()[1]))
        if (int(sub_line.split()[1])< thres):
            calibration.append('0')
        else:
            calibration.append('1')
    xx = np.arange(0.5,drawLen,1)
    ax.vlines(x=xx, ymin=0, ymax=yy, color='k', alpha=1, linewidth=0.1)
    ax.scatter(x=xx, y=yy, s=0.2, color='k', alpha=1)


    thresHold_y = [thres]*(drawLen+1)
    thresHold_x = np.arange(0,drawLen+1,1)
    ax.plot(thresHold_x,thresHold_y,'-.',markersize=1, markeredgewidth=0.1,color='r',lineWidth=0.4)


    font.setSize(6)
    plt.xlabel('Receiver\'s Observation Sequence',fontdict = font.fontaxes,labelpad=1.5)
    plt.ylabel('Latency(Cycles)',fontdict = font.fontaxes,labelpad=1.5)
    plt.gca().set_xlim(xLimit)
    plt.gca().set_ylim(yLimit)

    plt.tick_params(labelsize=6,width=0.2,length=1.5,pad =0.5)
    dirValue=['top','bottom','left','right']
    [plt.gca().spines[dir].set_linewidth(0.3) for dir in dirValue]
    

    ax=plt.subplot(212)
    drawLen=16
    xLimit=[0,16]
    yLimit=[80,230]
    lines = fileRead(filePath)
    # sta=1000+150
    sub_lines = lines[sta:sta+drawLen]
    yy=[]
    
    for sub_line in sub_lines:
        yy.append(int(sub_line.split()[1]))
        
    # thres=93
    subX,subY=getColorXY(yy,[thres])

    
    ax.plot(subX[0],subY[0],'o',markersize=2, markeredgewidth=0.1,color='b')
    ax.plot(subX[1],subY[1],'o',markersize=2, markeredgewidth=0.1,color='g')
    for i in range(0,drawLen,1):
        ax.text(i+0.4,textSta,str(calibration[i]),fontdict={'size':'6','color':'black','weight': 'bold'})

    plotGrid(currentAx=ax,xRange=xLimit,yRange=yLimit,xInterval=1)
    thresHold_y = [thres]*(drawLen+1)
    thresHold_x = np.arange(0,drawLen+1,1)
    ax.plot(thresHold_x,thresHold_y,'-.',markersize=3, markeredgewidth=0.2,color='r',lineWidth=0.5)

    font.setSize(6)
    plt.xlabel('Receiver\'s Observation Sequence',fontdict = font.fontaxes,labelpad=1.5)
    plt.ylabel('Latency(Cycles)',fontdict = font.fontaxes,labelpad=1.5)
    plt.gca().set_xlim(xLimit)
    plt.gca().set_ylim(yLimit)
    # plt.tick_params(labelsize=2)
    plt.tick_params(labelsize=6,width=0.2,length=1.5,pad =0.5)
    dirValue=['top','bottom','left','right']
    [plt.gca().spines[dir].set_linewidth(0.3) for dir in dirValue]
    plt.savefig(figName+'.png')

def get_error_rate(filePath,Threshold):
    cpu_freq = 10**9*2.2
    paras_dict = get_paras_from_filepath(filePath)
    if Threshold==-1:
        Threshold = paras_dict["ThresHold"]
        
    dirty_line_num =  paras_dict["dirty_line_num"]
    T_s = paras_dict["T_s"]


# During the evaluation, the sender continuously sends a 128-bit random sequence, and the first 16 bits of 
# the random sequence are set to a  fixed value for the receiver to identify. The 128-bit random sequence is
# sent at least 90 times to obtain the average bit error rates.

    correct_str='00001010111101011110101001000110001001110011110101111000100111111000011000111101011001011010101111111011000011110010110011011000'
    levenshtein = Levenshtein()
    correct_str=correct_str*(90)
    lines = fileRead(filePath)
    
    sta=1000
    end = sta+len(correct_str)+3000
    sub_lines = lines[sta:end]

    yy=''
    for sub_line in sub_lines:
        if (int(sub_line.split()[1])>Threshold):
            yy+='1' 
        else:
            yy+='0'
    ind = yy.find('0000101011110101')

    if(ind==-1):
        ind = 0
    elif ind>3000:
        ind = 0
    
    yy=yy[ind:ind+len(correct_str)]

    error_rate = (levenshtein.distance(correct_str, yy))/len(correct_str)
    
    text='transmit rate='+str(int(cpu_freq)/int(T_s)/1000)+' kbps '+'d='+str(dirty_line_num)+' '+' error rate='+str(error_rate)+' thresHold='+str(Threshold)+'\n'

    
    return text

def plotRate(filepath,figName):
    plt.switch_backend('Agg')
    font =MyFont(6)
    lines = fileRead(filepath)

    d_x=[]
    d_y=[]
    for i in range(1,9,1):
        d_x.append([])
        d_y.append([])

    ls=['d','transmit rate','error rate']
    fin = getValue(lines,ls)
    for line in fin :
        d_x[int(line['d'])-1].append(float(line['transmit rate']))
        d_y[int(line['d'])-1].append(float(line['error rate'])*100)

    ax = None
    fig = plt.figure(num=None, figsize=(3, 1.2), dpi=600, facecolor='w')
    plt.subplots_adjust(right = 0.98, top = 0.9, bottom=0.25,left=0.15,wspace=1, hspace=2)
    ax = plt.gca()
    for i in range(0,len(d_x),1):	
        if(len(d_x[i])!=0):
            xx,yy = sortSame(d_x[i],d_y[i])
            ax.plot(xx,yy,color=colors[i],linestyle='--',linewidth=0.1,marker='o',
                markeredgecolor=colors[i],markersize='0.3',markeredgewidth=2)
    
    plt.legend(['d=1','d=2','d=3','d=4','d=5','d=6','d=7','d=8'],fontsize=4,
            loc='center right',edgecolor='black',ncol=1)#upper left
    font.setSize(5)
    plt.xlabel('Transmission Rate (Kbps)',fontdict = font.fontaxes,labelpad=1.5)
    plt.ylabel('Error Rate',fontdict = font.fontaxes,labelpad=1.5)
    plt.gca().set_xlim([0,3300])
    plt.gca().set_ylim([0,15])
    plt.tick_params(labelsize=4)
    plt.gca().yaxis.set_major_formatter(mtick.FormatStrFormatter('%.2f%%'))
    plt.savefig(figName)

    
    
if __name__=="__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--file_path','-f',  default=None, help='The path where the data is located.')
    parser.add_argument('--Threshold', '-t', default=-1, help='Threshold for distinguishing different coding symbols')
    parser.add_argument('--draw_fig', '-d',action='store_true', default=False, help='Plot the delay sequence observed by the receiver.')
    parser.add_argument('--error_rate', '-e',action='store_true', default=False, help='Measure the bit error rate of the covert channel.')
    parser.add_argument('--fig_name', '-n', default=None, help='The name of the drawn picture.')
    parser.add_argument('--dir', default=None, help='The directory where the data is located.')
    parser.add_argument('--dest_file', default=None, help='The file to which the results are written.')
    parser.add_argument('--draw_error_rates', action='store_true', default=False, help='Plot the relationship between bit error rate and transmission rate.')

    args = parser.parse_args()


    # thres_judge=[113,118,122,127,137,146,152,157]
    
    if not args.fig_name and (args.draw_fig or args.draw_error_rates):
        args.fig_name = args.file_path.split("/")[-1].split(".")[0]
    
    if args.draw_fig:
        plotOneBit(args.file_path,getStart(args.file_path,int(args.Threshold)),figName=args.fig_name,thres=int(args.Threshold),textSta=215)
        print("draw "+str(args.fig_name))

        
    if args.error_rate:
        if args.file_path:
            text=get_error_rate(args.file_path,int(args.Threshold))
            print(text)
            if args.dest_file:
                fileAppend(args.dest_file, text)

                
        if args.dir:
            for path in walkFiles(args.dir):
                text=get_error_rate(path,int(args.Threshold))
                print(text)
                if args.dest_file:
                    fileAppend(args.dest_file, text)
            
    if args.draw_error_rates:
        plotRate(args.file_path,args.fig_name)
        print("draw "+str(args.fig_name))