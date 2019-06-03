#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time    : 2018/11/14 11:04 AM
# @Author  : liangk
# @Site    :
# @File    : auto_archive_ios.py
# @Software: PyCharm

import os
import shutil
import requests
import sys
import webbrowser
import subprocess
import time
import smtplib
from email.mime.text import MIMEText
from email import encoders
from email.header import Header
from email.utils import parseaddr, formataddr


project_name = 'YouXin'    # 项目名称
archive_workspace_path = '/Users/huzhangyi/Desktop/YouXin'    # 项目路径 #===source_dir
export_directory = 'RobertArchive'    # 输出的文件夹
source_dir = '/Users/huzhangyi/Desktop/YouXin/'
target_dir = '/Users/huzhangyi/Library/MobileDevice/Provisioning Profiles/'
test_desktop = '/Users/huzhangyi/Desktop' # 打包出来ipa所在文件夹路径

downloadUrl = 'http://192.168.31.99:8093/iosdownload/iosdownload/519858C352489A08C9F31577CEB77269C1266037.mobileprovision' 
uploadUrl = ""


# ipa_download_url = 'https://www.pgyer.com/XXX' #蒲公英的APP地址

# # 蒲公英账号USER_KEY、API_KEY
# USER_KEY = 'XXXXXXXXXXXXXXXXXXXX'
# API_KEY = 'XXXXXXXXXXXXXXXXXXXX'

# from_address = 'XXXXXXXXXXXXXXXXXXXX@qq.com'    # 发送人的地址
# password = 'XXXXXXXXXXXXXXXXXXXX'  # 邮箱密码换成他提供的16位授权码
# to_address = 'XXXXXXXXXXXXXXXXXXXX@qq.com'    # 收件人地址,可以是多个的
# smtp_server = 'smtp.qq.com'    # 因为我是使用QQ邮箱..


class AutoArchive(object):
    """自动打包并上传到蒲公英,发邮件通知"""

    def __init__(self):
        pass

    def clean(self):
        print("\n\n===========开始clean操作===========")
        start = time.time()
        clean_command = 'xcodebuild clean -workspace %s/%s.xcworkspace -scheme %s -configuration Release' % (
            archive_workspace_path, project_name, project_name)
        clean_command_run = subprocess.Popen(clean_command, shell=True)
        clean_command_run.wait()
        end = time.time()
        # Code码
        clean_result_code = clean_command_run.returncode
        if clean_result_code != 0:
            print("=======clean失败,用时:%.2f秒=======" % (end - start))
        else:
            print("=======clean成功,用时:%.2f秒=======" % (end - start))
            self.archive()

    def archive(self):
        print("\n\n===========开始archive操作===========")

        # 删除之前的文件
        subprocess.call(['rm', '-rf', '%s/%s' % (archive_workspace_path, export_directory)])
        time.sleep(1)
        # 创建文件夹存放打包文件
        subprocess.call(['mkdir', '-p', '%s/%s' % (archive_workspace_path, export_directory)])
        time.sleep(1)

        start = time.time()
        archive_command = 'xcodebuild archive -workspace %s/%s.xcworkspace -scheme %s -configuration Release -archivePath %s/%s' % (
            archive_workspace_path, project_name, project_name, archive_workspace_path, export_directory)
        archive_command_run = subprocess.Popen(archive_command, shell=True)
        archive_command_run.wait()
        end = time.time()
        # Code码
        archive_result_code = archive_command_run.returncode
        if archive_result_code != 0:
            print("=======archive失败,用时:%.2f秒=======" % (end - start))
        else:
            print("=======archive成功,用时:%.2f秒=======" % (end - start))
            # 导出IPA
            self.export()
# 以上编译文件的方法暂时不用执行


    # 网络请求描述文件
    def req_file(self):
        # 1. 网络请求，获取下载的url
        # 此处从别的地方传入设备ID，作为参数，网络请求描述文件的下载链接


        # 2. 通过获取到的url下载描述文件
        print("\n\n===========开始download描述文件操作===========")
        r = requests.get(downloadUrl) 
        if r.status_code == 200:# 如果状态不是200，引发HTTPError异常
            print("\n\n===========download描述文件成功!===========")
            # 下载成功后获取描述文件名称加后缀：xxxxxxxx.mobileprovision
            marr = url.split("/")
            file_name = marr[len(marr)-1]
        with open(file_name, "wb") as f:
            f.write(r.content) # 下载描述文件到YouXin文件夹
            # 下载好的描述文件放在当前目录下，移动描述文件到Xcode目录下
            self.mv_file(source_dir, target_dir)



# 移动描述文件mv_file和打包export方法需要写入多线程
    # 此处开始签名，签名前移动描述文件到制定目录下
    def file_exists(self, file_): 
        return os.path.exists(file_)

    def mv_file(self, source_dir, target_dir):
        UDID = sys.argv[1]
        print("\n\n===========开始move描述文件操作===========")
        file_name = UDID+".mobileprovision"#c87d71d23c921382f34677ff9306624baf16b58b
        # provisionName = file_name[0:40]
        # arr = file_name.split(".")
        # UDID = arr[0] # 用于修改plist文件中的value
        print "=============获取到UDID = ",UDID 
        target_file = "{0}{1}".format(target_dir, file_name)
        source_file = "{0}{1}".format(source_dir, file_name)
        if self.file_exists(target_file):
            print("\n===========文件已存在目标目录，开始进行删除命令===========")
            os.remove(target_file)
        if self.file_exists(source_file):
            # 开始移动文件到目标目录
            shutil.move(source_file, target_file)
            print("\n===========mobileprovision文件移动成功!===========")
        # else:
        #     print("\n======移动文件目录不存在!======")
            
            # 生成plist文件，此处已经测试过，使用设备ID命名的plist文件可以打包成功
            self.creat_plist_file(UDID)


    def creat_plist_file(self, UDID):
        content = """<?xml version="1.0" encoding="UTF-8"?>
    <!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
    <plist version="1.0">
    <dict>
        <key>compileBitcode</key>
        <false/>
        <key>destination</key>
        <string>export</string>
        <key>method</key>
        <string>development</string>
        <key>provisioningProfiles</key>
        <dict>
            <key>com.xijiwa.YouXin</key>
            <string>ios</string>
        </dict>
        <key>signingCertificate</key>
        <string>iPhone Developer</string>
        <key>signingStyle</key>
        <string>manual</string>
        <key>stripSwiftSymbols</key>
        <true/>
        <key>teamID</key>
        <string>CB624K4459</string>
        <key>thinning</key>
        <string>&lt;none&gt;</string>
    </dict>
    </plist>
    """.replace("ios", UDID)
        f = open("{0}.plist".format(UDID), "w")
        f.write(content)
        f.close()
        print("\n======plist文件创建成功!======")

        # 导出IPA
        self.export(UDID)


    def export(self, UDID):
        print("\n\n===========开始export操作===========")
        print("\n\n==========请耐心等待大约7秒钟~===========")
        start = time.time()
        # export_command = 'xcodebuild -exportArchive -archivePath /Users/liangk/Desktop/TestArchive/myArchivePath.xcarchive -exportPath /Users/liangk/Desktop/TestArchive/out -exportOptionsPlist /Users/liangk/Desktop/TestArchive/ExportOptions.plist'
        export_command = 'xcodebuild -exportArchive -archivePath %s/%s.xcarchive -exportPath %s/%s -exportOptionsPlist %s/%s.plist' % (
            archive_workspace_path, export_directory, archive_workspace_path, UDID, archive_workspace_path, UDID)
        export_command_run = subprocess.Popen(export_command, shell=True)
        export_command_run.wait()
        end = time.time()
        # Code码
        export_result_code = export_command_run.returncode
        if export_result_code != 0:
            print("=======导出IPA失败,用时:%.2f秒=======" % (end - start))
        else:
            print("=======导出IPA成功,用时:%.2f秒=======" % (end - start))
            # 删除plist文件
            subprocess.call(['rm', '-rf', '%s/%s.plist' % (archive_workspace_path, UDID)])
            print("\n\n==========plist文件已删除!===========")
            # 删除archive.xcarchive文件
            # subprocess.call(['rm', '-rf', '%s/%s.xcarchive' % (archive_workspace_path, export_directory)])

            #上传ipa到服务端
            # self.upload('%s/%s/%s.ipa' % (archive_workspace_path, UDID, project_name))

    def upload(self, ipa_path):
        print("\n\n===========开始上传服务端操作===========")
        if ipa_path:
    #         # https://www.pgyer.com/doc/api 具体参数大家可以进去里面查看,
            url = 'http://www.pgyer.com/apiv1/app/upload'
            data = {
                'uKey': USER_KEY,
                '_api_key': API_KEY,
                'installType': '1',
                'updateDescription': "robert测试版本"
            }
            files = {'file': open(ipa_path, 'rb')}
            r = requests.post(url, data=data, files=files)
            if r.status_code == 200:
                print("\n\n===========上传成功===========")
    #         # 上传成功后删除ipa所在的文件夹
    #         subprocess.call(['rm', '-rf', '%s/%s.xcarchive' % (archive_workspace_path, export_directory)])
    #             # 是否需要打开浏览器
    #             # self.open_browser(self)
    #             self.send_email()
            else:
                print("\n\n===========没有找到对应的ipa===========")
    #         return

    @staticmethod
    def open_browser(self):
        webbrowser.open(ipa_download_url, new=1, autoraise=True)

    @staticmethod
    def _format_address(self, s):
        name, address = parseaddr(s)
        return formataddr((Header(name, 'utf-8').encode(), address))

    # def send_email(self):
    #     # https://www.pgyer.com/XXX app地址
    #     # 只是单纯的发了一个文本邮箱,具体的发附件和图片大家可以自己去补充
    #     msg = MIMEText('Hello' +'╮(╯_╰)╭应用已更新,请下载测试╮(╯_╰)╭' +'蒲公英的更新会有延迟,具体版本时间以邮件时间为准' +
    #                    '', 'html', 'utf-8')
    #     msg['From'] = self._format_address(self, 'iOS开发团队 <%s>' % from_address)
    #     msg['Subject'] = Header('来自iOS开发团队的问候……', 'utf-8').encode()
    #     server = smtplib.SMTP(smtp_server, 25)  # SMTP协议默认端口是25
    #     server.set_debuglevel(1)
    #     server.login(from_address, password)
    #     server.sendmail(from_address, [to_address], msg.as_string())
    #     server.quit()
    #     print("===========邮件发送成功===========")


if __name__ == '__main__':
    # description = input("请输入内容:")
    archive = AutoArchive()
    # archive.export()
    archive.mv_file(source_dir, target_dir)
    # archive.req_file()


