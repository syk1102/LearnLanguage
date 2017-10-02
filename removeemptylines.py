source_file = open('Input/tags.txt', 'r')
for line in file:
    if not line.isspace():
        file.write(line)