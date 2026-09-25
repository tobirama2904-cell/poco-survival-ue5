#include "Core/Experience.h"
#include <cassert>
#include <limits>
#include <iostream>
using namespace survival;
int main(){
 for(float aspect:{1.4f,16.f/9,20.f/9,2.8f})for(auto p:DefaultControls){auto q=ClampControl(p,.06f,aspect);assert(ControlHit(q,q,.06f,aspect));assert(!ControlHit({q.x+.13f,q.y},q,.06f,aspect));assert(q.y>=.07f && q.y<=.93f);}
 auto q=ClampControl({-100,100},.08f,2);assert(q.x>=.049f&&q.y<=.911f);
 auto nan=std::numeric_limits<float>::quiet_NaN();q=ClampControl({nan,nan},nan,nan);assert(std::isfinite(q.x));assert(!ControlHit({nan,0},{0,0},.1f,2));
 WorldClock a,b;assert(a.Restore(17*3600,731));assert(b.Restore(a.seconds,731));
 for(int i=0;i<30*120;++i)a.Step(1.0/30,false);
 for(int i=0;i<60*120;++i)b.Step(1.0/60,false);
 assert(std::abs(a.seconds-b.seconds)<.001);const double before=a.seconds;a.Step(100,true);assert(a.seconds==before);assert(!a.Restore(-1,0));assert(!a.Restore(std::numeric_limits<double>::infinity(),0));
 assert(a.Restore(12*3600,731));assert(a.Sample().daylight>.99f);assert(a.Restore(0,731));assert(a.Sample().daylight==0);
 for(int day=0;day<90;++day)for(int hour=0;hour<24;++hour){a.Restore(day*86400.0+hour*3600,731);auto c=a.Sample();assert(c.rain>=0&&c.rain<=1&&c.cloud>=0&&c.cloud<=1);b.Restore(a.seconds,a.seed);assert(c.rain==b.Sample().rain);}
 a.Restore(10*14400-.01,731);float left=a.Sample().cloud;a.Step(.001,false);assert(std::abs(left-a.Sample().cloud)<.001);
 std::cout<<"EXPERIENCE_TEST_PASS touch_hitboxes aspect_clamping invalid_values 30_60hz persistent_weather smooth_transitions\n";
}
