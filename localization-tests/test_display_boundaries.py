"""Exercise dynamic display keys without launching Purge or requesting permissions."""
import json
import pathlib
import plistlib
import shutil
import subprocess
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
RESOURCE = ROOT / 'purge/zh-Hans.lproj/Localizable.strings'

def translations():
    return plistlib.loads(subprocess.check_output(['plutil', '-convert', 'xml1', '-o', '-', str(RESOURCE)]))

class DynamicDisplayTests(unittest.TestCase):
    def test_overview_sidebar_and_scan_display_labels_have_chinese(self):
        strings = translations()
        keys = ['Overview', 'App Caches', 'Dev Tools', 'Clean', 'Review', 'App Uninstaller',
                'Clean Safe Items', 'Checking...', 'Try Again', 'Installed apps', 'Leftovers from deleted apps',
                "macOS, your documents and photos, and files Purge doesn't sort", 'Available for new files',
                'Scan App Caches, Dev Tools, Large Files and apps, one after another',
                '%@ safe to clean', 'Nothing safe to clean', 'just now', '%llds ago', '%lldm ago', '%lldh ago', '%lldd ago']
        for key in keys:
            with self.subTest(key=key):
                self.assertTrue(key in strings, f'Missing display translation: {key}')
                self.assertRegex(strings[key], r'[\u4e00-\u9fff]')

    def test_sidebar_uses_display_names_and_keeps_original_ids(self):
        source = (ROOT / 'purge/Services/PurgeStore.swift').read_text()
        tab = source.split('enum Tab: String, CaseIterable, Identifiable {', 1)[1].split('enum ScanPhase:', 1)[0]
        self.assertTrue('var displayName: String' in tab, 'Sidebar tab has no localized display name')
        for declaration in ['case overview = "Overview"', 'case appCaches = "App Caches"', 'case uninstaller = "App Uninstaller"', 'var id: String { rawValue }']:
            self.assertIn(declaration, tab)
        content = (ROOT / 'purge/ContentView.swift').read_text()
        self.assertIn('title: tab.displayName', content)
        self.assertIn('title: store.selectedTab.displayName', content)
        self.assertIn('Text(LocalizedStringKey(title))', content)

    def test_shared_button_menu_and_overview_getters_localize(self):
        overview = (ROOT / 'purge/Views/OverviewView.swift').read_text()
        self.assertIn('return String(localized: "Installed apps")', overview)
        self.assertIn('return String(localized: "Leftovers from deleted apps")', overview)
        chrome = (ROOT / 'purge/Views/AppChrome.swift').read_text()
        self.assertTrue('Text(LocalizedStringKey(title))' in chrome, 'Shared labels still display raw keys')
        menu = (ROOT / 'purge/Menu/MenuBarView.swift').read_text()
        self.assertTrue('Text(LocalizedStringKey(title))' in menu, 'Menu row still displays raw keys')

    def test_native_bundle_formats_chinese_dynamic_counts_and_times(self):
        strings = translations()
        for key in ['%@ safe to clean', '%lldm ago']:
            self.assertTrue(key in strings, f'Cannot resolve native display template: {key}')
        with tempfile.TemporaryDirectory() as tmp:
            bundle = pathlib.Path(tmp) / 'Display.bundle/zh-Hans.lproj'
            bundle.mkdir(parents=True)
            shutil.copy2(RESOURCE, bundle / 'Localizable.strings')
            swift = r'''import Foundation
let zh = Bundle(path: CommandLine.arguments[1])!
func translated(_ key: String) -> String { zh.localizedString(forKey: key, value: nil, table: "Localizable") }
precondition(translated("App Caches") == "应用缓存")
precondition(translated("Clean Safe Items") == "清理安全项目")
precondition(String(format: translated("%@ safe to clean"), "225.8 MB") == "225.8 MB 可安全清理")
precondition(String(format: translated("%lldm ago"), Int64(5)) == "5 分钟前")
precondition(translated("just now") == "刚刚")
precondition(translated("Untranslated User Filename.txt") == "Untranslated User Filename.txt")
print("Dynamic Chinese display formatting and original-name fallback passed")
'''
            result = subprocess.run(['xcrun', 'swift', '-e', swift, str(bundle)], check=True, capture_output=True, text=True)
            self.assertIn('original-name fallback passed', result.stdout)

    def test_actual_foundation_time_helpers_resolve_the_main_bundle_language(self):
        with tempfile.TemporaryDirectory() as tmp:
            app = pathlib.Path(tmp) / 'DisplayProbe.app/Contents'
            executable = app / 'MacOS/DisplayProbe'
            executable.parent.mkdir(parents=True)
            resources = app / 'Resources/zh-Hans.lproj'
            resources.mkdir(parents=True)
            shutil.copy2(RESOURCE, resources / 'Localizable.strings')
            (app / 'Info.plist').write_bytes(plistlib.dumps({
                'CFBundleExecutable': 'DisplayProbe', 'CFBundleIdentifier': 'local.purge.display-probe',
                'CFBundleName': 'DisplayProbe', 'CFBundlePackageType': 'APPL',
                'CFBundleDevelopmentRegion': 'en', 'CFBundleLocalizations': ['en', 'zh-Hans'],
            }))
            main = pathlib.Path(tmp) / 'main.swift'
            main.write_text(r'''import Foundation
let now = Date(timeIntervalSince1970: 1700000000)
if CommandLine.arguments.contains("expectEnglish") {
    precondition(compactAgoText(from: now, to: now) == "just now")
    precondition(compactAgoText(from: now.addingTimeInterval(-300), to: now) == "5m ago")
    precondition(relativeDateText(for: now, referenceDate: now) == "Today")
    print("Actual English fallback getters passed")
} else {
    precondition(compactAgoText(from: now, to: now) == "刚刚")
    precondition(compactAgoText(from: now.addingTimeInterval(-300), to: now) == "5 分钟前")
    precondition(relativeDateText(for: now, referenceDate: now) == "今天")
    print("Actual localized time getters passed")
}
''')
            subprocess.run(['xcrun', 'swiftc', str(ROOT / 'purge/Utilities/RelativeDateText.swift'), str(main), '-o', str(executable)], check=True, capture_output=True)
            result = subprocess.run([str(executable), '-AppleLanguages', '(zh-Hans)'], check=True, capture_output=True, text=True)
            self.assertIn('Actual localized time getters passed', result.stdout)
            english = subprocess.run([str(executable), '-AppleLanguages', '(en)', 'expectEnglish'], check=True, capture_output=True, text=True)
            self.assertIn('Actual English fallback getters passed', english.stdout)

    def test_model_ids_commands_and_matching_metadata_stay_original(self):
        import hashlib
        project = (ROOT / 'purge/Models/ProjectModels.swift').read_text()
        metadata = project.split('private static let metadata:', 1)[1].split('nonisolated var explanationKey:', 1)[0]
        self.assertEqual(hashlib.sha256(metadata.encode()).hexdigest(), 'a2c8ad551d071d8e075620b9da9b87095b9f3e380a333dc7d4a99b787d26ac80')
        for command in ['npm install', 'pnpm install', 'yarn install']:
            self.assertIn('return "' + command + '"', project)
        comparison = (ROOT / 'purge/Utilities/OnboardingSizeComparison.swift').read_text()
        self.assertIn('var id: String { symbol + label }', comparison)
        self.assertIn('var displayLabel: String', comparison)
        large = (ROOT / 'purge/Models/LargeFile.swift').read_text()
        self.assertIn('displayNameOverride ?? path.lastPathComponent', large)
        self.assertIn('case "mov", "mp4"', large)

if __name__ == '__main__':
    unittest.main()
