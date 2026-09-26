#pragma once
#include <algorithm>
#include <cmath>
namespace survival {
struct MeleeAction {
 static constexpr float Impact=.30f,Duration=.80f;
 float time=0;bool active=false,hit=false;
 bool Begin(){if(active)return false;time=0;hit=false;active=true;return true;}
 void Cancel(){active=false;time=0;hit=false;}
 bool Step(float dt){
  if(!active||!std::isfinite(dt)||dt<=0)return false;
  time=std::min(Duration,time+std::min(dt,1.f));const bool impact=!hit&&time+1e-6f>=Impact;
  if(impact)hit=true;
  if(time+1e-6f>=Duration)active=false;
  return impact;
 }
};
}
