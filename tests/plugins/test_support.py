__author__ = 'pavle'

import logging
import sys
from logging import DEBUG

sys.path.append("../..")
logging.basicConfig(level=DEBUG)


import unittest
from io import StringIO


from termite.plugins.support import PluginManifestParser


class TestPluginManifestParser(unittest.TestCase):

    def setUp(self):
        self.PLUGIN_MF_STRING = """
        Plugin-Id: test.plugin
        Version: 0.1.2.TEST
        Plugin-Classes: test.class.One;
                        test.class.Two
        Requires: test.pkg [0.2.3, 0.2.5); test.pkg2 (1,7); other.pkg [1.a, 3.4.5]
        Exports: test.plugin [1.0.0]; test.plugin.module[1.0.0]
        Requires-Plugins: plugin1 [1.0];
                            plugin2 (1.0, 2.0);
        """

    def test_parse(self):
        parser = PluginManifestParser()
        manifest = parser.parse(StringIO(self.PLUGIN_MF_STRING))
        self.assertIsNotNone(manifest)
        self.assertEqual(manifest.id, "test.plugin")
        self.assertEqual(manifest.version, "0.1.2.TEST")
        self.assertIsNotNone(manifest.plugin_classes)
        self.assertEqual(len(manifest.plugin_classes), 2, "Expected 2 plugin classes")
        self.assertEqual(len(manifest.exports), 2, "Expected 2 exports")
        self.assertEqual(len(manifest.requires), 3, "Expected 3 requires entries")
        self.assertEqual(len(manifest.requires_plugins), 2, 'Expected 2 requires_plugins entries')
    
    def test_parse_requires_entry(self):
        parser = PluginManifestParser()
        req_e = parser.get_requires_entry('test.package.module [0.3.5.alpha, 0.4)')
        self.assertIsNotNone(req_e, 'Requires Entry should be returned')
        self.assertEqual(req_e.name, 'test.package.module')
        self.assertIsNotNone(req_e.version_range)
        self.assertEqual(len(req_e.version_range), 2)
        min_version, min_inclusive = req_e.version_range[0]
        self.assertIsNotNone(min_version)
        self.assertIsNotNone(min_inclusive)
        self.assertEqual(min_version, '0.3.5.alpha')
        self.assertEqual(min_inclusive, True)
        max_version, max_inclusive = req_e.version_range[1]
        self.assertIsNotNone(max_version)
        self.assertIsNotNone(max_inclusive)
        self.assertEqual(max_version, '0.4.0')
        self.assertEqual(max_inclusive, False)

    def test_parse_exports_entry(self):
        parser = PluginManifestParser()
        ee = parser.get_exports_entry('test.package.module [1.0.0.SNAPSHOT]')
        self.assertIsNotNone(ee, 'Exports entry was expected')
        self.assertEqual(ee.name, 'test.package.module')
        self.assertIsNotNone(ee.version)
        self.assertEqual(ee.version,'1.0.0.SNAPSHOT')
