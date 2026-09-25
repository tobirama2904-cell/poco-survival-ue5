#pragma once
#include "Core/FieldSurvival.h"
#include <cstdint>
namespace survival {
enum class CampaignResult { Advanced,Replay,Locked,Resources,Invalid };
struct CampaignState {
 std::uint32_t events=0;bool spareRecovered=false;
 bool Valid()const{return events==0||events==1||events==3||events==7||events==15||events==31;}
 bool Has(unsigned mask)const{return (events&mask)==mask;}
 CampaignResult Apply(int action,int scene,FieldKit& kit){
  if(!Valid()||!kit.Valid()||action<0||action>=6)return CampaignResult::Invalid;
  if(action==5){if(scene<20)return CampaignResult::Locked;if(spareRecovered)return CampaignResult::Replay;spareRecovered=true;return CampaignResult::Advanced;}
  const unsigned bit=1u<<action;if(events&bit)return CampaignResult::Replay;
  constexpr int firstScene[]={20,22,24,26,29};
  if(scene<firstScene[action]||!Has(bit-1))return CampaignResult::Locked;
  auto candidate=kit;bool ok=true;
  if(action==0&&!spareRecovered)ok=candidate.Spend(Supply::Scrap)&&candidate.Spend(Supply::Wood);
  // The medical pack is a protected quest item (bit 1 until bit 2),
  // not a spendable healing bandage: self-healing cannot soft-lock Ruth.
  if(!ok)return CampaignResult::Resources;
  kit=candidate;events|=bit;return CampaignResult::Advanced;
 }
};
}
