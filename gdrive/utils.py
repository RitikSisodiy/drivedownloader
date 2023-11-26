import requests
import threading
import json
from tqdm import tqdm
import time

class Drive:
    def __init__(self,creds) -> None:
        self._creds = json.loads(creds)
        self.session = requests.session()
        self.expired = 0
        self.access_token = ""
    def get_access_token(self):
        if self.expired > time.time():
            return self.access_token
        payload = {
            "refresh_token": self._creds["refresh_token"],
            "client_id": self._creds["client_id"],
            "client_secret": self._creds["client_secret"],
            "grant_type": "refresh_token"
        }
        response = self.session.post(self._creds["token_uri"], data=payload)

        # Parse the response
        assert response.status_code == 200
        response =  response.json()
        self.access_token =response["access_token"]
        self.expired = time.time() + response["expires_in"]
        return self.get_access_token()
    def upload_chunks(self,location,chunk,headers):
        self.session.put(location, headers=headers, data=chunk)
    def ini_file(self,filename):
        headers = {'Authorization': 'Bearer ' + self.get_access_token(),
           'Content-Type': 'application/json'}
        parameters = {'name': filename,
                'description': 'uploaded by machine.'}
        r = requests.post('https://www.googleapis.com/upload/drive/v3/files?uploadType=resumable'
                        , headers=headers, data=json.dumps(parameters))
        return r.headers['location']
# Parse the response

def get_num_chunks(url, max_chunks=8):
    response = requests.head(url)
    accept_ranges = response.headers.get('Accept-Ranges')
    return 1
    if accept_ranges == 'bytes':
        # Server supports partial content downloads
        return min(max_chunks, 8)  # Set an upper limit on the number of chunks
    else:
        # Server does not support partial content downloads
        return 1

def download_chunk(url, start_byte, end_byte,file_size, chunk_number,location, drive_ob,progress_bar,Downloadingob):
    headers = {'Range': f'bytes={start_byte}-{end_byte}'}
    response = requests.get(url, headers=headers, stream=True)
    chunk_size = 4980736  # 1 KB
    # chunk_size = 1024*1024*1  # 1 KB

    for data in response.iter_content(chunk_size=chunk_size):
        csize =  len(data)
        sbyte = start_byte
        ebyte = start_byte +csize-1
        headers =  {'Content-Length': str(csize),
        'Content-Range': 'bytes ' +str(sbyte) \
        + '-' + str(ebyte) + '/' + str(file_size)}
        drive_ob.upload_chunks(location,data,headers)
        # file.write(data)
        start_byte += csize
        progress_bar.update(len(data))
        Downloadingob.progress = str(progress_bar.n/progress_bar.total*100)[:5]
        Downloadingob.save()
        # break
    progress_bar.set_postfix(chunk=chunk_number)
    print(f"Chunk {chunk_number} downloaded.")

def download_file(url, max_chunks=8, output_file='downloaded_file.txt',Downloadingob=None):
    num_chunks = get_num_chunks(url, max_chunks)
    response = requests.head(url)
    file_size = int(response.headers['Content-Length'])
    chunk_size = file_size // num_chunks

    drive_ob = Drive(Downloadingob.user.driveModel.json)
    filename = url.split("?")[0]
    filename = filename[filename.rfind("/")+1:]
    location = drive_ob.ini_file(filename)
    Downloadingob.filename = filename
    Downloadingob.save()
    threads = []
    total_progress = tqdm(total=file_size, unit='B', unit_scale=True, desc='Downloading', position=0, leave=True)

    for i in range(num_chunks):
        start_byte = i * chunk_size
        end_byte = start_byte + chunk_size - 1 if i < num_chunks - 1 else file_size 
        thread = threading.Thread(target=download_chunk, args=(url, start_byte, end_byte,file_size, i,location,drive_ob, total_progress,Downloadingob))
        threads.append(thread)
        thread.daemon = True
        thread.start()

    for thread in threads:
        thread.join()

    total_progress.close()
    print("Download complete.")

# if __name__ == "__main__":
#     file_url = "https://example.com/example_file.zip"
#     download_file(file_url)

if __name__ == "__main__":
    file_url = "https://az764295.vo.msecnd.net/stable/1a5daa3a0231a0fbba4f14db7ec463cf99d7768e/VSCodeUserSetup-x64-1.84.2.exe"
    download_file(file_url,output_file="VSCodeUserSetup-x64-1.84.2.exe")