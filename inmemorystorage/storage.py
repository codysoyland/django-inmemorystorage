from django.core.files.storage import Storage
from django.core.files.base import ContentFile

class PathDoesNotExist(Exception):
    pass

class InMemoryNode(object):
    """
    Base class for files and directories.
    """
    parent = None

    def add_child(self, name, child):
        child.parent = self
        self.children[name] = child

class InMemoryFile(InMemoryNode):
    """
    Stores contents of file and stores reference to parent.
    """
    def __init__(self, contents='', parent=None):
        self.contents = contents
        self.parent = parent

class InMemoryDir(InMemoryNode):
    """
    Stores dictionary of child directories/files and reference to parent.
    """
    def __init__(self, dirs=None, files=None, parent=None):
        self.children = {}
        self.parent = parent

    def resolve(self, path, create=False):
        path_bits = path.strip('/').split('/', 1)
        current = path_bits[0]
        rest = path_bits[1] if len(path_bits) > 1 else None
        if not rest:
            if current == '':
                return self
            if current in self.children.keys():
                return self.children[current]
            if not create:
                raise PathDoesNotExist()
            node = InMemoryFile()
            self.add_child(current, node)
            return node
        if current in self.children.keys():
            return self.children[current].resolve(rest, create=create)
        if not create:
            raise PathDoesNotExist()
        node = InMemoryDir()
        self.add_child(current, node)
        return self.children[current].resolve(rest, create)

    def ls(self, path=''):
        return self.resolve(path).children.keys()

    def listdir(self, dir):
        nodes = tuple(self.resolve(dir).children.iteritems())
        dirs = [k for (k, v) in nodes if isinstance(v, InMemoryDir)]
        files = [k for (k, v) in nodes if isinstance(v, InMemoryFile)]
        return [dirs, files]

    def delete(self, path):
        node = self.resolve(path)
        for name, child in node.parent.children.iteritems():
            if child is node:
                del node.parent.children[name]
                break

    def exists(self, name):
        try:
            self.resolve(name)
        except PathDoesNotExist:
            return False
        else:
            return True

    def size(self, name):
        return len(self.resolve(name).contents)

    def open(self, path):
        return ContentFile(self.resolve(path, create=True).contents)

    def save(self, path, content):
        file = self.resolve(path, create=True)
        file.contents = content
        return path

class InMemoryStorage(Storage):
    """
    Django storage class for in-memory filesystem.
    """
    def __init__(self, filesystem=None):
        self.filesystem = filesystem or InMemoryDir()

    def listdir(self, dir):
        return self.filesystem.listdir(dir)

    def delete(self, path):
        return self.filesystem.delete(path)

    def exists(self, name):
        return self.filesystem.exists(name)

    def size(self, name):
        return self.filesystem.size(name)

    def _open(self, name, mode=None):
        return self.filesystem.open(name)

    def _save(self, name, content):
        return self.filesystem.save(name, content.read())
