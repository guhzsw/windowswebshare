import PyInstaller.__main__
import os

# 确保目录存在
if not os.path.exists('dist'):
    os.makedirs('dist')

PyInstaller.__main__.run([
    'app.py',
    '--name=WebShare',
    '--onefile',
    '--noconsole',
    '--add-data=templates:templates',
    '--add-data=static:static',
    '--icon=static/icon.ico',  # 如果你有图标的话
    '--clean',
])
