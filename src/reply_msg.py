#!/usr/bin/env python3
# -*- coding:utf-8 -*-
###
# #    File: reply_msg.py
# #    Project: Mocha-L/WechatPCAPI 
# #    Author: zzy
# #    mail: elliot.bia.8989@outlook.com
# #    github: https://github.com/elliot-bia
# #    Date: 2019-12-09 14:59:42
# #    LastEditors: zzy
# #    LastEditTime: 2019-12-12 16:26:07
# #    ---------------------------------
# #    Description: 对Mocha-L的WechatPCAPI进行调用,  实现功能: 自动接受的个人信息, 指定群信息发送到指定admin微信, 并且通过回复序列号(空格)信息进行回复


###
# -*- coding: utf-8 -*-
# @Time    : 2019/11/27 23:00
# @Author  : Leon
# @Email   : 1446684220@qq.com
# @File    : test.py
# @Desc    :
# @Software: PyCharm

from WechatPCAPI import WechatPCAPI
import time
import logging
from queue import Queue
import threading

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

                    reply_msage_ID = from_wxid
                    reply_msage = 'hello, world'
                    wx_inst.send_text(reply_msage_ID, str(reply_msage))
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