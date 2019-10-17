import  os
class PathItem:
    name = ""
    parent = ""
    url = ""

    def __init__(self, name, parent):
        self.name = name
        self.parent = parent
        self.url = os.path.join(parent, name)
        print (self.url)


class FileItem:
    name = ""
    parent = ""
    url = ""
    canRead = True

    def __init__(self, name, parent):
        self.name = name
        self.parent = parent
        self.url = os.path.join(parent, name)
