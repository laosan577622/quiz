# build_exe.py
import os
import PyInstaller.__main__

PyInstaller.__main__.run([
    '--name=%s' % 'LaosanQuizApp',
    '--onefile',
    '--windowed',
    '--add-data=%s' % 'exam_questions.json;.',
    '--add-data=%s' % 'config.ini;.',
    '--add-data=%s' % 'templates/index.html;templates',
   
    'app.py'
])
