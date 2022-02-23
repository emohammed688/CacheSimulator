import math
import sys
import time

######################################################################
#                   Start of helper functions
######################################################################
    
# Get immediate value
def getCorrectImm(immBin):
    # print(immBin)
    imm = int(immBin,2)     # Convert bin to int
    # print(imm)
    if immBin[0] == '1':    # Take 2's complement if number was negative
        imm = imm - (1 << 16)
    # print(imm)
    return imm

######################################################################
#                   End of helper functions
######################################################################

######################################################################
#                       Main code
######################################################################

import fileinput

print("Enter Cache Configuration : ")
ways = int(input("Enter number of ways : ")) #number of ways in the cache
sets = int(input("Enter number of sets : ")) #number of sets
lines = int(input("Enter block size in bytes : ")) #block size of cache line

cache_sim = []  #empty cache simulator
linesInCache = sets*ways    #find all lines in a cache
linesInSet = round(linesInCache/sets)    #find all lines in a set

cache_sim = [[0,0,0,0,0,0,0] for i in range(linesInCache)]

string = ''         #for log file

counter = 0
curSet = 0
curWay = 0

for i in range(linesInCache):
    cache_sim[i][0] = curSet #current set value
    cache_sim[i][1] = curWay #current way value
    cache_sim[i][2] = "tag"
    cache_sim[i][4] = "LRU/write back"
    cache_sim[i][6] = 0
    counter = counter + 1
    curWay = curWay + 1
    if (counter == linesInSet):
        counter = 0
        curSet = curSet + 1
        curWay = 0

#initialize values for cache access and cache misses
access = 0
miss = 0

# Instruction memory
inst_mem = []

# Store Instructions from file into Instruction memory
for line in fileinput.input(files ='input.txt'):
    inst_mem.append(line)
    
# # Print Instruction memory
# print('Instruction memory')
# print(inst_mem)

# Define 4 registers
no_of_reg = 32
registers = [0] * no_of_reg
# Data memory
size_of_dm = 65536 
data_mem = [0] * size_of_dm

# set program counter to start
pc = 0
dc = 0

print('\nStarting the program\n')
while int(pc/4) < len(inst_mem) :
    
    instInHex = inst_mem[int(pc/4)]
    instInBin = bin(int(instInHex, 16))[2:].zfill(32)
    opcode = instInBin[:6]

    rs = int(instInBin[6:11],2)
    rt = int(instInBin[11:16],2)
    rd = int(instInBin[16:21],2)
    imm = int(instInBin[16:],2)
        
    if opcode == "100000" or opcode == "101000":          
        access = access + 1
        hit = 0
        full = 0

        if opcode == "100000":                          # Load
            registers[rt] = data_mem[registers[rs]+getCorrectImm(bin(imm)[2:].zfill(8))]

            lineAddress = registers[rt]                                            
            offset = lineAddress & (lines - 1)                                    
            setIx = lineAddress >> int(math.log(lines, 2)) & (sets - 1)           
            tag = lineAddress >> (int(math.log(sets,2)) + int(math.log(lines,2))) 
       
            print("--------------------------------")
            print("Address = ", lineAddress)
            print("Offset = ", offset)
            print("Set = ", setIx)
            print("Tag = ", tag)

            string = string+'--------------------------------\n'
            string = string+'Address = '+str(lineAddress)+'\n'
            string = string+'Offset = '+str(offset)+'\n'
            string = string+'Set = '+str(setIx)+'\n'
            string = string+'Tag = '+str(tag)+'\n'

            firstRow = linesInSet * int(setIx)
            for i in range(firstRow, firstRow + linesInSet):
                if(cache_sim[i][6] == 1 and cache_sim[i][2] == tag):     #check for a hit
                    hit = 1                                              
                    cache_sim[i][5] = time.time()                        #record access stamp
                    print("Hits = ", access-miss)
                    print("Way matched = ", cache_sim[i][1])
                    string = string+'Hits = '+str(access-miss)+'\n'
                    string = string+'Way matched = '+str(cache_sim[i][1])+'\n'
                    break

            full = 1                     
            maxTimeConstant = sys.maxsize 
            maxRow = -1                   

            #read miss
            if(hit == 0):
                miss = miss + 1
                print("Miss = ", miss)
                string = string+'Miss = '+str(miss)+'\n'
                for i in range(firstRow, firstRow + linesInSet):
                    if(cache_sim[i][3] == 0):           #Check for full set
                        full = 0
                        break
                    if(cache_sim[i][5] < maxTimeConstant):
                        maxTimeConstant = cache_sim[i][5]       #add new access time
                        maxRow = i
                if(full == 0):                        #set is to be filled
                    cache_sim[i][2] = tag
                    cache_sim[i][3] = 1
                    cache_sim[i][4] = "LRU" 
                    cache_sim[i][5] = time.time()
                    cache_sim[i][6] = 1
                else:                                 #set is full
                    cache_sim[maxRow][2] = tag
                    cache_sim[maxRow][3] = 1
                    cache_sim[maxRow][4] = "LRU"
                    cache_sim[maxRow][5] = time.time() 
                    cache_sim[maxRow][6] = 1
            
            string = string+'\n'
            print()
        
        elif opcode == "101000":                            # Store
            data_mem[registers[rs]+getCorrectImm(bin(imm)[2:].zfill(8))] = 255 & registers[rt]

            lineAddress = data_mem[registers[rs]+getCorrectImm(bin(imm)[2:].zfill(8))]                                      
            offset = lineAddress & (lines - 1)                                           #calculate offset using address and block size
            setIx = lineAddress >> int(math.log(lines, 2)) & (sets - 1)                  #calculate set index using address, block size and number of sets in cache
            tag = lineAddress >> (int(math.log(sets,2)) + int(math.log(lines,2)))        #calculate tag using address, block size and number of sets in cache
       
            print("--------------------------------")
            print("Address = ", lineAddress)
            print("Offset = ", offset)
            print("Set = ", setIx)
            print("Tag = ", tag)         

            string = string+'--------------------------------\n'
            string = string+'Address = '+str(lineAddress)+'\n'
            string = string+'Offset = '+str(offset)+'\n'
            string = string+'Set = '+str(setIx)+'\n'
            string = string+'Tag = '+str(tag)+'\n'

            firstRow = linesInSet * int(setIx)
            for i in range(firstRow, firstRow + linesInSet):
                if(cache_sim[i][6] == 1 and cache_sim[i][2] == tag): #check for hit
                    cache_sim[i][2] = tag
                    cache_sim[i][3] = 1
                    cache_sim[i][4] = "write back"
                    cache_sim[i][5] = time.time()
                    hit = 1
                    print("Hits = ", access-miss)
                    print("Way matched = ", cache_sim[i][1])
                    string = string+'Hits = '+str(access-miss)+'\n'
                    string = string+'Way matched = '+str(cache_sim[i][1])+'\n'
                    break
             
            full = 1                        #set is full
            maxTimeConstant = sys.maxsize   #constant to check access time against
            maxRow = -1                     #sets simulator index to last value

            #write miss
            if(hit == 0):
                miss = miss + 1
                print("Miss = ", miss)
                string = string+'Miss = '+str(miss)+'\n'
                for i in range(firstRow, firstRow + linesInSet):
                    if(cache_sim[i][3] == 0):           #check for full set
                        full = 0
                        break
                    if(cache_sim[i][5] < maxTimeConstant):
                        maxTimeConstant = cache_sim[i][5] #add new access time
                        maxRow = i
                if(full == 0):                        #set is to be filled
                    cache_sim[i][2] = tag
                    cache_sim[i][3] = 1
                    cache_sim[i][4] = "LRU"
                    cache_sim[i][5] = time.time()
                    cache_sim[i][6] = 1
                else:                                 #set is full
                    cache_sim[maxRow][2] = tag
                    cache_sim[maxRow][3] = 1
                    cache_sim[maxRow][4] = "LRU"
                    cache_sim[maxRow][5] = time.time()
                    cache_sim[maxRow][6] = 1

            string = string+'\n'
            print()

        pc = pc+4
        dc = dc+1
        
    elif opcode == "000000":        #R-type instructions     
        
        if instInBin[-6:] == "100000":            # ADD
            registers[rd] = (registers[rs] + registers[rt])
            pc = pc+4
            dc = dc+1
        
        elif instInBin[-6:] == "100010":          # SUB
            registers[rd] = (registers[rs] - registers[rt])
            pc = pc+4
            dc = dc+1

        elif instInBin[-6:] == "101010":          # SLT
            if(registers[rs] < registers[rt]):
                registers[rd] = 1
            else:
                registers[rd] = 0
            pc = pc+4
            dc = dc+1

        elif instInBin[-6:] == "100110":          # XOR
            registers[rd] = (registers[rs] ^ registers[rt] )
            pc = pc+4
            dc = dc+1

    elif opcode == "001000":          # ADDI
        registers[rt] = (registers[rs] + getCorrectImm(bin(imm)[2:].zfill(8)))
        pc = pc+4
        dc = dc+1
        
    elif opcode == "000100":          # BEQ
        
        if registers[rs] == registers[rt]:
            pc = ( pc + (getCorrectImm(bin(imm)[2:].zfill(8))<<2) + 4)
        else:
            pc = pc+4
        dc = dc+1
        
    elif opcode == "000101":          # BNE
        
        if registers[rs] != registers[rt]:
            pc = ( pc + (getCorrectImm(bin(imm)[2:].zfill(8))<<2) + 4)
        else:
            pc = pc+4
        dc = dc+1
        
    else:
        print("Invalid instruction")
        print("Terminating the program....")
        break
    
# End while

file = open('log.txt', 'w')
file.write(string)
file.close()

#print cache performance values
print("Total Access = ", str(access))
print("Total Hits = ", str(access-miss))
print("Total Miss = ", str(miss))

ratePercentage = miss/access
rate = ratePercentage * 100

print("Cache miss rate: {:0.2f}%".format(rate, 2))

print()