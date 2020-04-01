# -*- mode: python ; coding: utf-8 -*-

block_cipher = None


a = Analysis(['titandash.py'],
             pathex=['C:\\Users\\Votum\\repos\\titandash2'],
             binaries=[],
             datas=[
                 ('C:\\Users\\Votum\\Envs\\titandash2\\lib\\site-packages\\eel\\eel.js', 'eel'),
                 ('C:\\Users\\Votum\\Envs\\titandash2\\Lib\\site-packages\\gevent', 'gevent'),
                 ('C:\\Users\\Votum\\Envs\\titandash2\\Lib\\site-packages\\imagehash\\VERSION', 'imagehash/'),
                 ('web', 'web'),
                 ('db\\__init__.py', 'db'),
                 ('db\\migrations', 'db/migrations'),
                 ('modules\\bot\\data', 'modules\\bot\\data'),
                 ('dependencies\\tesseract\\Tesseract-OCR', 'dependencies\\tesseract\\Tesseract-OCR'),
             ],
             hiddenimports=['bottle_websocket', 'pkg_resources.py2_warn'],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          [],
          exclude_binaries=True,
          name='titandash',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          console=True , icon='web\\favicon.ico')
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               upx_exclude=[],
               name='titandash')
