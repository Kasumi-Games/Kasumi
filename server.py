import subprocess
import os


# 获取当前脚本文件所在目录的绝对路径
script_directory = os.path.dirname(os.path.abspath(__file__))
ascii_tmr = '''
     __________________________________
    |                                  |\ 
    |   ████████╗███╗   ███╗██████╗    | |
    |   ╚══██╔══╝████╗ ████║██╔══██╗   | |
    |      ██║   ██╔████╔██║██████╔╝   | |
    |      ██║   ██║╚██╔╝██║██╔══██╗   | |
    |      ██║   ██║ ╚═╝ ██║██║  ██║   | |
    |      ╚═╝   ╚═╝     ╚═╝╚═╝  ╚═╝   | |
    |                                  | |
    |     欢迎使用 TomorinBOT 项目模版
    |     
    |                                  | |
    |                                  | |
    |                                  | |
    |              春日影                
    |                                  | |
    |                                  | |
    |                                  | |
    |__________________________________| |
     \__________________________________\|   
     
     曾经不会被忘记，星空会照亮未来，下一个春天。
            '''
print(ascii_tmr)

# 我们的迷失，从ano酱开始。（saki？

try:
    subprocess.run(["python", script_directory + '/core/server.py'])
except:
    try:
        print('[Python] 检测到您的系统路径没有Python，正在尝试使用Python3运行')
        subprocess.run(["python3", script_directory + '/core/server.py'])
    except:
        exit(1)


