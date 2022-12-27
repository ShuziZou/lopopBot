# 开源脚本

## 前言

非常感谢大佬[PairZhu](https://github.com/PairZhu)开源的自动健康打卡脚本，本人只是在源码基础上做了机器人的通知，图形验证码一开始的思路是tesseract识别，但是准确率感人，后来在空间看到另一位大佬用的ddddocr，然后也用了这个库，实际体验下来很不错。

在最近南工校园网登录加了图片验证码的情况下，通过（~~tesseract-oct~~）ddddocr识别其中的数字，然后将参数放入请求体中即可，其他部分完全不变

## 使用

- 自动健康打卡：clockin

    1. 安装`ddddocr`

        `pip install ddddocr`

        [对比Pytesseract](https://blog.csdn.net/fun_sn/article/details/125421983)

    2. 运行`retryHealth`函数或者将插件放到机器人上

    可以直接添加好友：1418187180并发送“帮助”，会自动通过的

- 校园网自动登录：autologin

    1. 直接下载其中的dist文件夹，然后在`config.json`中修改相关配置即可

    2. 源码详见`main.py`

    3. 打包过程：

        1. 安装`pipenv`：`pip install pipenv`

        2. 安装虚拟环境：`pipenv install`

        3. 进入虚拟环境并安装相关的包：`pipenv shell`

            - `pip install requests ddddocr beautifulsoup4 pyinstaller`

        4. 通过`pyinstaller`进行exe打包

            > ddddocr打包会出错，解决方案参考[ddddocr正确的打包方式](https://blog.csdn.net/weixin_46010646/article/details/124926207)
