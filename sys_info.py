# -*- coding: utf-8 -*-
"""
--------------------------------------------------
    Date Time ：     2023/10/13 17:09
    Author ：        dokeyhou
    IDE ：           PyCharm
    File ：          sys_info.py
    Description:     
--------------------------------------------------
"""
import platform as plt


def get_sys_info() -> plt.uname_result:
    return plt.uname()


if __name__ == '__main__':
    info = get_sys_info()
    print('OS_TYPE="%s"\nOS_ARCH="%s"' % (info.system, info.machine))
