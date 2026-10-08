import Foundation
@main
struct LocalBuildStorageTests {
    static func main() {
        let actual = FirstRunGate.defaultSupportDirectory()?.lastPathComponent
        #if PURGE_LOCAL_BUILD
        let expected = "io.getpurge.app.zhlocal"
#else
        let expected = "io.getpurge.app"
#endif
        guard actual == expected else {
            fputs("FAIL: local build would share the vendor data directory: \(actual ?? "nil")\n", stderr)
            exit(1)
        }
        print("PASS: local build storage does not share the vendor data directory")
    }
}
