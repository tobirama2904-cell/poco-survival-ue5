#pragma once
#include <cstdint>
#include <map>
#include <set>
#include <string>
#include <vector>

// Engine-independent domain code, compiled both by UBT and native C++ tests.
namespace survival {
using Counts = std::map<std::string, std::int32_t>;
using Flags = std::set<std::string>;
struct Item { std::int32_t grams; std::int32_t stackLimit; };
struct Action {
    std::string id;
    std::string district;
    std::string title;
    Flags requiredFlags;
    Flags forbids;
    Counts consumes;
    Counts grants;
    Flags sets;
};
struct World {
    std::map<std::string, Item> items;
    Flags flags;
    Flags districts;
    std::vector<Flags> exclusiveGroups;
    std::vector<Action> actions;
    std::int64_t carryLimitGrams = 12000;
};
struct Snapshot {
    std::int32_t version = 1;
    std::uint64_t revision = 0;
    Counts inventory;
    Flags flags;
    Flags completed;
    std::vector<std::string> journal;
    bool operator==(const Snapshot& other) const;
};
enum class Error {
    None, InvalidDefinition, UnknownAction, AlreadyCommitted,
    MissingPrerequisite, ConflictingChoice, MissingItem,
    CapacityExceeded, InvalidSnapshot, RevisionLimit
};
const char* Explain(Error error);
World MakeCampaign();
Error ValidateWorld(const World& world);
class Runtime {
public:
    explicit Runtime(World world = MakeCampaign());
    Error TryAction(const std::string& id);
    Error Restore(const Snapshot& candidate);
    Error CanApply(const std::string& id) const;
    std::vector<std::string> AvailableActions() const;
    const Snapshot& State() const { return state_; }
    const World& Definition() const { return world_; }
    std::int64_t CarriedGrams() const;
    bool HasFlag(const std::string& flag) const;
private:
    Error Prepare(const std::string& id, Snapshot& candidate) const;
    Error ValidateSnapshot(const Snapshot& candidate) const;
    World world_;
    Snapshot state_;
    Error definitionStatus_;
};
} // namespace survival
