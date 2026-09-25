#pragma once
#include "Core/FieldSurvival.h"
#include <algorithm>
#include <cmath>
namespace survival {
// A crouched probe must stay above the floor, not reuse a standing capsule.
inline float CompanionProbeHalf(float actualHalf){return std::max(40.f,std::min(70.f,actualHalf-5.f));}
enum class AidResult { Idle,Approaching,Treating,Completed,Cancelled };
struct AidContext {bool near=false,clear=false,still=false,safe=true,allowed=true;};
class CompanionAid {
 float elapsed=0,contact=0;bool active=false;
public:
 bool Active()const{return active;}
 float Progress()const{return contact/2.5f;}
 void Cancel(){active=false;elapsed=contact=0;}
 bool Begin(float health,const Trauma& wounds,const FieldKit& kit){
  if(active||!std::isfinite(health)||health<=0||health>100||!wounds.Valid()||!kit.Valid()||kit.Get(Supply::Bandage)<1||(health>=100&&wounds.bleeding<=0))return false;
  active=true;elapsed=contact=0;return true;
 }
 AidResult Step(float dt,const AidContext& c,float& health,Trauma& wounds,FieldKit& kit){
  if(!active)return AidResult::Idle;
  if(!std::isfinite(dt)||dt<=0)return AidResult::Approaching;
  if(!c.safe||!c.allowed||!std::isfinite(health)||health<=0||health>100||!wounds.Valid()||!kit.Valid()||kit.Get(Supply::Bandage)<1||(health>=100&&wounds.bleeding<=0)){Cancel();return AidResult::Cancelled;}
  dt=std::min(dt,.25f);elapsed+=dt;
  if(elapsed>12.f){Cancel();return AidResult::Cancelled;}
  if(!c.near||!c.clear||!c.still){contact=0;return AidResult::Approaching;}
  contact+=dt;if(contact+1e-5f<2.5f)return AidResult::Treating;
  if(!kit.Spend(Supply::Bandage)){Cancel();return AidResult::Cancelled;}
  wounds.Bandage();health=std::min(100.f,health+32.f);Cancel();return AidResult::Completed;
 }
};
}
