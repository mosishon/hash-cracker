import hashlib
import os
import hashlib
import multiprocessing
import threading
from concurrent import futures
import datetime

def detect_hash_type(string: str) -> str:
    """
    Detect the type of hash that the given string is.
    
    Parameters:
    - string: str
        The input string that may be a hash.
    
    Returns:
    - str
        A string representing the type of hash that the input string is. If the input string is not a hash, returns the string "Not a hash."
    
    Example:
    >>> detect_hash_type("5f4dcc3b5aa765d61d8327deb882cf99")
    'MD5'
    >>> detect_hash_type("$2y$10$X9.C8/O/dI2.Ie5MlNkW8OXPaEZ/hIR1chK5GLxz5j5c5whJz5A5G")
    'Bcrypt'
    >>> detect_hash_type("hello world")
    'Not a hash.'
    """
    if len(string) == 32:
        return "MD5"
    elif len(string) == 40:
        return "SHA1"
    elif len(string) == 56:
        return "SHA224"
    elif len(string) == 64:
        return "SHA256"
    elif len(string) == 96:
        return "SHA384"
    elif len(string) == 128:
        return "SHA512"
    elif string.startswith("$2y$"):
        return "Bcrypt"
    else:
        return "Not a hash."


def make_hash_and_check(words,hash_to_match, algorithm,rd):
    """
    This function takes a word and a hashing algorithm as input and returns the hash of the word using the specified algorithm.
    """
    founded = False
    algorithm = algorithm.lower()
    for word in words:
        if rd['done'] == True:
            return None
        if algorithm == "md5":
            maked_hash = hashlib.md5(word.encode()).hexdigest()
            if maked_hash.strip() == hash_to_match.strip():
                founded = maked_hash
                break
                
        elif algorithm == "sha1":
            maked_hash = hashlib.sha1(word.encode()).hexdigest()
            if maked_hash == hash_to_match:
                founded = maked_hash
                break
        elif algorithm == "sha256":
            maked_hash = hashlib.sha256(word.encode()).hexdigest()
            if maked_hash == hash_to_match:
                founded = maked_hash
                break
        elif algorithm == "sha512":
            maked_hash = hashlib.sha512(word.encode()).hexdigest()
            if maked_hash == hash_to_match:
                founded = maked_hash
                break
        else:
            return ["Invalid algorithm",False]
    if founded:
        rd['done'] = True
        rd['res'] = [word,founded,os.getpid(),threading.current_thread().native_id]
        return [word,founded,os.getpid(),threading.current_thread().native_id]
    else:
        return -1


def future_done(f,executor:futures.ThreadPoolExecutor):
    global processes
    if f.done() and not f.cancelled() and f.result() != -1:
        executor.shutdown(False,cancel_futures=True)
            
            
        
def check_hash_match(words, hash_to_match, algorithm,return_dict):
    """
    This function takes a list of words, a hash to match, and a hashing algorithm as input.
    It returns a list of words whose hash matches the given hash using the specified algorithm.
    """
    chunk_size = len(words) // 2
    
    if chunk_size ==0:
        return
    chunks = (tuple(words[i:i+chunk_size]) for i in range(0, len(words), chunk_size))
    with futures.ThreadPoolExecutor(max_workers=5) as executor:
        future_to_url = {executor.submit(make_hash_and_check, chunk, hash_to_match, algorithm,return_dict): hash_to_match for chunk in chunks}
        for f in future_to_url:
            f.add_done_callback(lambda x:future_done(x,executor))
            
        for future in futures.as_completed(future_to_url):
            hash_to_match = future_to_url[future]
            try:
                data = future.result()
                if data != -1:
                    return_dict[str(os.getpid())] = data
                    return_dict['done'] = True
                    return
            except Exception as exc:
                print('%r generated an exception: %s' % (hash_to_match, exc))

        


def process_words(words, hash_to_match, algorithm):
    """
    This function takes a list of words, a hash to match, and a hashing algorithm as input.
    It divides the list of words into chunks and processes each chunk in a separate process using the check_hash_match function.
    """
    core_count = 1
    if len(words)>1_000_000:
        core_count = 2
    if len(words)>5_000_000:
        core_count = 3
    if len(words) >10_000_000:
        core_count = os.cpu_count()
    chunk_size = len(words) // core_count

    chunks = (tuple(words[i:i+chunk_size]) for i in range(0, len(words), chunk_size))
    
    processes = []
    return_dict['done'] = False
    print(f"START ON {datetime.datetime.now().strftime('%d-%m-%Y-%T')}")
    print(f"[!]Checking {chunk_size} word per process({core_count}). and {chunk_size//2} per thread(2 thred per process)")
    for chunk in chunks:
        process = multiprocessing.Process(target=check_hash_match, args=(chunk, hash_to_match, algorithm,return_dict))
        processes.append(process)
        process.start()
    for process in processes:
        process.join()
    print(return_dict)
    k = 'res'
    print(f"Hash: {return_dict[k][1]}\nword: {return_dict[k][0]}\nfind by: pid->{return_dict[k][2]}&threadId->{return_dict[k][3]}")

if __name__ == "__main__":

    # Create Storage to share data between processes
    manager = multiprocessing.Manager()
    return_dict = manager.dict()

    multiprocessing.freeze_support()
    hsh = input("Enter Your Hash:")
    #hsh = hashlib.md5(hash_str.encode()).hexdigest()
    htype = detect_hash_type(hsh)
    if htype == "Not a hash.":
        print(f"[!] i can't crack this hash. sorry!")
        exit(1)
    else:
        print(f"[1] Your hash : {hsh}\n[2] Hash type : {htype}")
    wordListPath = input("Enter WordListPath:") 
    print("[!] Reading Word list and Removing duplicates ...")
    words = tuple((i.replace("\n","") for i in open(wordListPath).readlines()))
    process_words(words,hsh,htype)
    print(f"FINISH ON {datetime.datetime.now().strftime('%d-%m-%Y-%T')}")


