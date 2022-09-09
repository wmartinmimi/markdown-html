import os

# extract string from index "start" to character "trim_char"
def trimTo(origin, start, trim_char):
  i = start
  char = origin[i]
  while char != trim_char:
    i += 1
    char = origin[i]

  return origin[start + 1:i]
  
def newI(i, line):
  return i + len(line) + 1

# open markdown file for converting to html
def openMarkDown(path):
  origin = None
  with open(path, "r") as markdown:
    origin = markdown.read()

  if origin == None:
    print("Cannot open: " + path)
    return

  html_name = path[::-1][path[::-1].find(".") + 1:len(path[::-1])][::-1] + ".html"

  with open(html_name, 'w') as html:
    # html basics
    html.write("<!DOCTYPE html>")
    html.write("<html lang=\"en\">")

    # <head>
    html.write("<head>")

    # title
    html.write("<title>")
    has_title = False
    for line in origin.splitlines():
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
        line = line.strip("#").strip(" ")
        html.write(line)
        has_title = True
    
    html.write("</title>")

    html.write("</head>")

    # <body>
    html.write("<body>")

    i = 0
    size = len(origin)
    is_paragraph = False

    while i < size:
      char = origin[i]
      if char == "\n" or i == 0:

        if i + 1 >= size:
          break

        # for first chars
        if not i == 0:
          i += 1
          char = origin[i]

        # for special hooks
        if char == "?":
          line = trimTo(origin, i, "\n")
          i = newI(i, line)

        # parsing headers
        elif char == "#":
          heading_size = 0
          while char == "#":
            i += 1
            char = origin[i]
            heading_size += 1

          line = trimTo(origin, i, "\n")
          i = newI(i, line)

          line = line.lstrip(" ").rstrip("#").rstrip(" ")
          if heading_size > 0:
            html.write("<h" + str(heading_size) + ">")
            html.write(line)
            html.write("</h" + str(heading_size) + ">")

        elif char == "-":

          # horizontal line
          t = i
          while char == "-":
            t += 1
            char = origin[t]

          if origin[t + 1] == "\n":
            i = t
            html.write("</hr>")
            continue

          # unordered list
          html.write("<ul>")
          
          while True:
            html.write("<li>")

            line = trimTo(origin, i, "\n")
            i = newI(i, line)

            html.write(line.strip(" "))

            html.write("</li>")

            if len(origin) > i or origin[i + 1] != "-":
              break

            i += 1
          
          html.write("</ul>")
          continue
            

        # for empty lines
        elif char == "\n":
          if is_paragraph:
            html.write("</p>")
            is_paragraph = False
          continue
        
        else:
          i -= 1
        i += 1
        continue

      if not is_paragraph:
        html.write("<p>")
        is_paragraph = True

      elif origin[i - 1] == "\n":
        html.write(" ")

      # parsing links
      if char == "[":

        link_name = trimTo(origin, i, "]")
        i = newI(i, link_name)

        char = origin[i]

        while not char == "(":
          i += 1
          char = origin[i]

        link = trimTo(origin, i, ")")
        i = newI(i, link)
          
        html.write("<a href=\"" + link.strip(" ") + "\">")
        html.write(link_name)
        html.write("</a>")

      # img
      elif char == "!" and origin[i + 1] == "[":
        i += 1
        char = origin[i]

        img_name = trimTo(origin, i, "]")
        i = newI(i, img_name)

        char = origin[i]

        while not char == "(":
          i += 1
          char = origin[i]

        img_link = trimTo(origin, i, ")")
        i = newI(i, img_link)
          
        html.write("<img src=\"" + img_link.strip(" ") + "\"")
        html.write(" alt=\"" + img_name + "\" />")

      # parsing plain text
      else:
        html.write(char)
      
      i += 1
          
    # end paragraph
    if is_paragraph:
      html.write("</p>")
      is_paragraph = False
    html.write("</body>")

    # html basics
    html.write("</html>")

# open directory containing the markdown
def openRoot(root):
  for path, subdirs, files in os.walk(root):
    for name in files:
      if name.endswith(".md"):
        openMarkDown(os.path.join(path, name))
      if name.endswith(".markdown"):
        openMarkDown(os.path.join(path, name))

openRoot(os.getcwd())
