
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
  is_paragraph = False
  try:
    while i < size:
      char = origin[i]
      if char == "\n" or i == 0:
        # for first chars
        if not i == 0:
          i += 1
          char = origin[i]

        # for special hooks
        if char == "?":
          while not char == "\n":
            i += 1
            char = origin[i]

        # parsing headers
        elif char == "#":
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

      # img
      elif char == "!" and origin[i + 1] == "[":
        i += 1
        char = origin[i]

        start = i + 1
        
        while not char == "]":
          i += 1
          char = origin[i]

        end = i

        img_name = origin[start:end]

        while not char == "(":
          i += 1
          char = origin[i]

        start = i + 1

        while not char == ")":
          i += 1
          char = origin[i]

        end = i

        img_link = origin[start:end].strip(" ")
          
        html.write("<img src=\"" + img_link + "\"")
        html.write(" alt=\"" + img_name + "\" /img>")

      # parsing plain text
      else:
        html.write(char)
      
      i += 1

  except:
    unused = None
        
  if is_paragraph:
    html.write("</p>")
    is_paragraph = False
  html.write("</body>")

  # html basics
  html.write("</html>")
