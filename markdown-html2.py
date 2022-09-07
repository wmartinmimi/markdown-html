
origin = None
with open("example.md", "r") as markdown:
  origin = markdown.read()

if origin == None:
  exit()

with open('example.html', 'w') as html:
  # html basics
  html.write("<!DOCTYPE html>")
  html.write("<html lang=\"en\">")

  # <head>
  html.write("<head>")

  # title
  html.write("<title>")
  has_title = False
  for line in origin:
    if has_title:
      break
    if line.startswith("?title:"):
      line = line.removeprefix("?title:").rstrip(" ")
      html.write(line)
      has_title = True
  
  for line in origin.splitlines():
    if has_title:
      break
    if line.startswith("#"):
      line = line.removeprefix("#").lstrip(" ").rstrip("#").rstrip(" ")
      html.write(line)
      has_title = True
  
  html.write("</title>")

  html.write("</head>")

  # <body>
  html.write("<body>")

  i = 0
  size = len(origin)
  while i < size:
    char = origin[i]
    if char == "\n":
      continue
    if char == " ":
      continue
    if char == "?":
      continue

    # parsing headers
    if  char == "#":
      heading_size = 0
      while char == "#":
        i += 1
        char = origin[i]
        heading_size += 1
      start = i + 1

      while not char == "\n":
        i += 1
        char = origin[i]

      end = i

      line = origin[start: end]
      line = line.lstrip(" ").rstrip("#").rstrip(" ")
      if heading_size > 0:
        html.write("<h" + str(heading_size) + ">")
        html.write(line)
        html.write("</h" + str(heading_size) + ">")

    elif char == "[":
      start = i + 1
      
      while not char == "]":
        i += 1
        char = origin[i]

      end = i

      link_name = origin[start:end]

      while not char == "(":
        i += 1
        char = origin[i]

      start = i + 1

      while not char == ")":
        i += 1
        char = origin[i]

      end = i

      link = origin[start:end].strip(" ")
        
      html.write("<a href=\"" + link + "\">")
      html.write(link_name)
      html.write("</a>")

    # parsing plain text
    else:
      # html.write("<p>" + line + "</p>")
      continue

    i += 1
        
  html.write("</body>")

  # html basics
  html.write("</html>")
