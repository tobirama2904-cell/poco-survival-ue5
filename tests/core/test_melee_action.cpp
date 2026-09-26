#include "Core/MeleeAction.h"
#include <cassert>
#include <limits>
#include <iostream>
using namespace survival;
int main(){
 for(int hz:{15,30,60,120}){MeleeAction a;assert(a.Begin());assert(!a.Begin());int hits=0;for(int i=0;i<hz*2;++i)if(a.Step(1.f/hz)){++hits;assert(a.time>=.2999f);}assert(hits==1&&!a.active);}
 MeleeAction a;a.Begin();assert(!a.Step(.1f));a.Cancel();assert(!a.Step(1));assert(a.Begin());assert(!a.Step(-1)&&!a.Step(std::numeric_limits<float>::quiet_NaN()));assert(a.Step(1));assert(!a.active&&!a.Step(.1f));a.Cancel();assert(a.Begin());assert(!a.Step(.29f));assert(a.Step(.01f));assert(!a.Step(.4f));assert(a.active);assert(!a.Step(.1f)&&!a.active);
 std::cout<<"MELEE_TIMING_PASS 15_30_60_120hz single_impact cancellation no_duplicate_input finite_hitch\n";
}
