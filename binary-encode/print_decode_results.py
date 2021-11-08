import os
import argparse


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



    
def print_observation(filePath,Threshold):
    

    lines = fileRead(filePath)
    
    sta=1000
    end = sta+3000
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
    
    yy=yy[ind:ind+128]
    print(yy)

    
if __name__=="__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--file_path','-f',  default=None, help='The path where the data is located.')
    parser.add_argument('--Threshold', '-t', default=-1, help='Threshold for distinguishing different coding symbols')
    args = parser.parse_args()
    if args.file_path and args.Threshold:
        print_observation(args.file_path,int(args.Threshold))
    else:
        print("python print_decode_results.py --file_path=your_data_path --Threshold=your_Threshold")