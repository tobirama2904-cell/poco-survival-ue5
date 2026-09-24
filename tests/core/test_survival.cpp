#include "Core/SurvivalCore.h"
#include <cstdlib>
#include <iostream>
#include <queue>
#include <random>
#include <sstream>
using namespace survival;
static int checks = 0;
#define CHECK(x) do { ++checks; if (!(x)) { std::cerr << "FAIL line " << __LINE__ << ": " << #x << '\n'; std::exit(1); } } while (false)
static void Apply(Runtime& r, const std::string& id) { CHECK(r.TryAction(id) == Error::None); }
static void Repair(Runtime& r) { Apply(r,"search_depot"); Apply(r,"recover_fuel"); Apply(r,"repair_generator"); }
static std::string Key(const Snapshot& s) {
    std::ostringstream out;
    for (const auto& x : s.completed) out << x << ';';
    return out.str();
}
int main() {
    CHECK(ValidateWorld(MakeCampaign()) == Error::None);
    Runtime initial;
    CHECK(initial.AvailableActions().size() == 4);
    CHECK(initial.CarriedGrams() == 0);
    auto before = initial.State();
    CHECK(initial.TryAction("not_an_action") == Error::UnknownAction);
    CHECK(initial.TryAction("repair_generator") == Error::MissingItem);
    CHECK(initial.TryAction("power_clinic") == Error::MissingPrerequisite);
    CHECK(initial.State() == before);
    Apply(initial,"search_depot");
    before = initial.State();
    CHECK(initial.TryAction("search_depot") == Error::AlreadyCommitted);
    CHECK(initial.State() == before);
    CHECK(initial.CarriedGrams() == 2400);

    for (const bool clinic : {false,true}) for (const bool local : {false,true}) {
        Runtime r;
        // Exploration rewards can precede the story; no forced quest ordering.
        Apply(r,"recover_relay"); Apply(r,"recover_handle"); Repair(r);
        Apply(r,clinic ? "power_clinic" : "power_pumps");
        before = r.State();
        CHECK(r.TryAction(clinic ? "power_pumps" : "power_clinic") == Error::ConflictingChoice);
        CHECK(r.State() == before);
        Apply(r,clinic ? "open_manual_bypass" : "start_pumps");
        CHECK(r.HasFlag("water_restored"));
        CHECK(r.HasFlag("manual_bypass") == clinic);
        Apply(r,local ? "connect_local_network" : "send_evacuation_beacon");
        before = r.State();
        CHECK(r.TryAction(local ? "send_evacuation_beacon" : "connect_local_network") == Error::ConflictingChoice);
        CHECK(r.State() == before);
        Runtime restored;
        CHECK(restored.Restore(r.State()) == Error::None);
        CHECK(restored.State() == r.State());
        CHECK(restored.HasFlag("local_network") == local);
        CHECK(restored.CarriedGrams() == (clinic ? 0 : 1400));
    }
    auto limited = MakeCampaign(); limited.carryLimitGrams = 3000;
    Runtime heavy(limited); Apply(heavy,"search_depot"); before = heavy.State();
    CHECK(heavy.TryAction("recover_fuel") == Error::CapacityExceeded);
    CHECK(heavy.State() == before); // No grant, flag, action record or revision leaks.

    Runtime r; Repair(r); before = r.State();
    for (int corruption=0; corruption<9; ++corruption) {
        auto bad = r.State();
        switch(corruption) {
        case 0: bad.version=99; break;
        case 1: bad.inventory["fuel"]=-1; break;
        case 2: bad.inventory["unknown"]=1; break;
        case 3: bad.flags.insert("water_restored"); break;
        case 4: bad.completed.insert("nonexistent"); break;
        case 5: ++bad.revision; break;
        case 6: bad.journal.push_back("search_depot"); ++bad.revision; break;
        case 7: std::swap(bad.journal[0],bad.journal[2]); break;
        case 8: bad.inventory["fuel"]=2147483647; break;
        }
        CHECK(r.Restore(bad) != Error::None); CHECK(r.State() == before);
    }
    for (int corruption=0; corruption<7; ++corruption) {
        auto world=MakeCampaign();
        switch(corruption) {
        case 0: world.actions.push_back(world.actions[0]); break;
        case 1: world.items["fuel"].grams=-1; break;
        case 2: world.actions[0].grants["nonexistent"]=1; break;
        case 3: world.actions[0].requiredFlags.insert("typo"); break;
        case 4: world.actions[0].district="missing"; break;
        case 5: world.actions[0].sets={"clinic_power","pump_power"}; break;
        case 6: world.items["fuel"].stackLimit=0; break;
        }
        CHECK(ValidateWorld(world) == Error::InvalidDefinition);
        Runtime invalid(world); CHECK(invalid.TryAction("search_depot") == Error::InvalidDefinition);
    }
    // Exhaustive state-graph walk: each reachable state has a completion route.
    // Distinct histories with identical committed actions are equivalent here.
    std::queue<Snapshot> queue; queue.push(Runtime().State()); Flags seen; int terminals=0;
    while (!queue.empty()) {
        const auto state=queue.front(); queue.pop();
        if (!seen.insert(Key(state)).second) continue;
        Runtime current; CHECK(current.Restore(state)==Error::None);
        const auto available=current.AvailableActions();
        if (available.empty()) {
            CHECK(current.HasFlag("local_network") || current.HasFlag("evacuation_beacon"));
            ++terminals;
        }
        for (const auto& id : available) {
            Runtime next; CHECK(next.Restore(state)==Error::None); Apply(next,id);
            CHECK(next.State().revision == state.revision+1); queue.push(next.State());
        }
    }
    CHECK(terminals == 4);
    std::mt19937 rng(0x504F434F);
    for (int trial=0; trial<200; ++trial) {
        Runtime random;
        for (int step=0; step<80; ++step) {
            const auto& definitions=random.Definition().actions;
            const auto id=definitions[rng()%definitions.size()].id; before=random.State();
            const auto error=random.TryAction(id);
            if (error!=Error::None) CHECK(random.State()==before);
            CHECK(random.CarriedGrams()<=random.Definition().carryLimitGrams);
            Runtime copy; CHECK(copy.Restore(random.State())==Error::None);
        }
    }
    std::cout << "CORE_TEST_PASS checks=" << checks << " reachable_states=" << seen.size()
              << " terminal_variants=" << terminals << " randomized_attempts=16000\n";
}
