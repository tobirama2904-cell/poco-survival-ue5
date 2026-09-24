#include "Core/SurvivalCore.h"
namespace survival {
World MakeCampaign() {
    World w;
    w.items = {{"starter_coil", {2400, 1}}, {"fuel", {1800, 2}}, {"valve_handle", {1400, 1}}, {"relay", {600, 1}}};
    w.districts = {"depot", "canal", "residential", "pumpworks", "relay_tower"};
    w.flags = {"generator_running", "clinic_power", "pump_power", "manual_bypass", "water_restored", "local_network", "evacuation_beacon"};
    w.exclusiveGroups = {{"clinic_power", "pump_power"}, {"local_network", "evacuation_beacon"}};
    // Authored quest-state foundation. No levels, dialogue performances or
    // campaign duration are implied by these action definitions.
    w.actions = {
        {"search_depot", "depot", "Запасная катушка", {}, {}, {}, {{"starter_coil",1}}, {}},
        {"recover_fuel", "canal", "Канистра у шлюза", {}, {}, {}, {{"fuel",1}}, {}},
        {"recover_handle", "residential", "Ручной привод", {}, {}, {}, {{"valve_handle",1}}, {}},
        {"recover_relay", "relay_tower", "Уцелевшее реле", {}, {}, {}, {{"relay",1}}, {}},
        {"repair_generator", "depot", "Вернуть ток", {}, {}, {{"starter_coil",1},{"fuel",1}}, {}, {"generator_running"}},
        {"power_clinic", "depot", "Сначала лазарет", {"generator_running"}, {"pump_power"}, {}, {}, {"clinic_power"}},
        {"power_pumps", "depot", "Сначала насосы", {"generator_running"}, {"clinic_power"}, {}, {}, {"pump_power"}},
        {"open_manual_bypass", "pumpworks", "Вода без электричества", {"clinic_power"}, {}, {{"valve_handle",1}}, {}, {"manual_bypass","water_restored"}},
        {"start_pumps", "pumpworks", "Запуск насосной", {"pump_power"}, {}, {}, {}, {"water_restored"}},
        {"connect_local_network", "relay_tower", "Остаться и соединить кварталы", {"water_restored"}, {"evacuation_beacon"}, {{"relay",1}}, {}, {"local_network"}},
        {"send_evacuation_beacon", "relay_tower", "Позвать эвакуацию", {"water_restored"}, {"local_network"}, {{"relay",1}}, {}, {"evacuation_beacon"}}
    };
    return w;
}
} // namespace survival
