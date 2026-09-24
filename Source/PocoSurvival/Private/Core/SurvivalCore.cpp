#include "Core/SurvivalCore.h"
#include <algorithm>
#include <limits>
#include <utility>
namespace survival {
namespace {
constexpr std::uint64_t MaxRevision = static_cast<std::uint64_t>(std::numeric_limits<std::int64_t>::max());
bool ContainsAll(const Flags& have, const Flags& need) {
    return std::all_of(need.begin(), need.end(), [&](const auto& id) { return have.count(id) != 0; });
}
bool Overlap(const Flags& a, const Flags& b) {
    return std::any_of(a.begin(), a.end(), [&](const auto& id) { return b.count(id) != 0; });
}
const Action* Find(const World& world, const std::string& id) {
    const auto it = std::find_if(world.actions.begin(), world.actions.end(), [&](const auto& a) { return a.id == id; });
    return it == world.actions.end() ? nullptr : &*it;
}
}
bool Snapshot::operator==(const Snapshot& b) const {
    return version == b.version && revision == b.revision && inventory == b.inventory && flags == b.flags && completed == b.completed && journal == b.journal;
}
const char* Explain(Error e) {
    switch (e) {
    case Error::None: return "ok";
    case Error::InvalidDefinition: return "invalid_world_definition";
    case Error::UnknownAction: return "unknown_action";
    case Error::AlreadyCommitted: return "action_already_committed";
    case Error::MissingPrerequisite: return "missing_prerequisite";
    case Error::ConflictingChoice: return "conflicting_choice";
    case Error::MissingItem: return "missing_item";
    case Error::CapacityExceeded: return "inventory_capacity_exceeded";
    case Error::InvalidSnapshot: return "invalid_save_state";
    case Error::RevisionLimit: return "save_revision_limit";
    }
    return "unknown_error";
}
Error ValidateWorld(const World& w) {
    if (w.carryLimitGrams <= 0 || w.carryLimitGrams > 1000000 || w.actions.empty() || w.actions.size() > 4096)
        return Error::InvalidDefinition;
    for (const auto& entry : w.items)
        if (entry.first.empty() || entry.second.grams <= 0 || entry.second.grams > 1000000 ||
            entry.second.stackLimit <= 0 || entry.second.stackLimit > 1000000) return Error::InvalidDefinition;
    if (w.flags.count("") || w.districts.count("")) return Error::InvalidDefinition;
    for (const auto& group : w.exclusiveGroups)
        if (group.size() < 2 || !ContainsAll(w.flags, group)) return Error::InvalidDefinition;
    Flags ids;
    for (const auto& a : w.actions) {
        if (a.id.empty() || a.title.empty() || !ids.insert(a.id).second || !w.districts.count(a.district) ||
            !ContainsAll(w.flags, a.requiredFlags) || !ContainsAll(w.flags, a.forbids) || !ContainsAll(w.flags, a.sets) ||
            Overlap(a.requiredFlags, a.forbids) || Overlap(a.sets, a.forbids)) return Error::InvalidDefinition;
        for (const auto* counts : {&a.consumes, &a.grants})
            for (const auto& entry : *counts) {
                const auto item = w.items.find(entry.first);
                if (item == w.items.end() || entry.second <= 0 || entry.second > item->second.stackLimit)
                    return Error::InvalidDefinition;
            }
        for (const auto& group : w.exclusiveGroups) {
            Flags resulting = a.requiredFlags; resulting.insert(a.sets.begin(), a.sets.end());
            std::size_t count = 0;
            for (const auto& flag : group) count += resulting.count(flag);
            if (count > 1) return Error::InvalidDefinition;
        }
    }
    return Error::None;
}
Runtime::Runtime(World world) : world_(std::move(world)), definitionStatus_(ValidateWorld(world_)) {}
Error Runtime::ValidateSnapshot(const Snapshot& s) const {
    if (definitionStatus_ != Error::None) return definitionStatus_;
    if (s.version != 1 || s.revision > MaxRevision || s.revision != s.journal.size() ||
        s.journal.size() > world_.actions.size()) return Error::InvalidSnapshot;
    Runtime replay(world_);
    for (const auto& id : s.journal)
        if (replay.TryAction(id) != Error::None) return Error::InvalidSnapshot;
    return replay.State() == s ? Error::None : Error::InvalidSnapshot;
}
Error Runtime::Prepare(const std::string& id, Snapshot& next) const {
    if (definitionStatus_ != Error::None) return definitionStatus_;
    const auto* a = Find(world_, id);
    if (!a) return Error::UnknownAction;
    if (state_.completed.count(id)) return Error::AlreadyCommitted;
    if (!ContainsAll(state_.flags, a->requiredFlags)) return Error::MissingPrerequisite;
    if (Overlap(state_.flags, a->forbids)) return Error::ConflictingChoice;
    if (state_.revision >= MaxRevision) return Error::RevisionLimit;
    next = state_;
    for (const auto& e : a->consumes) {
        auto it = next.inventory.find(e.first);
        if (it == next.inventory.end() || it->second < e.second) return Error::MissingItem;
        it->second -= e.second;
        if (it->second == 0) next.inventory.erase(it);
    }
    for (const auto& e : a->grants) {
        const auto current = next.inventory.find(e.first);
        const std::int64_t count = (current == next.inventory.end() ? 0 : current->second) + static_cast<std::int64_t>(e.second);
        const auto item = world_.items.find(e.first);
        if (count > item->second.stackLimit) return Error::CapacityExceeded;
        next.inventory[e.first] = static_cast<std::int32_t>(count);
    }
    next.flags.insert(a->sets.begin(), a->sets.end());
    next.completed.insert(id); next.journal.push_back(id); ++next.revision;
    for (const auto& group : world_.exclusiveGroups) {
        std::size_t count = 0;
        for (const auto& flag : group) count += next.flags.count(flag);
        if (count > 1) return Error::ConflictingChoice;
    }
    std::int64_t mass = 0;
    for (const auto& e : next.inventory) {
        mass += static_cast<std::int64_t>(e.second) * world_.items.find(e.first)->second.grams;
        if (mass > world_.carryLimitGrams) return Error::CapacityExceeded;
    }
    return Error::None;
}
Error Runtime::TryAction(const std::string& id) {
    Snapshot next;
    const auto error = Prepare(id, next);
    if (error == Error::None) state_ = std::move(next);
    return error;
}
Error Runtime::CanApply(const std::string& id) const { Snapshot ignored; return Prepare(id, ignored); }
std::vector<std::string> Runtime::AvailableActions() const {
    std::vector<std::string> result;
    for (const auto& a : world_.actions) if (CanApply(a.id) == Error::None) result.push_back(a.id);
    return result;
}
Error Runtime::Restore(const Snapshot& candidate) {
    const auto error = ValidateSnapshot(candidate);
    if (error == Error::None) state_ = candidate;
    return error;
}
bool Runtime::HasFlag(const std::string& flag) const { return state_.flags.count(flag) != 0; }
std::int64_t Runtime::CarriedGrams() const {
    std::int64_t result = 0;
    for (const auto& e : state_.inventory) result += static_cast<std::int64_t>(e.second) * world_.items.find(e.first)->second.grams;
    return result;
}
} // namespace survival
