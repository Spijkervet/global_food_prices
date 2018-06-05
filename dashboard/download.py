from tqdm import tqdm
import requests
import math



def download(url, file_name):
    r = requests.get(url, stream=True)

    total_size = int(r.headers.get('content-length', 0)); 
    block_size = 1024
    written = 0 

    print("Downloading dataset")
    with open(file_name, 'wb') as f:
        for data in tqdm(r.iter_content(block_size), total=math.ceil(total_size//block_size) , unit='KB', unit_scale=True):
            written = written  + len(data)
            f.write(data)

    if total_size != 0 and written != total_size:
        print("ERROR, something went wrong")  
    else:
        print("Successfully downloaded the dataset")
