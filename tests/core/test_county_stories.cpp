#include "Core/CountyStories.h"
#include <cassert>
#include <iostream>
using namespace survival;
int main(){
 assert(CountyArcs().size()==6);int lines=0;
 for(const auto& arc:CountyArcs())for(const auto& beat:arc.beats){assert(beat.ru.size()==beat.en.size());assert(beat.ru.size()==6);lines+=beat.ru.size();}
 assert(lines==144);
 for(int bits=0;bits<64;++bits){CountyState s;FieldKit kit;assert(kit.Add(Supply::Wood,6)&&kit.Add(Supply::Scrap,6));
  for(int i=0;i<6;++i){assert(s.Apply(i,2,kit)==CountyResult::WrongOrder);assert(s.Apply(i,0,kit)==CountyResult::Advanced);assert(s.Apply(i,0,kit)==CountyResult::Replay);assert(s.Apply(i,1,kit)==CountyResult::Advanced);auto before=kit.items;assert(s.Apply(i,1,kit)==CountyResult::Replay);assert(kit.items==before);int choice=(bits&(1<<i))?3:2;assert(s.Apply(i,choice,kit)==CountyResult::Advanced);before=kit.items;assert(s.Apply(i,choice,kit)==CountyResult::Replay);assert(kit.items==before);assert(s.Apply(i,choice==2?3:2,kit)==CountyResult::WrongOrder);}
  assert(s.Complete()==6&&s.Valid()&&kit.Valid());assert(kit.Get(Supply::Wood)==0&&kit.Get(Supply::Scrap)==0);
 }
 CountyState s;FieldKit kit;assert(s.Apply(-1,0,kit)==CountyResult::Invalid);assert(s.Apply(6,0,kit)==CountyResult::Invalid);assert(s.Apply(0,4,kit)==CountyResult::Invalid);
 assert(s.Apply(0,0,kit)==CountyResult::Advanced);assert(kit.Add(Supply::Scrap,1));auto before=kit.items;assert(s.Apply(0,1,kit)==CountyResult::Resources);assert(kit.items==before&&s.stages[0]==1);
 s.stages[0]=5;assert(!s.Valid());s.stages[0]=-1;assert(!s.Valid());
 s={};s.stages[0]=2;kit={};assert(kit.Add(Supply::Wood,96));before=kit.items;assert(s.Apply(0,3,kit)==CountyResult::Resources);assert(kit.items==before&&s.stages[0]==2);assert(s.Apply(0,2,kit)==CountyResult::Advanced);
 std::cout<<"COUNTY_STORY_PASS 144_bilingual_lines 64_choice_combinations atomic_costs no_reward_farming irreversible_choices capacity_failure\n";
}
