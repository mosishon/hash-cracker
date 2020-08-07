from concurrent.futures import ThreadPoolExecutor
from colorama import Fore,Style
from time import sleep
import sys
import hashlib
import os
import time
#For Test 
# Hash : 8b1a9953c4611296a827abf8c47804d7 String : Hello
FINDED = False
HASH_FIND = ''
THE_HASH = ''
COUNTER = 0
WORDS = []
def crack(hash,type):
    hash = hash.replace("\n","").strip()
    encoded = hash.encode("utf8")
    x = eval(f'hashlib.{type}({encoded}).hexdigest()')
    #print(f" {THE_HASH} == {x} == {hash}")
    global COUNTER
    COUNTER +=1
    if str(THE_HASH).strip() == str(x).strip():
        global FINDED
        global HASH_FIND
        FINDED = True
        HASH_FIND = hash
        return True
    return False

def cracking(type):
    global FINDED
    while not FINDED:
        global WORDS
        hash = WORDS.pop(0)
        if hash == '':
            break 
        res = crack(hash,type)
        if res == True:
            break





TYPES = {"32":"md5","64":"sha256"}
def main():
    INFO = f"{Fore.BLUE}[!] "
    ERROR = f"{Fore.RED}[-] "
    SUCCESS = f"{Fore.GREEN}[+] "
    print(f"""
    {INFO}Welcome To Hash Cracker!
    {INFO}Developer : @beQrity
    """)
    max_worker = input(f"{INFO}Enter Max Worker Number >>")
    while 1:
        if max_worker.isnumeric() and int(max_worker) >=1:
            break
        max_worker = input(f"{ERROR}Enter a Number nigger than 1 >>")

    TPE = ThreadPoolExecutor(int(max_worker) if int(max_worker)<=30 else 30)
    file_name = input(f"{INFO}Enter Wordlist path >>")
    while 1:
        if not os.path.exists(file_name) or not os.path.isfile(file_name):
            file_name = input(f"{ERROR}File Not Found! Enter a valid file path >")
        else:
            break

    global THE_HASH
    THE_HASH = input(f"{INFO}Enter hash >>")
    TYPE = TYPES.get(str(len(THE_HASH)))
    if TYPE:
        acc = input(f"{INFO}hash type is {TYPE} ? (Y/n)")
        if acc.lower() not in ("y","Y","","\n"):
            TYPE = input(f"{INFO}Enter hash type >>")
    while 1:
        if TYPE not in dir(hashlib):
            TYPE = input(f"{ERROR}Hash type not found enter a valid hash type >>")
        else:
            break
    print(f"{SUCCESS}Hash type is {TYPE}")
    open(file_name,"a+").write("\n")
    global WORDS
    WORDS= open(file_name).readlines()

    before = time.time()
    ts = [TPE.submit(cracking,TYPE) for i in range(int(max_worker))]
    while 1:
        sys.stdout.flush()
        sys.stdout.write(f"\r{SUCCESS}{Style.BRIGHT}{COUNTER}{Style.NORMAL} Word Checked")
        res = [t.done() for t in ts]
        if not False in res:
            break
    after = time.time()
    global FINDED
    
    if FINDED:
        print(f"\n{SUCCESS}Hash Cracked -> {Fore.WHITE}{Style.BRIGHT}{HASH_FIND}{Style.NORMAL}\n")
    else:
        print(f"\n{ERROR}Hash Not Found !")
    print(f"\n{INFO}in {Fore.YELLOW}{Style.BRIGHT}{after-before} {Fore.BLUE}{Style.NORMAL}Secounds\n\n\n")
try:
    main()
except KeyboardInterrupt:
    sys.exit()
