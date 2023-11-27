import requests
import threading
import json
from tqdm import tqdm
import time
import re
class Drive:
    def __init__(self,drive_model) -> None:
        self.drive_model = drive_model
        creds = drive_model.json
        self._creds = json.loads(creds)
        self.session = requests.session()
    def get_availabe_space(self):
        url = "https://www.googleapis.com/drive/v3/about?fields=storageQuota"
        response = self.session.get(url,headers=self._get_headers())
        available = response.json()["storageQuota"]
        return round((int(available["limit"]) - int(available["usage"]))/(1024 ** 3),2)
    def get_access_token(self):
        if self._creds.get("expires_in") and self._creds["expires_in"] > time.time():
            return self._creds["access_token"]
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
        self._creds["access_token"] =response["access_token"]
        self._creds["expires_in"] = time.time() + response["expires_in"]
        self.drive_model.json = json.dumps(self._creds)
        self.drive_model.save()
        return self.get_access_token()
    def upload_chunks(self,location,chunk,headers):
        self.session.put(location, headers=headers, data=chunk)
    def _get_headers(self):
        return {'Authorization': 'Bearer ' + self.get_access_token(),
           'Content-Type': 'application/json'}
    def ini_file(self,filename):
        parameters = {'name': filename,
                'description': 'uploaded by machine.'}
        r = self.session.post('https://www.googleapis.com/upload/drive/v3/files?uploadType=resumable'
                        , headers=self._get_headers(), data=json.dumps(parameters))
        return r.headers['location']
# Parse the response

def get_num_chunks(url,session, max_chunks=8):
    response = session.head(url)
    accept_ranges = response.headers.get('Accept-Ranges')
    return 1
    if accept_ranges == 'bytes':
        # Server supports partial content downloads
        return min(max_chunks, 8)  # Set an upper limit on the number of chunks
    else:
        # Server does not support partial content downloads
        return 1

def download_chunk(url,session, start_byte, end_byte,file_size, chunk_number,location, drive_ob,progress_bar,Downloadingob):
    try:
        headers = {'Range': f'bytes={start_byte}-{end_byte}'}
        response = session.get(url, headers=headers, stream=True)
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
            try:
                Downloadingob.progress = str(progress_bar.n/progress_bar.total*100)[:5]
                Downloadingob.save()
                send_by_download_ob(Downloadingob)
            except:
                pass
            # break
        progress_bar.set_postfix(chunk=chunk_number)
        print(f"Chunk {chunk_number} downloaded.")
    except Exception as e:
        Downloadingob.status = f"failed {e}"
        Downloadingob.save()
        send_by_download_ob(Downloadingob)
def download_file(url, max_chunks=8, output_file='downloaded_file.txt',Downloadingob=None):
    try:
        session = requests.session()
        num_chunks = get_num_chunks(url,session, max_chunks)
        response = session.head(url)
        file_size = int(response.headers['Content-Length'])
        chunk_size = file_size // num_chunks
        content_disposition = response.headers.get("Content-Disposition","")
        if "filename=" in content_disposition:
            fn_pattern = 'filename="(.*)"'
            filename = re.findall(fn_pattern,content_disposition)[0]
        else:
            filename = url.split("?")[0]
            filename = filename[filename.rfind("/")+1:]
        drive_ob = Drive(Downloadingob.user.driveModel)
        filename = filename[-1000:]
        location = drive_ob.ini_file(filename)
        Downloadingob.filename = filename
        Downloadingob.status = "in_progress"
        send_by_download_ob(Downloadingob)
        threads = []
        total_progress = tqdm(total=file_size, unit='B', unit_scale=True, desc='Downloading', position=0, leave=True)

        for i in range(num_chunks):
            start_byte = i * chunk_size
            end_byte = start_byte + chunk_size - 1 if i < num_chunks - 1 else file_size 
            thread = threading.Thread(target=download_chunk, args=(url, session,start_byte, end_byte,file_size, i,location,drive_ob, total_progress,Downloadingob))
            threads.append(thread)
            thread.daemon = True
            thread.start()

        for thread in threads:
            thread.join()

        total_progress.close()
        Downloadingob.status = "downloaded"
        Downloadingob.save()
        send_by_download_ob(Downloadingob)
        print("Download complete.")
    except Exception as e:
        Downloadingob.status = f"failed {e}"
        Downloadingob.save()
        send_by_download_ob(Downloadingob)
# if __name__ == "__main__":
#     file_url = "https://example.com/example_file.zip"
#     download_file(file_url)

from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

def send_by_download_ob(Downloadingob):
    sent_to_socket(Downloadingob.user,{
        "id":Downloadingob.id,
        "progress":Downloadingob.progress,
        "filename":Downloadingob.filename,
        "status":Downloadingob.status}
    )
def sent_to_socket(user,message):
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        user.username,
        {
            'type': 'websocket.message',
            'text': json.dumps(message)
        }
    )
if __name__ == "__main__":
    file_url = "https://az764295.vo.msecnd.net/stable/1a5daa3a0231a0fbba4f14db7ec463cf99d7768e/VSCodeUserSetup-x64-1.84.2.exe"
    download_file(file_url,output_file="VSCodeUserSetup-x64-1.84.2.exe")