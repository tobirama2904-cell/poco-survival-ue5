#include "Core/Combat.h"
#include <cassert>
#include <iostream>
#include <limits>
using namespace survival;
int main(){
 for(int hz:{30,60}){
  Combat c;assert(!c.Fire());assert(!c.Reload(24));c.Select(true);assert(c.Reload(24));assert(!c.Fire());
  for(int i=0;i<2*hz;++i)c.Step(1.0f/hz,24);
  assert(c.state.loaded==8 && c.Reserve(24)==16);
  for(int i=0;i<8;++i){assert(c.Fire());assert(!c.Fire());c.Step(.4f,24);}
  assert(!c.Fire() && c.state.spent==8 && c.state.loaded==0);
  assert(c.Reload(24));c.Select(false);c.Step(2,24);assert(c.state.loaded==0); // cancelling doesn't conjure ammunition
  c.Select(true);assert(c.Reload(24));c.Step(1,24);c.Step(1,24);assert(c.state.loaded==8);
  for(int i=0;i<3;++i) { assert(c.Throw(3)); } assert(!c.Throw(3));
  Combat restored;assert(restored.Restore(c.state,24,3,true));assert(restored.state.spent==8 && restored.state.bottlesUsed==3);
  auto invalid=c.state;invalid.loaded=9;assert(!restored.Restore(invalid,24,3,true));invalid=c.state;invalid.spent=25;assert(!restored.Restore(invalid,24,3,true));assert(!restored.Restore(c.state,24,2,true));assert(!restored.Restore(c.state,24,3,false));
  c.Step(std::numeric_limits<float>::quiet_NaN(),24);assert(c.state.loaded==8);
 }
 std::cout<<"COMBAT_TEST_PASS 30_60hz reload_cancel finite_ammo finite_distractions save_validation\n";
}
