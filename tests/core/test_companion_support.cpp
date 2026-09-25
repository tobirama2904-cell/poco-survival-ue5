#include "Core/CompanionSupport.h"
#include <cassert>
#include <iostream>
#include <limits>
using namespace survival;
int main(){
 assert(CompanionProbeHalf(40)==40&&CompanionProbeHalf(96)==70);
 assert(40+20-CompanionProbeHalf(40)>0);
 for(int hz:{30,60}){CompanionAid aid;FieldKit k;k.Add(Supply::Bandage,2);Trauma w;w.bleeding=1;w.leg=.7f;float hp=50;assert(aid.Begin(hp,w,k));assert(!aid.Begin(hp,w,k));AidContext c;c.near=c.clear=c.still=true;AidResult r=AidResult::Idle;for(int i=0;i<hz*3&&aid.Active();++i)r=aid.Step(1.f/hz,c,hp,w,k);assert(r==AidResult::Completed&&hp==82&&w.bleeding==0&&w.leg==.7f&&k.Get(Supply::Bandage)==1);assert(aid.Step(1,c,hp,w,k)==AidResult::Idle);}
 for(int reason=0;reason<6;++reason){CompanionAid a;FieldKit k;k.Add(Supply::Bandage,1);Trauma w;w.bleeding=1;float hp=60;assert(a.Begin(hp,w,k));AidContext c;c.near=c.clear=c.still=true;a.Step(.25f,c,hp,w,k);
  if(reason==0){c.safe=false;}if(reason==1){c.allowed=false;}if(reason==2){hp=0;}if(reason==3){k.Spend(Supply::Bandage);}if(reason==4){hp=100;w.bleeding=0;}if(reason==5)hp=std::numeric_limits<float>::quiet_NaN();
  const auto before=k.items;assert(a.Step(.25f,c,hp,w,k)==AidResult::Cancelled);assert(k.items==before);
 }
 CompanionAid a;FieldKit k;k.Add(Supply::Bandage,1);Trauma w;float hp=70;assert(a.Begin(hp,w,k));AidContext c;
 for(int i=0;i<52;++i){a.Step(.25f,c,hp,w,k);}
 assert(!a.Active()&&hp==70&&k.Get(Supply::Bandage)==1);
 assert(a.Begin(hp,w,k));c.near=c.clear=c.still=true;for(int i=0;i<9;++i)a.Step(.25f,c,hp,w,k);c.clear=false;a.Step(.25f,c,hp,w,k);c.clear=true;for(int i=0;i<9;++i)a.Step(.25f,c,hp,w,k);assert(a.Active()&&k.Get(Supply::Bandage)==1);assert(a.Step(.25f,c,hp,w,k)==AidResult::Completed&&hp==100);
 std::cout<<"COMPANION_SUPPORT_PASS 30_60hz bounded_approach LOS_contact_reset no_free_healing interruption no_double_spend\n";
}
