#include "Core/JourneyDialogue.h"
#include <cassert>
#include <iostream>
using namespace survival;
int main(){
 assert(JourneyScenes().size()==12);int lines=0;
 for(int i=0;i<12;++i){const auto& d=JourneyScenes()[i];assert(d.ru.size()==6&&d.en.size()==6);lines+=d.ru.size();JourneyHistory h;JourneyContext c;c.scene=d.first;c.quiet=c.companion=true;c.walking=c.rain=c.rest=c.night=c.water=true;
  for(int j=0;j<i;++j){assert(h.Finish(j));}
  c.hurt=d.trigger==JourneyTrigger::Hurt;assert(h.Pick(c)==i);assert(h.Finish(i));assert(!h.Finish(i));
  c.companion=false;assert(h.Pick(c)==-1);c.companion=true;c.quiet=false;assert(h.Pick(c)==-1);
 }
 assert(lines==72);JourneyHistory bad;bad.heard=1u<<12;assert(!bad.Valid());assert(!bad.Finish(0));bad={};assert(!bad.Finish(-1)&&!bad.Finish(12));
 JourneyContext c;c.scene=20;c.walking=c.hurt=c.quiet=c.companion=true;JourneyHistory h;assert(h.Pick(c)==5);assert(h.Finish(5));assert(h.Pick(c)==-1);
 for(unsigned mask=0;mask<4096;++mask){h.heard=mask;assert(h.Valid());c={};c.scene=28;c.walking=c.rest=c.rain=c.night=c.water=c.quiet=c.companion=true;int p=h.Pick(c);if(p>=0){assert(!(mask&(1u<<p)));assert(JourneyScenes()[p].first<=28&&JourneyScenes()[p].last>=28);}}
 h={};for(int i=0;i<11;++i)h.Finish(i);c={};c.scene=29;c.rest=c.quiet=c.companion=true;assert(h.Pick(c)==-1);c.water=true;assert(h.Pick(c)==11);
 std::cout<<"JOURNEY_TEST_PASS 72_bilingual_lines 4096_history_masks context_safety injury_priority water_context\n";
}
