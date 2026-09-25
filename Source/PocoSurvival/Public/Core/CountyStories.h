#pragma once
#include "Core/FieldSurvival.h"
#include <array>
#include <string>
#include <vector>
namespace survival {
struct CountyBeat {std::vector<std::string> ru,en;};
struct CountyArc {std::string id,title,titleEn,poi;std::array<std::string,2> choices,choicesEn;std::array<CountyBeat,4> beats;};
const std::vector<CountyArc>& CountyArcs();
enum class CountyResult { Advanced, Replay, Invalid, WrongOrder, Resources };
struct CountyState {
 static constexpr int Count=6;
 std::array<int,Count> stages{}; // 0 unseen, 1 read, 2 repaired, 3 public, 4 private
 bool Valid()const {for(int v:stages)if(v<0||v>4)return false;return true;}
 int Complete()const {int n=0;for(int v:stages)if(v>=3)++n;return n;}
 CountyResult Apply(int arc,int action,FieldKit& kit) {
  if(!Valid()||!kit.Valid()||arc<0||arc>=Count||action<0||action>3)return CountyResult::Invalid;
  int& state=stages[arc];
  if(action==0){if(state>0)return CountyResult::Replay;state=1;return CountyResult::Advanced;}
  if(action==1){
   if(state==0)return CountyResult::WrongOrder;
   if(state>=2)return CountyResult::Replay;
   auto candidate=kit;if(!candidate.Spend(Supply::Scrap)||!candidate.Spend(Supply::Wood))return CountyResult::Resources;
   kit=candidate;state=2;return CountyResult::Advanced;
  }
  if(state==action+1)return CountyResult::Replay;
  if(state!=2)return CountyResult::WrongOrder;
  auto candidate=kit;if(action==3&&!candidate.Add(Supply::Bandage,1))return CountyResult::Resources;
  kit=candidate;state=action+1;return CountyResult::Advanced;
 }
};
}
