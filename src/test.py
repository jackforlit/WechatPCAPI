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

logging.basicConfig(level=logging.INFO)


def on_message(message):
    print(message)


def main():
    wx_inst = WechatPCAPI(on_message=on_message, log=logging)
    wx_inst.start_wechat(block=True)

    while not wx_inst.get_myself():
        time.sleep(5)

    print(wx_inst.get_myself())

    time.sleep(10)
    wx_inst.send_text(to_user='filehelper', msg='777888999')
    wx_inst.send_link_card(
        to_user='filehelper',
        title='博客',
        desc='我的博客，红领巾技术分享网站',
        target_url='http://www.honglingjin.online/',
        img_url='http://honglingjin.online/wp-content/uploads/2019/07/0-1562117907.jpeg'
    )
    wx_inst.send_img(to_user='filehelper', img_abspath=r'C:\Users\Leon\Pictures\1.jpg')
    wx_inst.send_file(to_user='filehelper', file_abspath=r'C:\Users\Leon\Desktop\1.txt')
    wx_inst.send_gif(to_user='filehelper', gif_abspath=r'C:\Users\Leon\Desktop\08.gif')
    wx_inst.send_card(to_user='filehelper', wx_id='gh_6ced1cafca19')

    # wx_inst.update_frinds()


if __name__ == '__main__':
    main()
