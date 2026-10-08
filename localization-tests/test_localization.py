import json, re, subprocess, unittest
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
RESOURCE = ROOT / 'purge/zh-Hans.lproj/Localizable.strings'
def translations():
    if not RESOURCE.exists(): return {}
    return json.loads(subprocess.check_output(['plutil', '-convert', 'json', '-o', '-', str(RESOURCE)]))
PLACEHOLDER = re.compile(r'%(?:\d+\$)?(?:[-+#0 ]*\d*(?:\.\d+)?)(?:hh|ll|h|l|z|t|j)?[@diuoxXfFeEgGcsp]')
class LocalizationTests(unittest.TestCase):
    def test_main_actions_are_chinese(self):
        strings = translations()
        for key, expected in [('Scan Everything', '扫描全部'), ('Settings', '设置'), ('Move to Trash', '移到废纸篓')]:
            self.assertEqual(strings.get(key), expected)
    def test_permanent_deletion_is_explicit(self):
        strings = translations()
        self.assertIn('永久', strings.get('Permanently delete these items?', ''))
        self.assertIn('无法', strings.get("Purge couldn't identify this file. Only delete it if you know what it is. It can't be put back afterward.", ''))
    def test_simulator_data_deletion_warning_is_chinese(self):
        strings = translations()
        self.assertIn('应用和数据', strings.get('Deletes its apps and data.', ''))
        self.assertIn('个月', strings.get('Last used %lld months ago. %@', ''))
    def test_disk_permission_onboarding_is_chinese(self):
        strings = translations()
        for key in ['Want Purge to look deeper?', 'App Store app caches', 'Big forgotten files', "Deleted apps' leftovers", 'Only cleans when you say', 'Nothing leaves your Mac', 'Everything goes to the Trash']:
            self.assertRegex(strings.get(key, ''), r'[一-鿿]')
    def test_translation_preserves_interpolation_placeholders(self):
        strings = translations()
        self.assertGreaterEqual(len(strings), 250)
        for key, value in strings.items():
            self.assertEqual(PLACEHOLDER.findall(key), PLACEHOLDER.findall(value), key)
if __name__ == '__main__': unittest.main()
