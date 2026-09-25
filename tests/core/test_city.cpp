#include "Core/CityContent.h"
#include <iostream>
#include <cstdlib>
#include <random>
using namespace survival;
#define CHECK(x) do { if(!(x)) { std::cerr<<"CITY FAIL "<<__LINE__<<" "<<#x<<"\n";std::exit(1); } } while(false)
void Apply(Runtime& r,const char* id){CHECK(r.TryAction(id)==Error::None);}
int main(){
 auto w=MakeCityCampaign();CHECK(ValidateWorld(w)==Error::None);CHECK(w.actions.size()==61);CHECK(CitySites().size()==61);
 for(const auto& a:w.actions)CHECK(FindCitySite(a.id)!=nullptr);
 for(bool clinic:{false,true})for(bool stay:{false,true})for(bool truth:{false,true}){
  Runtime r(w);for(int i=0;i<6;++i)CHECK(r.TryAction("supply_"+std::to_string(i))==Error::None);
  for(auto a:{"meet_dispatch","inspect_break","read_orders","search_depot","recover_fuel","repair_generator","collect_clinic_key","unlock_clinic","meet_doctor","find_antibiotics","deliver_antibiotics","recover_handle","recover_relay"})Apply(r,a);
  Apply(r,clinic?"power_clinic":"power_pumps");Apply(r,clinic?"open_manual_bypass":"start_pumps");
  for(auto a:{"check_reservoir","sample_water","analyze_sample","speak_guard","find_logbook","trace_pipeline","retrieve_filter","install_filter","radio_brother","find_rooftop_key","rescue_brother","assemble_receiver"})Apply(r,a);
  Apply(r,truth?"broadcast_truth":"seal_records");CHECK(r.TryAction(truth?"seal_records":"broadcast_truth")==Error::ConflictingChoice);
  Apply(r,stay?"connect_local_network":"send_evacuation_beacon");Apply(r,"open_shelter");Apply(r,"repair_lift");Apply(r,stay?"settle_districts":"lead_evacuation");
  CHECK(r.HasFlag("campaign_resolution"));CHECK(r.HasFlag("ending_stay")==stay);
  // Side quests and crafting remain available after the story resolution.
  for(auto a:{"find_mina_letter","deliver_mina_letter","find_tools","repair_bridge","craft_medkit_0","use_medkit_0"})Apply(r,a);
  auto old=r.State();CHECK(r.TryAction("supply_0")==Error::AlreadyCommitted);CHECK(r.State()==old);
  Runtime loaded(w);CHECK(loaded.Restore(r.State())==Error::None);CHECK(loaded.State()==r.State());
 }
 // Historical foundation journals replay without changed meanings.
 Runtime legacy;for(auto a:{"search_depot","recover_fuel","repair_generator","power_clinic"})Apply(legacy,a);
 Runtime migrated(w);CHECK(migrated.Restore(legacy.State())==Error::None);
 std::mt19937 gen(410);for(int run=0;run<40;++run){Runtime r(w);for(int step=0;step<180;++step){auto old=r.State();auto a=w.actions[gen()%w.actions.size()].id;auto e=r.TryAction(a);if(e!=Error::None)CHECK(r.State()==old);Runtime c(w);CHECK(c.Restore(r.State())==Error::None);}}
 std::cout<<"CITY_TEST_PASS actions=61 sites=61 tested_branch_combinations=8 replay_and_optional_postgame=true duration_not_measured=true\n";
}
