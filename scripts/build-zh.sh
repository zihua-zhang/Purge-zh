#!/bin/zsh
set -euo pipefail
TASK_SOURCE_ROOT=$(cd "$(dirname "$0")/.." && pwd)
cd "$TASK_SOURCE_ROOT"
python3 - <<'PY'
from pathlib import Path
import shutil,json,subprocess,plistlib
root=Path.cwd(); original=root/'purge.xcodeproj'; project=root/'purge-local.xcodeproj'
if project.exists():shutil.rmtree(project)
shutil.copytree(original,project)
pbx=project/'project.pbxproj'
d=json.loads(subprocess.check_output(['plutil','-convert','json','-o','-',str(pbx)]))
objects=d['objects']; app=next(x for x in objects.values() if x.get('isa')=='PBXNativeTarget' and x.get('name')=='purge')
for configuration in objects[app['buildConfigurationList']]['buildConfigurations']:
 b=objects[configuration]['buildSettings']
 original_info=root/b['INFOPLIST_FILE']
 info=plistlib.loads(original_info.read_bytes())
 for url_type in info.get('CFBundleURLTypes',[]):
  url_type['CFBundleURLName']='io.getpurge.app.zhlocal'
  url_type['CFBundleURLSchemes']=['purge-zhlocal']
 info_path=project/'LocalInfo.plist';info_path.write_bytes(plistlib.dumps(info))
 b['INFOPLIST_FILE']='purge-local.xcodeproj/LocalInfo.plist'
 b['PRODUCT_BUNDLE_IDENTIFIER']='io.getpurge.app.zhlocal'
 b['INFOPLIST_KEY_CFBundleDisplayName']='Purge 中文版'
 b['SWIFT_ACTIVE_COMPILATION_CONDITIONS']='$(inherited) PURGE_LOCAL_BUILD'
for x in objects.values():
 if x.get('isa')=='PBXProject':
  x['knownRegions']=list(dict.fromkeys(x.get('knownRegions',[])+['zh-Hans']))
for p in project.rglob('*.xcscheme'):p.write_text(p.read_text().replace('container:purge.xcodeproj','container:purge-local.xcodeproj'))
pbx.write_text(json.dumps(d));subprocess.run(['plutil','-convert','xml1',str(pbx)],check=True)
PY
/usr/bin/xcodebuild -project purge-local.xcodeproj -scheme purge -configuration Debug -destination 'platform=macOS,arch=arm64' -derivedDataPath '../构建输出/PurgeLocal' -clonedSourcePackagesDirPath '../构建依赖/Purge' -disableAutomaticPackageResolution -jobs 4 CODE_SIGNING_ALLOWED=YES CODE_SIGNING_REQUIRED=YES CODE_SIGN_IDENTITY=- DEVELOPMENT_TEAM= "${1:-build}"
