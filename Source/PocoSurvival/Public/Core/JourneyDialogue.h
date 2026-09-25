#pragma once
#include <vector>
#include <string>
#include <cstdint>
namespace survival {
enum class JourneyTrigger { Walk,Rain,Rest,Night,Hurt,Water };
struct JourneyScene {std::string id;int first,last;JourneyTrigger trigger;std::vector<std::string> ru,en;};
const std::vector<JourneyScene>& JourneyScenes();
struct JourneyContext {int scene=0;bool walking=false,rain=false,rest=false,night=false,hurt=false,water=false,quiet=false,companion=false;};
struct JourneyHistory {
 static constexpr int Count=12;
 std::uint32_t heard=0;
 bool Valid()const{return (heard>>Count)==0;}
 bool Finish(int id){if(id<0||id>=Count||!Valid())return false;const auto bit=1u<<id;if(heard&bit)return false;heard|=bit;return true;}
 int Pick(const JourneyContext& c)const {
  if(!Valid()||!c.quiet||!c.companion)return -1;
  const auto& scenes=JourneyScenes();
  if(c.hurt){for(int i=0;i<static_cast<int>(scenes.size());++i)if(scenes[i].trigger==JourneyTrigger::Hurt&&c.scene>=scenes[i].first&&c.scene<=scenes[i].last&&!(heard&(1u<<i)))return i;return -1;}
  for(int i=0;i<static_cast<int>(scenes.size());++i){
   const auto& s=scenes[i];if((heard&(1u<<i))||c.scene<s.first||c.scene>s.last)continue;
   const bool match=s.trigger==JourneyTrigger::Walk?c.walking:s.trigger==JourneyTrigger::Rain?c.rain:s.trigger==JourneyTrigger::Rest?c.rest:s.trigger==JourneyTrigger::Night?c.night:s.trigger==JourneyTrigger::Hurt?c.hurt:c.water&&c.rest;
   if(match)return i;
  }
  return -1;
 }
};
}
