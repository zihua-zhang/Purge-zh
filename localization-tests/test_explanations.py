"""Regression checks for readable cache explanations; no app launch required."""
import hashlib
import json
import pathlib
import plistlib
import re
import subprocess
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
DATABASE = ROOT / 'purge/Resources/explanations.json'
RESOURCE = ROOT / 'purge/zh-Hans.lproj/Explanations.strings'

class ExplanationLocalizationTests(unittest.TestCase):
    def translations(self):
        self.assertTrue(RESOURCE.exists(), 'Chinese cache-safety explanation table is missing')
        return plistlib.loads(subprocess.check_output(['plutil', '-convert', 'xml1', '-o', '-', str(RESOURCE)]))

    def test_every_database_name_and_explanation_has_chinese(self):
        translations = self.translations()
        entries = json.loads(DATABASE.read_text())
        keys = {entry[field] for entry in entries for field in ['display_name', 'explanation']}
        self.assertEqual(len(entries), 282)
        self.assertEqual(len(keys), 564)
        self.assertEqual(set(translations), keys)
        for key in keys:
            with self.subTest(key=key):
                self.assertRegex(translations[key], r'[\u4e00-\u9fff]')

    def test_format_arguments_match_english_sources(self):
        translations = self.translations()
        placeholders = re.compile(r'%(?:\d+\$)?[-+0#]*\d*(?:\.\d+)?(?:ll|l|h)?[@dfiu]')
        for key, value in translations.items():
            with self.subTest(key=key):
                self.assertEqual(sorted(placeholders.findall(key)), sorted(placeholders.findall(value)))

    def test_warnings_keep_rebuild_cost_and_manual_restore_steps(self):
        translations = self.translations()
        entries = {entry['key']: entry for entry in json.loads(DATABASE.read_text())}
        requirements = {
            'adobe-media-cache-files': ['大型项目', '几分钟'],
            'cloudkit': ['不会丢失', '重新同步', '较慢'],
            'ms-playwright': ['测试', '失败', 'npx playwright install', '重新下载'],
            'node-modules': ['旧项目', 'npm install'],
            'macos-installer': ['12', '15', 'USB', '保留'],
            'archives': ['检查', '重要'],
            'docker': ['所有镜像', '容器', '卷', '没有其他副本', 'docker --context desktop-linux system prune', '运行时', '先退出'],
            'maven': ['mvn install', '重新构建后才能恢复'],
            'sbt': ['耗时较长', '无法离线'],
            'gradle-global-cache': ['耗时较长', '无法离线'],
            'cocoapods-spec-repos': ['pod install', 'pod repo add', '私有', '手动重新添加'],
            'xcode-archives': ['删除后无法恢复', '不再需要'],
            'gitworktrees': ['不再使用', '未保存的工作'],
            'iossimulators': ['也会删除', '应用与数据'],
            'telegram-media-cache': ['秘密聊天', '仅保存在这台 Mac'],
            'screen-time': ['清空', '历史与报告', '无法恢复'],
            'orphaned-git-worktree': ['未提交的工作'],
            'orphaned-editor-workspace-storage': ['AI 聊天历史', '移动或重命名', '聊天记录仍保存在这里'],
            'unity-temp': ['打开时请勿移除'],
            'unity-library': ['大型项目', '耗时很长', '移除前请检查'],
            'venv': ['requirements.txt', 'pyproject.toml', '重新安装', '互联网连接'],
            'mail-downloads': ['原件仍保留', '修改只保存在这里', '打开时', '暂不纳入清理'],
            'xctest-devices': ['没有测试运行时'],
            'puppeteer-browsers': ['脚本会失败', 'npm install', 'npx puppeteer browsers install'],
            'conda-packages': ['通过链接', '仍可继续运行', '空间会少于显示值', 'conda clean --all'],
        }
        for entry_key, expected in requirements.items():
            value = translations[entries[entry_key]['explanation']]
            for phrase in expected:
                with self.subTest(entry=entry_key, phrase=phrase):
                    self.assertIn(phrase, value)

    def test_original_matching_and_risk_database_is_unchanged(self):
        self.assertEqual(hashlib.sha256(DATABASE.read_bytes()).hexdigest(), '7cbefc21c390c4696fc36dbde28bf16b1cbdd24c6093620a2ac58eded62fcf06')

if __name__ == '__main__':
    unittest.main()
