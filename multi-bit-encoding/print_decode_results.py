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



def print_observation(filePath,ThresHold):

    
    lines = fileRead(filePath)
    sta=299
    end = sta+3000
    sub_lines = lines[sta:end]
    yy=''
    print_res=''
    for sub_line in sub_lines:
        if (int(sub_line.split()[1])<ThresHold[0]):
            yy+='00'
        elif (int(sub_line.split()[1])<ThresHold[1]):
            yy+='01'
        elif (int(sub_line.split()[1])<ThresHold[2]):
            yy+='10'
        else:
            yy+='11'
            
    # When sending a random sequence, look for the bit pattern at the start position.
    ind = yy.find('0010001011011101')
    
    
    if(ind==-1):
        ind = 0
    elif ind>3000:
        ind = 0
    
    yy=yy[ind:ind+256]
    for i in range(0,len(yy)):
        print(yy[i],end='')
        if ((i+1)%2==0 and i!=0):
            print(' ',end='')
    print()


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
    
    ThresHold=[125,157,181]
    
    if args.file_path:
        text=print_observation(args.file_path,ThresHold)
      


