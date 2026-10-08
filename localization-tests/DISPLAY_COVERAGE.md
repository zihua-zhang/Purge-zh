# 动态界面本地化核查

主界面资源表现有 768 个键；安全说明使用独立的 `Explanations.strings` 表，覆盖 282 个名称和 282 段说明，共 564 个键。

普通 `String` 进入自定义组件时不会自动成为翻译键。设置页、概览、侧栏和菜单通过标准 Foundation / SwiftUI 本地化 API 读取显示名称；带数量、大小和时间的说明在组装时读取完整句子的资源，避免把实际数字拼成无法命中的翻译键。

原始设置值、枚举标识、缓存匹配元数据、文件路径、恢复命令和用户文件名继续使用原值。空间比较保留原来的标签与身份标识，单独提供中文显示值；完成提示保存的原始鼓励文案也保持原样。风险分类和删除操作未修改。

```sh
python3 -m unittest discover -s localization-tests
scripts/build-zh.sh
python3 localization-tests/audit_display_keys.py ../构建输出/PurgeLocal/Build/Intermediates.noindex/purge-local.build/Debug/purge.build/Objects-normal/arm64 --report localization-tests/display-coverage.json
```

15 项本地化检查已通过，其中包括临时 Foundation 进程实际调用日期显示函数，核查简体中文和英语回退。此检查不启动 Purge，不创建 AppKit 界面，不请求系统权限。原始安全说明数据库字节和开发产物匹配元数据也有一致性检查。

最终主应用编译成功，并通过本地临时签名验证。编译器提取 646 个键，637 个有中文资源，另外 9 个为品牌名、数字单位或仅格式占位符；未发现遗漏的可翻译编译器键。人工界面检查由安装流程单独进行。用户内容及系统或库返回的诊断信息保留其原始语言，不能将静态覆盖数字视作所有运行时数据都已翻译。

`translation-map.json` 与原生主界面资源表保持同步，可供后续跟进上游时补充和核查翻译。
