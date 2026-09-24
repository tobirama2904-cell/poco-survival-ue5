#include "Core/Vitals.h"
#include <cassert>
#include <limits>
#include <iostream>
int main() {
    using survival::Vitals;Vitals a;
    assert(a.Alive() && a.CanSprint());
    for(int i=0;i<5;i++)a.Step(1,true);
    assert(a.stamina==0 && a.exhausted && !a.CanSprint());
    a.Step(1,false);assert(a.stamina==0);
    a.Step(1,false);assert(a.stamina>9 && a.stamina<10);
    for(int i=0;i<8;i++)a.Step(1,false);
    assert(a.stamina==100 && a.CanSprint());
    assert(!a.Spend(101) && !a.Spend(-1));
    assert(a.Spend(18) && a.stamina==82);
    assert(a.Damage(-10)==0 && a.Damage(std::numeric_limits<float>::infinity())==0);
    assert(a.Damage(25)==25 && a.health==75);
    assert(a.Damage(100)==75 && !a.Alive() && !a.Spend(1));
    assert(!a.Restore(101,50) && !a.Restore(100,-1));
    assert(!a.Restore(std::numeric_limits<float>::quiet_NaN(),100));
    assert(a.Restore(60,20) && a.Alive() && a.exhausted);
    a.Step(1,false);assert(a.stamina==36 && !a.exhausted);
    Vitals b,c;for(int i=0;i<60;i++) b.Step(1.0f/60,true);for(int i=0;i<30;i++) c.Step(1.0f/30,true);
    assert(std::abs(b.stamina-c.stamina)<0.001f);
    std::cout<<"VITALS_TEST_PASS exhaustion recovery melee_cost damage invalid_input 30_60hz\n";
}
