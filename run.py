from facexem_app import app
import os

f = open('banner.txt')
os.system('cls')
for line in f:
    line = line.rstrip('\n')
    print(line)
app.run(port=9999, debug=True)
