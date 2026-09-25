#include "Core/FieldSurvival.h"
#include <cassert>
#include <iostream>
#include <limits>
using namespace survival;
int main(){
 FieldKit k;assert(k.Valid());assert(k.Loot(0));assert(k.Get(Supply::Bow)==1&&k.Get(Supply::Arrows)==6);assert(!k.Loot(0));assert(!k.Loot(-1));assert(!k.Loot(24));
 auto before=k;assert(!k.Craft(0));assert(k.items==before.items&&k.looted==before.looted);
 assert(k.Loot(1));assert(k.Craft(0));assert(k.Get(Supply::Bandage)==3);assert(k.Loot(3));assert(k.Craft(2));assert(k.Get(Supply::Arrows)==9);assert(!k.Craft(99));
 assert(!k.Add(Supply::Cloth,257));assert(!k.Spend(Supply::Cloth,-1));auto bad=k;bad.looted=1u<<24;assert(!bad.Valid());bad=k;bad.items[0]=-1;assert(!bad.Valid());
 for(int hz:{30,60}){Trauma t;float hp=100;assert(t.Hit(30,WoundZone::Leg)==24);assert(!t.CanSprint());for(int i=0;i<hz*10;++i)hp-=t.Step(1.f/hz);assert(std::abs(hp-96.4f)<.02f);t.Bandage();assert(t.Step(1)==0);t.Splint();assert(t.CanSprint());t.Hit(45,WoundZone::Arm);assert(!t.CanShoot());t.Splint();assert(t.CanShoot());assert(t.Valid());BowDraw bow;bow.Begin(true);for(int i=0;i<hz;++i)bow.Step(1.f/hz);assert(std::abs(bow.Release()-1/1.1f)<.001f);assert(bow.Release()==0);bow.Begin(true);bow.Step(.1f);assert(bow.Release()==0);}
 Trauma invalid;invalid.leg=std::numeric_limits<float>::quiet_NaN();assert(!invalid.Valid());
 std::cout<<"FIELD_TEST_PASS transactional_loot_craft duplicate_cache save_validation bleeding_body_zones 30_60hz_bow\n";
}
