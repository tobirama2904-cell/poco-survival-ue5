#pragma once
#include <cmath>
namespace survival {
struct SceneryLODPolicy {
 float nearRange=9000,middleRange=18000,endRange=47000,hysteresis=600;
 bool Valid()const{return std::isfinite(nearRange)&&std::isfinite(middleRange)&&std::isfinite(endRange)&&std::isfinite(hysteresis)&&nearRange>0&&middleRange>nearRange&&endRange>middleRange&&hysteresis>=0&&hysteresis<nearRange*.25f;}
 int Choose(float distance,int current=-1)const{
  if(!Valid()||!std::isfinite(distance)||distance<0)return 3;
  if(current==0&&distance<nearRange+hysteresis)return 0;
  if(current==1&&distance>=nearRange-hysteresis&&distance<middleRange+hysteresis)return 1;
  if(current==2&&distance>=middleRange-hysteresis&&distance<endRange+hysteresis)return 2;
  if(current==3&&distance>=endRange-hysteresis)return 3;
  return distance<nearRange?0:distance<middleRange?1:distance<endRange?2:3;
 }
};
}
