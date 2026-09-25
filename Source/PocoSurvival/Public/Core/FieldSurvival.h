#pragma once
#include <array>
#include <algorithm>
#include <cmath>
#include <cstdint>
namespace survival {
enum class Supply:int { Cloth,Alcohol,Wood,Scrap,Arrows,Bandage,Splint,Bow,Rounds,Count };
enum class WoundZone:int { Torso,Head,Arm,Leg };
struct Trauma {
 float bleeding=0,arm=0,leg=0,concussion=0;
 bool Valid() const { return std::isfinite(bleeding)&&bleeding>=0&&bleeding<=4&&std::isfinite(arm)&&arm>=0&&arm<=1&&std::isfinite(leg)&&leg>=0&&leg<=1&&std::isfinite(concussion)&&concussion>=0&&concussion<=4; }
 float Hit(float amount,WoundZone zone) {
  if(!std::isfinite(amount)||amount<=0)return 0;
  amount=std::min(amount,100.f);
  if(amount>=12)bleeding=std::min(4.f,bleeding+amount*.012f);
  if(zone==WoundZone::Arm)arm=std::min(1.f,arm+amount*.022f);
  if(zone==WoundZone::Leg)leg=std::min(1.f,leg+amount*.025f);
  if(zone==WoundZone::Head)concussion=std::min(4.f,concussion+amount*.06f);
  return amount*(zone==WoundZone::Head?1.8f:zone==WoundZone::Arm?.6f:zone==WoundZone::Leg?.8f:1.f);
 }
 float Step(float dt,bool paused=false) {
  if(paused||!std::isfinite(dt)||dt<=0)return 0;
  dt=std::min(dt,1.f);concussion=std::max(0.f,concussion-dt*.22f);return bleeding*dt;
 }
 bool CanSprint()const{return leg<.5f;}
 bool CanShoot()const{return arm<.95f;}
 float WalkScale()const{return 1-.55f*leg;}
 void Bandage(){bleeding=0;}
 void Splint(){leg=0;arm=0;}
};
struct FieldKit {
 std::array<int,static_cast<int>(Supply::Count)> items{};
 std::uint32_t looted=0,doors=0;
 static constexpr int CacheCount=24;
 int Get(Supply s)const{return items[static_cast<int>(s)];}
 int Weight()const{constexpr int grams[]={50,200,250,150,30,100,350,900,12};int n=0;for(unsigned i=0;i<items.size();++i)n+=items[i]*grams[i];return n;}
 bool Valid()const {for(int i:items)if(i<0||i>256)return false;return Get(Supply::Bow)<=1&&Weight()<=24000&&(looted>>CacheCount)==0&&(doors>>24)==0;}
 bool Spend(Supply s,int n=1){if(n<1||Get(s)<n)return false;items[static_cast<int>(s)]-=n;return true;}
 bool Add(Supply s,int n){if(n<0||n>256)return false;auto c=*this;c.items[static_cast<int>(s)]+=n;if(!c.Valid())return false;*this=c;return true;}
 bool Loot(int id){
  if(id<0||id>=CacheCount||(looted&(1u<<id)))return false;
  auto c=*this;bool ok=true;
  if(id==0)ok=c.Add(Supply::Bow,1)&&c.Add(Supply::Arrows,6)&&c.Add(Supply::Bandage,2)&&c.Add(Supply::Splint,1);
  else switch(id%4){case 0:ok=c.Add(Supply::Wood,3)&&c.Add(Supply::Scrap,2);break;case 1:ok=c.Add(Supply::Cloth,3)&&c.Add(Supply::Alcohol,2);break;case 2:ok=c.Add(Supply::Arrows,4)&&c.Add(Supply::Rounds,8);break;default:ok=c.Add(Supply::Cloth,2)&&c.Add(Supply::Wood,2)&&c.Add(Supply::Scrap,2);}
  if(!ok){return false;}c.looted|=1u<<id;*this=c;return true;
 }
 bool Craft(int recipe){
  auto c=*this;bool ok=false;
  if(recipe==0)ok=c.Spend(Supply::Cloth)&&c.Spend(Supply::Alcohol)&&c.Add(Supply::Bandage,1);
  if(recipe==1)ok=c.Spend(Supply::Cloth)&&c.Spend(Supply::Wood,2)&&c.Add(Supply::Splint,1);
  if(recipe==2)ok=c.Spend(Supply::Wood)&&c.Spend(Supply::Scrap)&&c.Add(Supply::Arrows,3);
  if(!ok){return false;}*this=c;return true;
 }
};
class BowDraw {
public:
 float time=0;bool drawing=false;
 void Begin(bool available){drawing=available;time=0;}
 void Step(float dt){if(drawing&&std::isfinite(dt)&&dt>0)time=std::min(1.4f,time+std::min(dt,1.f));}
 float Release(){const float power=drawing&&time>=.18f?std::clamp(time/1.1f,.2f,1.f):0;drawing=false;time=0;return power;}
 void Cancel(){drawing=false;time=0;}
};
}
