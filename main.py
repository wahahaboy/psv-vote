import requests,json,base64,urllib,re,threading,time,asyncio
from CAPTCHA_object_detection import *

#class ACE():
#        def get_answer(self, img_base64):
#                try:
#                        imgdata = base64.b64decode(img_base64)
#                        filename = id+'.png'
#                        with open(filename, 'wb') as f:
#                                f.write(imgdata)
#                        solvedText = Captcha_detection(filename)
#                        #print(image['solvedText'])
#                        return image['solvedText']
#                except Exception as e:
#                        return False


class PLAYSERVER():
        def get_image(self, proxy):
                try:
                        rid = requests.post(self.update_psv["getimage"], headers=self.update_psv["header"],proxies=proxy).json()
                        IMAGE_ID = rid['checksum']
                        IMAGECT = requests.get(self.update_psv["u_image"] + IMAGE_ID, headers=self.update_psv["header"],proxies=proxy)
                        base64pic = base64.b64encode(IMAGECT.content).decode('utf-8')
                        if base64pic.find('iVBORw0KGgoAAAANSUhE') > -1:
                                IMAGE = {'id':IMAGE_ID,'base64':base64pic}
                                return IMAGE
                        else:
                                return False
                except Exception as e:
                        return False
        def post_image(self, data_vote, proxy):
                try:
                        vote = requests.post(self.update_psv["submit"],headers=self.update_psv["header"],data=data_vote,proxies=proxy).json()
                        return vote
                except Exception as e:
                        return False
        
class MAIN(PLAYSERVER):
        def __init__(self,config):
                self.config = config
                self.update_psv = {
                "u_server" : "https://playserver.in.th/index.php/Server/",
                "u_vote" : "https://playserver.in.th/index.php/Vote/prokud/",
                "u_image" : "http://playserver.co/index.php/VoteGetImage/",
                "cb_vote" : "http://playserver.in.th/index.php/Vote/prokud/",
        }

        def _update_psv(self):
                try:
                        unpack1 = requests.get(self.update_psv["u_server"]+self.config['SERVERID'])
                        unpack2 = re.search(self.update_psv["u_vote"]+'(.+?)"',unpack1.text)
                        unpack_unicode = (unpack2.group(1))
                        unpack_fn = urllib.parse.quote(unpack_unicode)
                        self.update_psv["getimage"] =  ("http://playserver.co/index.php/Vote/ajax_getpic/"+unpack_fn)
                        self.update_psv["submit"] = ("http://playserver.co/index.php/Vote/ajax_submitpic/"+unpack_fn)
                        self.update_psv["header"] = {
                                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36",
                                "Content-Type":"application/x-www-form-urlencoded; charset=UTF-8",
                                "Connection": "keep-alive",
                                "Accept-Encoding": "gzip, deflate",
                                "Referer": (self.update_psv["cb_vote"]+unpack_fn)
                        }
                except:
                        print("check your sever id !!")

        def loop_vote(self, proxy):
                next_time = None
                dle_time = 0
                while True:
                        try:
                                b = self.get_image(proxy)
                                if b:
                                        #solvedText = self.get_answer(b['base64'])
                                        imgdata = base64.b64decode(b['base64'])
                                        filename = b['id']+'.png'
                                        with open(filename, 'wb') as f:
                                                f.write(imgdata)
                                        time.sleep(2)
                                        solvedText = Captcha_detection(filename)
                                        time.sleep(4)
                                        os.remove(b['id']+'.png')
                                        time.sleep(2)
                                        if next_time:
                                                get_time = time.time()
                                                if get_time - dle_time < next_time:
                                                        tiem_x = int(get_time - dle_time)
                                                        time.sleep(next_time-tiem_x)
                                        data_vote = {'server_id':self.config['SERVERID'] ,'captcha': solvedText, 'gameid': self.config['USERID'], 'checksum': b['id']}
                                        c = self.post_image(data_vote, proxy)
                                        if c:
                                                next_time = int(c["wait"])
                                                dle_time = time.time()
                                                print(c)
                                                #print(b['id'],solvedText)
                                                print("==============================")
                                                #if c['error_msg'] == 'รหัสในภาพไม่ถูกต้อง ลองใหม่':
                                                    #filename = '_error_'+b['id']+'.png'
                                                    #with open(filename, 'wb') as f:
                                                        #f.write(imgdata)
                                                    #time.sleep(2)
                                else:
                                        break
                        except Exception as e:
                                return False
        
        def auto_vote(self):
                with open('proxy.txt', 'r') as fp:
                        loop = asyncio.get_event_loop()
                        check = []
                        px = fp.read().splitlines()
                        for x in px:
                                if x not in check:
                                        check.append(x)
                                        proxies = {'http': ('http://'+x),'https': ('https://'+x), 'ftp': ('ftp://'+x)}
                                        thread = threading.Thread(target=self.loop_vote, args=(proxies,)).start()
        
if __name__ == "__main__":
        config = None
        with open('config.json', 'r') as config_paser:
                config = json.load(config_paser)
        c = MAIN(config)
        c._update_psv()
        c.auto_vote()
