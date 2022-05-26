
# WB cache channels

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.5653683.svg)](https://doi.org/10.5281/zenodo.5653683) 

======================================================================

The files included in this archive contain the WB covert channel demo code.
Please contact us with any questions:

Yujie Cui (YujieCui@pku.edu.cn)

Code updated: December 7, 2020

README updated: November 1, 2021

======================================================================

**IMPORTANT NOTE:**  
1. This code is distributed under GPLv3 license.  Please see LICENSE file for
the details of the license.
2. If you use this code in original or modified version as part of
a scientific publication, be it a paper, journal article, demonstration, or 
similar work, we ask you to cite our paper.
```bibtex
@inproceedings{cui2022abusing,
  title={Abusing Cache Line Dirty States to Leak Information in Commercial Processors},
  author={Cui, Yujie and Yang, Chun and Cheng, Xu},
  booktitle={2022 IEEE International Symposium on High-Performance Computer Architecture (HPCA)},
  pages={82--97},
  year={2022},
  organization={IEEE}
}
```



**Requirements:**  
1. The code is tested on Ubuntu 16.04 with gcc 5.4. But it should work on other
linux distributions.
2. If you want to run on Windows, you will want to replace some functions. Good luck!
3. To test hyper-threaded sharing, you must use a machine with a processor that
has SMT feature enabled.
4. python 3.x, library e.g., matplotlib, numpy
5. We tested on a private cloud server (**Intel(R) Xeon(R) CPU E5-2650 v4** ) and a public cloud server (**Amazon EC2 M4.large**). 
6. Some other microarchitectures exhibit different behavior (such as using MSHR to hold loaded data and pass it directly to the CPU, or using buffer to hold data to be written back). If you want to run on other processor models, you may need to make modifications.


======================================================================  

Step 1: Preparations

--------------------------------------------------------------------------------
Step 1.0: check hyper-threaded sharing of your processor:

1. $ `lscpu --extend`

2. And find two *CPU* ids that share the same *Core* id.

3. For example, on Xeon(R) CPU E5-2650 with 24 cores, CPU 3 and 27 share the same
physical core.


Step 2: Covert channel

--------------------------------------------------------------------------------
Step 2.1: covert channel using binary encode under Hyper-threaded sharing:
(in ./binary-encode)

----------------
Step 2.1.1: Bind sender and receiver to two hyper-threads of the same physical
core:

$ `cd ./binary-encode`

Important:
* Now you should get two CPU ids that share the same physical core from step 1.0
and change line 269 and line 270 of ./binary-encode/main.c with the
two CPU ids:  
  `CPU_SET(3,&receiver_set);`  
  `CPU_SET(27,&sender_set);`

* E.g., on Xeon(R) CPU E5-2650 with 24 cores, CPU 3 and 27 share the same physical
core. So we let the sender run on CPU 27 and the receiver run on CPU 3.


----------------
Step 2.1.2: compile and run both the sender program and the receiver program
in parallel:

$ `make`

Code Usage:

Sender:
`./WBattack sender sender_mode sender_period_Ts   sender_parameter_d` (sender_parameter_d represents the number of dirty cache lines used.)

Receiver:
`./WBattack receiver  receiver_period_Tr`    

For details on the sender's operations and the receiver's operations, please
read Section IV of the paper.

----------------
Step 2.1.3: sender sends bit strings:

Open two terminals, first, in terminal 1:

$ `./WBattack sender a 11000 8`

Then, in terminal 2:

$ `./WBattack receiver 11000 >a_d=8_t=11000`

In this example, the sender program will send 0 and 1 alternatively every 11000 cycles and 
the receiver will take 100000 measurements every 11000 cycles. 

After the receiver program finishes, you can kill the sender program.



Open two terminals, first, in terminal 1:

$ `./WBattack sender r 11000 8`

Then, in terminal 2:

$ `./WBattack receiver 11000 >r_d=8_t=11000`

In this example, the sender program will send a random string every 11000 cycles and 
the receiver will take 100000 measurements every 11000 cycles. 

After the receiver program finishes, you can kill the sender program.



Info:
* Now you can watch the results in the `a_d=8_t=11000` and `r_d=8_t=11000` files. The `a_d=8_t=11000` file is the result that the sender process alternately sends 0 and 1, and the receiver process observes. Since the sender is transmitting `0` and `1` alternately, you can see that high delay and low delay alternately appear. Through this you can determine the threshold on your machine. The `r_d=8_t=11000` file is the result of a random string sent by the sender process and observed by the receiver process.
* Files such as `sample-a_d=8_t=11000` are sample files that can be used as reference.


scripts:
* The `print_decode_results.py` script exists in this directory to print out the decoded results of the receiver.
* You can try the sample file first to observe the correct output:
  * `python print_decode_results.py --file_path=sample-a_d=8_t=11000 --Threshold=149`  
    * Execute the above command, the script will output 010101... string. Because the `sample-a_d=8_t=11000` file is the result that the sender process alternately sends 0 and 1, and the receiver process observes.  
  * `python print_decode_results.py --file_path=sample-r_d=8_t=11000 --Threshold=149`  
    * The `r_d=8_t=11000` file is the result of a random string sent by the sender process and observed by the receiver process. According to section V of the paper, the beginning position of the random string is set to a fixed bit pattern (`0000101011110101`). So execute the above command, you will see a random string starting with `0000101011110101`.
  * Now you can change the path to the file you generated, and set the threshold according to your processor.  
  * Note: When the sender process is executed, it will output the string it sent. You can compare the output of the script with the string output of the execution of the sender process.


Tips:

* In [top level path]/plot/ there is a python code to plot the attack trace and solve the bit error rate. Learn how to use these scripts through step 3.
--------------------------------------------------------------------------------




Step 2.2: covert channel using multi-bit encoding under Hyper-threaded sharing:
(in ./multi-bit-encoding)

----------------
Step 2.1.1: Bind sender and receiver to two hyper-threads of the same physical
core:

$ `cd ./multi-bit-encoding`

Important:
* Now you should get two CPU ids that share the same physical core from step 1.0
and change line 277 and line 278 of `./multi-bit-encoding/main.c` with the
two CPU ids:

  `CPU_SET(3,&receiver_set);`

  `CPU_SET(27,&sender_set);`

* E.g., on Xeon(R) CPU E5-2650 with 24 cores, CPU 3 and 27 share the same physical
core. So we let the sender run on CPU 27 and the receiver run on CPU 3.


----------------
Step 2.1.2: compile and run both the sender program and the receiver program
in parallel:

$ `make`

Code Usage:

Sender:  
`./WBattack sender sender_mode sender_period_Ts `  
Receiver:  
`./WBattack receiver  receiver_period_Tr   `

For details on the sender's operations and the receiver's operations, please
read Section IV of the paper.

----------------
Step 2.1.3: sender sends bit strings:

Open two terminals, first, in terminal 1:  

$ `./WBattack sender a 11000`

Then, in terminal 2:  

$ `./WBattack receiver 11000 >a_t=11000`

In this example, the sender program will send 00 01 10 11 alternatively every 11000 cycles and 
the receiver will take 100000 measurements every 11000 cycles. 

After the receiver program finishes, you can kill the sender program.


Open two terminals, first, in terminal 1:  
$ `./WBattack sender r 11000`  

Then, in terminal 2:  
$ `./WBattack receiver 11000 >r_t=11000`

In this example, the sender program will send a random string every 11000 cycles and 
the receiver will take 100000 measurements every 11000 cycles. 

After the receiver program finishes, you can kill the sender program.


Info:
* Now you can watch the results in the a_t=11000 and r_t=11000 files. 
Files such as `sample-a_t=11000` are sample files that can be used as reference.

scripts:
* The `print_decode_results.py` script exists in this directory to print out the decoded results of the receiver.
* You can try the sample file first to observe the correct output:
  * `python print_decode_results.py --file_path=sample-a_t=11000`  
    * Execute the above command, the script will output 00 01 10 11 00 01 10 11 ... string. Because the `sample-a_t=11000` file is the result that the sender process alternately sends `00 01 10 11`, and the receiver process observes.  
  * `python print_decode_results.py --file_path=sample-r_t=11000`  
    * The `r_d=8_t=11000` file is the result of a random string sent by the sender process and observed by the receiver process. According to section V of the paper, the beginning position of the random string is set to a fixed bit pattern (`0010001011011101`). So execute the above command, you will see a random string starting with `00 10 00 10 11 01 11 01`.
  * Now you can change the path to the file you generated. Since decoding in multi-bit transmission requires multiple thresholds, you should modify the thresholds in the script(`ThresHold` variable in the script.).
  * Note: When the sender process is executed, it will output the string it sent. You can compare the output of the script with the string output of the execution of the sender process.


----------------
Step 3: Run scripts:

Tips:
* In [top level path]/plot/ there is a python code to plot the attack trace and solve the bit error rate.  
* plots/
    * binary_encode.py : Scripts related to binary encoding
    * multi_bits_encoding.py: Scripts related to multi-bit encoding


* Instructions:
    * `python binary_encode.py  -h` :      Get the usage parameters of the script
    * `python multi_bits_encoding.py -h` : Get the usage parameters of the script
    * Using the following scripts will require some python package support. E.g: matplotlib


* Instructions examples
  * Draw the sequence observed by the receive.
  * According to the paper: the first 16 bits of the random sequence are set to a fixed value for the receiver to identify. (For random sequences, the following script draws these fixed bits.).
  *  You can first use the sample data to plot the sequence of the receiver’s observations. You can run the following example commands directly. 
     * `python binary_encode.py  --draw_fig --file_path=../binary-encode/sample-a_d=8_t=11000  --fig_name="figures/sample-alter-oneBit_d=8"   --Threshold=149`
     * `python binary_encode.py  --draw_fig --file_path=../binary-encode/sample-r_d=8_t=11000  --fig_name="figures/sample-random-oneBit_d=8"   --Threshold=149`
     * `python multi_bits_encoding.py --draw_fig --file_path=../multi-bit-encoding/sample-a_t=11000  --fig_name="figures/alter-multi-encoding"`
     * `python multi_bits_encoding.py --draw_fig --file_path=../multi-bit-encoding/sample-r_t=11000  --fig_name="figures/random-multi-encoding"`

  * After executing the above command, you can see the corresponding picture in the `figures` directory. Through these pictures, you can understand the expected data. Then you can change the path above to the data you obtained through the steps above. 

  * Solve for bit error rate (Wait patiently for a while)
    * `python binary_encode.py  --error_rate --file_path=../binary-encode/sample-r_d=8_t=11000    `
    * `python multi_bits_encoding.py --error_rate  --file_path=../multi-bit-encoding/sample-r_t=11000`

  * You can’t simply change the path to your path to get the bit error rate. Before you solve the bit error rate, you need to make some specific modifications according to your situation.
* **Importantly:**
  * You need to change the threshold in the script according to your own machine. In the case of binary encoding, the threshold can be set in the command line parameter. In the case of multi-bit encoding, there are multiple thresholds, and you need to modify the script.
  * The file name of the data you get needs to be set to a specific format so that the script can get the transfer rate. For binary encoding, the file name should be similar to `r_d=3_t=800`. Among them, `r` means that the sender sends a random sequence; `d=3` means that the sender uses three dirty cache lines for encoding; `t=800` represents the transmission period. For multi-bit encoding, the file name should be similar to `r_t=1100`. Among them, `r` means that the sender sends a random sequence; `t=1100` represents the transmission period. You can modify the number of dirty cache lines used by various encoding symbols in the source code.
  * More importantly, you need to modify the correct string in the script.
    * According to Section V of the paper, the sender repeatedly sends a random string. The receiver restores the string according to the measured time delay. When measuring the bit error rate, the script will measure the edit distance between the string sent by the sender(`correct_str` variable  in the script) and the string restored by the receiver.
    * You should modify `correct_str` variable to the string sent by the sender process when you execute the sender process. Otherwise you may get a bit error rate of about 50%.
    * When you run the sender process as described in 2.1.2, it will print out the string it sends. You need to assign this string to the `correct_str` variable in the python scripts.
   *  The frequency of the CPU on my server is 2.2GHz. You should modify the `cpu_freq` variable in the python scripts to the frequency of the CPU you are using.

* Acknowledgement
  * We would like to thank the authors of the LRU channel [44], especially Wenjie Xiong. Thanks for her willingness to open her source code and the help provided. 
  * Special thanks to Dong Tong for his suggestions, writing and revision guidance on the paper
