/*
Covert channel using Algorithm 1 under Hyper-threaded sharing

Usage: see README 
Authors: Yujie Cui (YujieCui@pku.edu.cn) 

*/

#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include<stdint.h>
#include<math.h>
#include <string.h>
#include <unistd.h>
#include <sys/mman.h>
#include <sys/types.h>
#include <sys/syscall.h>
#include <immintrin.h>
#include <x86intrin.h>
#include <pthread.h>
#include <assert.h>
#include <time.h>
#define gettid() syscall(SYS_gettid)
#include <dlfcn.h>
#include <assert.h>


void * chainSta[2];
void ** chainLast[2];

char* chain_array[512*8]; // array to hold the pointer chasing chain  =way_size *8
unsigned int g_result[512*2*256];// to hold 100000 element, only use set 0-31 ((i/512)*1024+i%512)
uint64_t probe[64*35*8]; //64sets * 8 way * linesize
int perm[32]; 

int Tone=10000;
int Tzero=10000;
int Tmonitor=10000;
volatile uint8_t temp = 0;
int para_d=4;
char sender_mode='a';
uint8_t *chain;
uint64_t* way[64][10];
int cacheSetNum = 64;
int cacheLineNum = 8;
int cachelineSize =  64;
int d ;




void  createPermutation(int arr[],int size){
//  create random permutation of probe size in perm[]
//  To avoid prefetcher
	srand(10);
	for(int i=0; i < size; i++){
		arr[i]=i;
	}

	for(int i=0; i < size; i++){
		int j = i + (rand()%(size-i));
		if(i!=j){
			int tmp=arr[i];
			arr[i]=arr[j];
			arr[j]=tmp;
		}
	
	}
}





void**  creatChase(void *addr,unsigned int stride,int len){
	
	len=len-1;
	void* memory=addr;
	void** last = (void**) memory;
	int perm[20];
	createPermutation(perm, len);
	for(int i=0;i<len;i++) {
		uint8_t* next = (uint8_t*) memory + (perm[i]+1)*stride; //stride depends to data type (uint8_t +1)
		*last = (void*) next; 
		last = (void**) next;
	}
	*last = (void *)memory;
	return last;

}

void setWayArr( uint64_t* way[64][10],uint64_t probe[]){
	int perm[10];
	 for (int i = 0; i< 64;i++) {//64 sets
      createPermutation(perm,9);
      way[i][0]= &probe[cachelineSize/8*i + cachelineSize/8*64];
      for( int j = 0; j < 9;j++){
		way[i][j+1]= &probe[cachelineSize/8*(i+(perm[j]+1)*64) + cachelineSize/8*64];
      }
  }

}

void  senderMultiBits() {
  	int message[128] = {0,2,0,2, 3,1,3,1};
	unsigned int junk=0;
	 void *sta;
  if(sender_mode== '0'){
      for(int i =0; i< 128; i++){
            message[i] = 0;
      }
  }
  else if(sender_mode== '1'){
      for(int i =0; i< 128; i++){
            message[i] = 1;
      }
  }
  else if(sender_mode== 'r'){
        for(int i = 8;i < 128;i++){
        message[i]= rand()%4;
      } //generate random message
  }else{ // mode == 'a'
        for(int i =0; i< 128; i++){
            message[i] = i%4;
        } 
  }
    
  printf("Message to be sent: ");
  for(int i = 0;i < 128;i++){
    printf("%d",message[i]);
  }
  printf("\n");
    
  unsigned long long t=0,t1=0;
  unsigned long long T_next=0;


	t1= __rdtsc();
  for (;;) 
  {
      for(int i=0;i<128;i++){
		  
         if(message[i]==0){

      		t1= __rdtsc();
			do{
                t= __rdtsc();
              }
              while( (t-t1) < Tone  );
         }
       //send zero for Tzero
         else if(message[i]==1){
		 	t1= __rdtsc();
			for(int p=0;p<3;p++){
				for(int k=0;k<3;k++){
					*way[7][k]=*(way[7][k])+1;
				}
			}
			do{
                t= __rdtsc();
              }
              while( (t-t1) < Tone  );
			
		}else if(message[i]==2){

          	t1= __rdtsc();
			for(int p=0;p<3;p++){
				for(int k=0;k<5;k++){
					*way[7][k]=*(way[7][k])+1;
				}
			}
			do{
                t= __rdtsc();
              }while( (t-t1) < Tone  );	
		}else if(message[i]==3){
			t1= __rdtsc();
			for(int p=0;p<3;p++){
				for(int k=0;k<8;k++){
					*way[7][k]=*(way[7][k])+1;
				}
			}
			do{
                t= __rdtsc();
              }
              while( (t-t1) < Tone  );	
         }


       }

  }

}

void delayTest(){

unsigned int No_test=100000;
unsigned long long t=0,t1=0;
 void *sta;
  int cnt=0;
  for (cnt=0;cnt<No_test;cnt++) 
  {  
	 	 t1=_rdtsc();
		sta=chainSta[cnt%2];
		asm __volatile__ (
		"lfence              \n" 
		"rdtsc               \n"
		"movl %%eax, %%esi   \n"
		"movq (%%rcx),  %%rax     \n"
		"movq (%%rax),  %%rax     \n"
		"movq (%%rax),  %%rax     \n"
		"movq (%%rax),  %%rax     \n"
		"movq (%%rax),  %%rax     \n"
		"movq (%%rax),  %%rax     \n"
		"movq (%%rax),  %%rax     \n"
		"movq (%%rax),  %%rax     \n"
		"movq (%%rax),  %%rax     \n"
		"movq (%%rax),  %%rax     \n"
		"lfence              \n"
		"rdtsc               \n"
		"subl %%esi, %%eax   \n"
		: "=a" (t)
		: "c" (sta)
		: "%esi", "%edx");
		g_result[((cnt/512)*1024+cnt%512)]= t;
		
		do{
			t = _rdtsc();
		} while((t-t1) < Tmonitor );
  }

  for (cnt=0;cnt<No_test;cnt++){
      printf("%d %d\n",cnt, g_result[((cnt/512)*1024+cnt%512)]);
  }
    
}

int main(int argc, char *argv[]) {
    
	int isSend = 0;
	if(argc <2) { printf("wrong configure! must choose between sender or receiver\n"); return -1;}
  if (strcmp(argv[1], "sender") == 0){
      isSend=1;
      if(argc <3) { 
			printf("wrong configure! must choose sender mode, opetions: \n 0 (send 0),\n 1 (send 1),\n a (send 010101...),\n r (send random bits after a prefix).\n"); return -1;}
			sender_mode=argv[2][0]; 
      if(argc >= 4){
        	Tone=strtol(argv[3], NULL, 10);
        	Tzero=strtol(argv[3], NULL, 10);
        	printf("Tone=%d Tzero=%d\n",Tone,Tzero);
      }    
  }else if (strcmp(argv[1], "receiver") == 0){
		isSend=0;
		if(argc >= 3){
        	Tmonitor=strtol(argv[2], NULL, 10);
        	printf("Tmonitor=%d\n",Tmonitor);
      }  

  } else{ 
		printf("wrong configure!\n"); 
		return -1;
		}

	for(int i=0;i<sizeof(probe)/8;i++){
		probe[i] = i;
	}


	srand(1234);
	cpu_set_t victim_set;
  	CPU_ZERO(&victim_set); 
  	cpu_set_t attacker_set;
  	CPU_ZERO(&attacker_set);
    
  //For example, cpu 3 and 27 are sharing one core  
	CPU_SET(3,&victim_set);
  	CPU_SET(27,&attacker_set);


	setWayArr(way,probe);

	chainSta[0] = &probe[8*7 + 1*cachelineSize/8*64]; // two replacement sets
	chainLast[0] = creatChase(chainSta[0],64*64,10);
	chainSta[1] = &probe[8*7 + 12*cachelineSize/8*64];
	chainLast[1] = creatChase(chainSta[1],64*64,10); 

	if(isSend){
		if(sched_setaffinity(gettid(),sizeof(cpu_set_t),&victim_set)==-1){
			printf("Can not set affinity\n");
			return 1;
		} 
		senderMultiBits();
	}
	else{

		if(sched_setaffinity(gettid(),sizeof(cpu_set_t),&attacker_set)==-1){
			printf("Can not set affinity\n");
			return 1;
		}
	
		delayTest();
	}




  return 0;
}

