#include "Core/MainCampaign.h"
#include "Core/AmericanStory.h"
#include <cassert>
#include <iostream>
using namespace survival;
int main(){
 assert(FilmScenes().size()==30);int lines=0;for(const auto& s:FilmScenes()){assert(s.ru.size()==s.en.size());assert(!s.intentRu.empty()&&!s.intentEn.empty());lines+=s.ru.size();}assert(lines==194);
 CampaignState s;FieldKit kit;assert(s.Valid());assert(s.Apply(0,19,kit)==CampaignResult::Locked);assert(s.Apply(1,22,kit)==CampaignResult::Locked);
 assert(kit.Add(Supply::Scrap,1));auto before=kit.items;assert(s.Apply(0,20,kit)==CampaignResult::Resources);assert(kit.items==before&&s.events==0);
 assert(kit.Add(Supply::Wood,1));assert(s.Apply(0,20,kit)==CampaignResult::Advanced);assert(kit.Get(Supply::Wood)==0&&kit.Get(Supply::Scrap)==0);
 assert(s.Apply(0,20,kit)==CampaignResult::Replay);
 for(int mask=0;mask<64;++mask){CampaignState c;c.events=mask;bool expect=mask==0||mask==1||mask==3||mask==7||mask==15||mask==31;assert(c.Valid()==expect);}
 assert(s.Apply(1,22,kit)==CampaignResult::Advanced);assert(kit.Get(Supply::Bandage)==0); // protected quest pack, cannot be consumed by self-healing
 assert(s.Apply(2,24,kit)==CampaignResult::Advanced);assert(s.Apply(3,25,kit)==CampaignResult::Locked);assert(s.Apply(3,26,kit)==CampaignResult::Advanced);assert(s.Apply(4,29,kit)==CampaignResult::Advanced);assert(s.events==31);
 for(int i=0;i<5;++i)assert(s.Apply(i,30,kit)==CampaignResult::Replay);
 assert(s.Apply(-1,30,kit)==CampaignResult::Invalid);assert(s.Apply(6,30,kit)==CampaignResult::Invalid);
 CampaignState recovery;FieldKit empty;assert(recovery.Apply(5,19,empty)==CampaignResult::Locked);assert(recovery.Apply(5,20,empty)==CampaignResult::Advanced);assert(recovery.Apply(5,20,empty)==CampaignResult::Replay);assert(recovery.Apply(0,20,empty)==CampaignResult::Advanced);assert(empty.Weight()==0);
 std::cout<<"MAIN_CAMPAIGN_PASS continuous30scenes 194_bilingual_lines protected_medical_pack ordered_actions atomic_costs\n";
}
