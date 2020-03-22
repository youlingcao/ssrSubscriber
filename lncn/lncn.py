# -*- coding:UTF-8 -*-
import requests as requests
import json
from Crypto.Cipher import AES
import base64
import subprocess

api_theSSR = 'https://lncn.org/api/SSR'
api_nextUpdateTime = 'https://lncn.org/api/notices'

proxies = {'http': '127.0.0.1:1080', 'https': '127.0.0.1:1080'}
subscribeFile = 'list.txt'

git = 'git'
git_commit_auto = True


def lncn_encrypt(data, key):
    aes = AES.new(str.encode(key), AES.MODE_ECB)  # 初始化加密器
    decrypted_text = aes.decrypt(base64.decodebytes(bytes(data, encoding='utf8'))).decode('utf8')  # 解密
    decrypted_text = decrypted_text[:-ord(decrypted_text[-1])]  # 去除多余补位
    return decrypted_text


def update_git(date, list_ssrUrl):
    # base64 data
    data = ''
    for item in list_ssrUrl:
        data += item + '\n'
    data = base64.encodebytes(bytes(data, 'utf-8')).decode('utf-8').replace('\n', '')
    file = open(subscribeFile, mode='w')
    file.write(data)
    file.close()

    # commit git
    if git_commit_auto:
        subprocess.call([git, 'add', '*'])
        subprocess.call([git, 'commit', '-m', date])
        subprocess.call([git, 'push'])
    return


def gain_data():
    try:
        resp = requests.post(api_theSSR, proxies=proxies)
    except requests.ConnectionError as err:
        print('error', err)
    else:
        print(resp.status_code)
        if resp.status_code == 200:
            print(resp.text)
            json_data = json.loads(resp.text)
            date = json_data['date']
            ssrs = json_data['ssrs']
            if date and ssrs:
                # encrypt data
                ssrs = lncn_encrypt(ssrs, '3912658659499321')
                assert ssrs

                json_ssrs = json.loads(ssrs)
                list_ssrUrl = []
                for item in json_ssrs:
                    if item['ssrUrl']:
                        list_ssrUrl.append(item['ssrUrl'])

                update_git(date, list_ssrUrl)
    return


gain_data()
