from facexem_app import app
f = open('banner.txt')
for line in f:
    line = line.rstrip('\n')
    print(line)
app.run(port=9999, debug=True)


