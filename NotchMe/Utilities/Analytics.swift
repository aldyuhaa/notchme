import Foundation

/// Usage analytics (currently disabled).
/// Previously reported to Aptabase under the upstream author's key.
/// To re-enable: add the Aptabase Swift package back in project.yml,
/// `import Aptabase` here, and initialize with YOUR OWN app key from aptabase.com.
enum Analytics {
    /// Call once at app launch — safe to call multiple times.
    static func start() {}

    /// Fire a named event with optional key/value properties.
    /// Safe to call from anywhere; currently a no-op.
    static func track(_ event: String, properties: [String: Any]? = nil) {}
}
