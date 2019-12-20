#!/usr/bin/env python3
# -*- coding:utf-8 -*-
###

# Webchat
from WechatPCAPI import WechatPCAPI
import time
import logging
from queue import Queue
import threading, requests, re
from bs4 import BeautifulSoup


logging.basicConfig(level=logging.INFO)
queue_recved_message = Queue()


def on_message(message):
    queue_recved_message.put(message)


# 创建remark_name字典
dict_remark_name = {}
# 定义信息ID字典
dict_msg_ID = {}
# 全局
ID_num = 0


def get_url_coupon_info(url):
    try:
        res = requests.get(url)
        soup = BeautifulSoup(res.text, 'lxml')
        title = soup.title.text
        print(title)
    except:
        title = ''

    if '&' in url:
        url_group = url.split('?')
        param = url_group[1].split('&')
        product = param[0].split('=')
        product_id = product[1]
    else:
        url_group = url.split('?')
        product = url_group[1].split('=')
        product_id = product[1]

    apikey = 'eqYJsXQOcP'
    siteid = '446200449'
    adzoneid = '108517850497'
    uid = '140228417'

    url = 'https://api.taokouling.com/tkl/TbkPrivilegeGet?apikey=' + apikey + '&itemid=' + product_id + '&siteid=' + siteid + '&adzoneid=' + adzoneid + '&uid=' + uid
    se = requests.session()
    res = se.get(url)
    res = res.json()
    print(res)

    # mm_coupon_info situation need to check
    if ('msg' in res and ('下架' in res['msg'] or '非淘宝客' in res['msg'])) or 'coupon_info' not in res['result']['data']:
        res_txt = '''%s
-----------------
该宝贝暂时没有找到内部返利通道！亲您可以换个宝贝试试。        
        ''' % title
    else:
        coupon_info = res['result']['data']['coupon_info']
        coupon_url = res['result']['data']['coupon_click_url']
        res_txt = '''恭喜您，已找到隐藏优惠！！

%s

【优惠券】%s 
-----------------
【优惠券地址】%s
    ''' % (title, coupon_info, coupon_url)
    return res_txt

def get_tkl_coupon_info(original_tkl):
    title = re.search(r'【.*】', original_tkl).group().replace(u'【', '').replace(u'】', '')
    se = requests.session()
    se.cookies['UM_distinctid'] = '16f0dd06c08480-0f27fcf58aeb138-4c302a7b-1fa400-16f0dd06c09f8'
    se.cookies['CNZZDATA1261806159'] = '305133404-1576484760-%7C1576644781'
    se.cookies['Hm_lvt_73f904bff4492e23046b74fe0d627b3d'] = '1576484763,1576640457'
    se.cookies['PHPSESSID'] = 'b938uravn6ovrpk915qb1a83e9'
    se.cookies['Hm_lpvt_73f904bff4492e23046b74fe0d627b3d'] = '1576646963'
    se.cookies[
        'tkdg_user_info'] = 'think%3A%7B%22id%22%3A%2246458%22%2C%22password%22%3A%2212892b74dcb71da900559b15bd2665ee%22%7D'
    url = 'https://www.taokouling.com/index/tbtkltoitemid/'
    headers = {
        'Host': 'www.taokouling.com',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:71.0) Gecko/20100101 Firefox/71.0',
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'Accept-Language': 'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2',
        'Accept-Encoding': 'gzip, deflate',
        'Content-Type': 'application/x-www-form-urlencoded',
        'Content-Length': '507',
        'Origin': 'https://www.taokouling.com',
        'X-Requested-With': 'XMLHttpRequest',
        'Connection': 'close',
        'Referer': 'https://www.taokouling.com/index/tbtkltoitemid/'
    }
    datas = {
        'tkl': original_tkl,
        'zdgy': 'true',
        'pid': 'mm_389810114_446200449_108517850497',
        'tgdl': 'true'
    }
    res = se.post(url, data=datas, headers=headers)
    res = res.json()
    print(res['data'])
    if 'error' in res['data']['tkl'] or 'coupon_info' not in res['data']:
        res_txt = '''
%s
-----------------
该宝贝暂时没有找到内部返利通道！亲您可以换个宝贝试试。        
        ''' % title
    else:
        coupon_info = res['data']['coupon_info']
        tkl = res['data']['tkl']
        url = res['data']['url']
        res_txt = '''恭喜您，已找到隐藏优惠！！
    
%s

【优惠券】%s 
请复制%s淘口令、打开淘宝APP下单
-----------------
【下单地址】%s
        ''' % (title, coupon_info, tkl, url)
    return res_txt


def deal_remark_name(message):
    ###
    # #    描述: 字典好友信息, 每次启动微信都重新获取一份, 注重remark_name, 其他不管
    # #    description: save wechat's friends message, reload file when wechat start everytime
    # #    param: {message}
    # #    usage:
    # #    return: none
    ###
    wx_id = message.get('data', {}).get('wx_id', '')
    remark_name = message.get('data', {}).get('remark_name', '')
    dict_remark_name[wx_id] = remark_name


# 消息处理 分流
def thread_handle_message(wx_inst):
    global ID_num
    while True:
        message = queue_recved_message.get()
        print(message)

        # 坑点: if和elif 慎用

        # 本地保存friends信息, 重点remark_name
        try:
            if 'friend::person' in message.get('type'):
                deal_remark_name(message)
        except:
            pass

        # 单人消息
        try:
            if 'msg::single' in message.get('type'):
                # 这里是判断收到的是消息 不是别的响应
                send_or_recv = message.get('data', {}).get('send_or_recv', '')
                # 判断微信id, 黑名单
                from_wxid = message.get('data', {}).get('from_wxid', '')

                # 进行回复
                if (send_or_recv[0] == '0'): #and (from_wxid in admin_wx):
                    from_msg = message.get('data', {}).get('msg', '')
                    if r'http://' in from_msg or r'https://' in from_msg:
                        reply_msage = get_url_coupon_info(from_msg)
                    elif '【' in from_msg and '】' in from_msg:
                        reply_msage = get_tkl_coupon_info(from_msg)
                    reply_msage_ID = from_wxid
                    wx_inst.send_text(reply_msage_ID, str(reply_msage))
        except:
            pass

        try:
            if 'msg::chatroom' in message.get('type'):
                # 这里是判断收到的是消息 不是别的响应
                send_or_recv = message.get('data', {}).get('send_or_recv', '')
                data_type = message.get('data', {}).get('data_type', '')
                if send_or_recv[0] == '0':
                    if data_type[0] == '1':
                        from_msg = message.get('data', {}).get('msg', '')
                        from_wxid = message.get('data', {}).get('from_member_wxid', '')
                        from_chatroom_wxid = message.get('data', {}).get('from_chatroom_wxid', '')
                        if r'http://' in from_msg or r'https://' in from_msg:
                            reply_msage = get_url_coupon_info(from_msg)
                        elif '【' in from_msg and '】' in from_msg:
                            reply_msage = get_tkl_coupon_info(from_msg)
                        wx_inst.send_text(to_user=from_chatroom_wxid, msg=reply_msage,
                                          at_someone=from_wxid)
        except:
            pass

def main():
    wx_inst = WechatPCAPI(on_message=on_message, log=logging)
    wx_inst.start_wechat(block=True)

    while not wx_inst.get_myself():
        time.sleep(5)

    print('登陆成功')

    threading.Thread(target=thread_handle_message, args=(wx_inst,)).start()

    time.sleep(10)
    # wx_inst.send_text(to_user=admin_wx, msg='脚本开始')


if __name__ == '__main__':
    main()