import unittest
from inmemorystorage import InMemoryStorage
from inmemorystorage.storage import InMemoryDir, InMemoryFile
from django.core.files.base import ContentFile

class MemoryStorageTests(unittest.TestCase):
    def setUp(self):
        self.storage = InMemoryStorage()
        self.filesystem = self.storage.filesystem

    def test_listdir(self):
        self.assertEqual(self.storage.listdir(''), [[], []])

        self.filesystem.add_child('dir0', InMemoryDir())
        self.filesystem.add_child('file0', InMemoryFile())

        self.assertEqual(self.storage.listdir(''), [['dir0'], ['file0']])
        self.assertEqual(self.storage.listdir('dir0'), [[], []])

        self.filesystem.resolve('dir0').add_child('subdir', InMemoryDir())
        self.assertEqual(self.storage.listdir('dir0'), [['subdir'], []])

    def test_delete(self):
        self.filesystem.add_child('dir0', InMemoryDir())
        self.filesystem.resolve('dir0').add_child('nested_file', InMemoryFile())
        self.filesystem.add_child('file0', InMemoryFile())
        self.assertEqual(self.filesystem.resolve('dir0').ls(), ['nested_file'])

        self.storage.delete('dir0/nested_file')
        self.assertEqual(self.filesystem.resolve('dir0').ls(), [])
        self.assertEqual(set(self.filesystem.ls()), set(['dir0', 'file0']))

        self.storage.delete('dir0')
        self.assertEqual(set(self.filesystem.ls()), set(['file0']))

    def test_exists(self):
        self.filesystem.add_child('file0', InMemoryFile())
        self.assertTrue(self.storage.exists('file0'))
        self.assertFalse(self.storage.exists('file1'))
        self.storage.delete('file0')
        self.assertFalse(self.storage.exists('file0'))

    def test_size(self):
        self.filesystem.add_child('file0', InMemoryFile('test'))
        self.assertEqual(self.storage.size('file0'), 4)

    def test_save(self):
        self.storage.save('file', ContentFile('test'))
        self.assertEqual(self.storage.size('file'), 4)
        self.storage.save('subdir/file', ContentFile('test'))
        self.assertEqual(self.storage.size('subdir/file'), 4)

    def test_all(self):
        self.assertEqual(self.storage.listdir('/'), [[], []])
        self.assertEqual(self.storage.save('dir/subdir/file', ContentFile('testing')), 'dir/subdir/file')
        self.assertEqual(self.storage.listdir('/'), [['dir'], []])
        self.assertEqual(self.storage.listdir('dir/'), [['subdir'], []])
        self.assertEqual(self.storage.save('dir/subdir/file2', ContentFile('testing2')), 'dir/subdir/file2')
        self.assertEqual(self.storage.save('file', ContentFile('testing3')), 'file')
        self.assertEqual(self.storage.listdir('/'), [['dir'], ['file']])
        self.assertEqual(self.storage.listdir('dir/'), [['subdir'], []])
        self.assertEqual(self.storage.open('dir/subdir/file').read(), 'testing')
        self.assertEqual(self.storage.size('dir/subdir/file'), 7)
        self.assertEqual(self.storage.size('dir/subdir/file2'), 8)
        self.assertEqual(self.storage.size('file'), 8)
        self.assertEqual(self.storage.delete('file'), None)
        self.assertEqual(self.storage.listdir('/'), [['dir'], []])
        self.assertEqual(self.storage.delete('dir/subdir/file'), None)
        self.assertEqual(self.storage.listdir('dir/subdir'), [[], ['file2']])
        self.assertEqual(self.storage.exists('dir/subdir/file2'), True)
        self.assertEqual(self.storage.delete('dir/subdir/file2'), None)
        self.assertEqual(self.storage.exists('dir/subdir/file2'), False)
        self.assertEqual(self.storage.listdir('dir/subdir'), [[], []])

if __name__ == '__main__':
    unittest.main()
