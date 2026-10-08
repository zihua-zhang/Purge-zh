import Foundation

/// The personal test build keeps vendor data and services separate.
nonisolated enum PurgeLocalBuild {
    static var isEnabled: Bool {
#if PURGE_LOCAL_BUILD
        true
#else
        false
#endif
    }
    static var supportComponent: String {
        isEnabled ? "io.getpurge.app.zhlocal" : "io.getpurge.app"
    }
}
