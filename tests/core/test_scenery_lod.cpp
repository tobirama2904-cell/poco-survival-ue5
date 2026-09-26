#include "Core/SceneryLOD.h"
#include <cassert>
#include <limits>
#include <iostream>
using namespace survival;
int main(){SceneryLODPolicy p;assert(p.Valid());assert(p.Choose(0)==0);assert(p.Choose(10000)==1);assert(p.Choose(19000)==2);assert(p.Choose(50000)==3);
 assert(p.Choose(9100,0)==0);assert(p.Choose(9700,0)==1);assert(p.Choose(8800,1)==1);assert(p.Choose(8300,1)==0);assert(p.Choose(17900,2)==2);assert(p.Choose(17000,2)==1);assert(p.Choose(46800,3)==3);assert(p.Choose(46000,3)==2);
 int current=-1;for(int d=0;d<60000;++d){int next=p.Choose(d,current);assert(next>=0&&next<=3);assert(next>=current);current=next;}
 for(int d=60000;d>=0;--d){int next=p.Choose(d,current);assert(next>=0&&next<=3);assert(next<=current);current=next;}
 assert(p.Choose(std::numeric_limits<float>::quiet_NaN())==3);assert(p.Choose(-1)==3);p.endRange=100;assert(!p.Valid()&&p.Choose(0)==3);
 std::cout<<"SCENERY_LOD_PASS ranges hysteresis near_far_120k_steps invalid_inputs\n";
}
