#pragma once
#include <array>
#include <algorithm>
#include <cmath>
#include <cstdint>
namespace survival {
enum class Control : int { Interact,Attack,Sprint,Jump,Crouch,Reload,Throw,Weapon,Journal,Save,Load,Settings,Flashlight,Move,Count };
struct ControlPoint { float x,y; };
inline constexpr std::array<ControlPoint,14> LegacyControls={{{.91f,.80f},{.91f,.59f},{.75f,.80f},{.75f,.59f},{.75f,.39f},{.91f,.39f},{.91f,.23f},{.75f,.23f},{.55f,.08f},{.75f,.08f},{.91f,.08f},{.39f,.08f},{.55f,.23f},{.13f,.80f}}};
// Keep the centre and upper-right view clear. Save/load live inside the backpack.
inline constexpr std::array<ControlPoint,14> DefaultControls={{{.93f,.82f},{.91f,.59f},{.25f,.81f},{.77f,.72f},{.83f,.87f},{.94f,.40f},{.83f,.40f},{.82f,.56f},{.89f,.075f},{.75f,.075f},{.68f,.075f},{.96f,.075f},{.82f,.075f},{.12f,.79f}}};
inline float ControlRadius(Control id) {
 return id==Control::Move?.095f:id==Control::Interact?.060f:id==Control::Attack?.058f:
        (id==Control::Journal||id==Control::Save||id==Control::Load||id==Control::Settings||id==Control::Flashlight)?.030f:.043f;
}
inline bool ControlVisible(Control id,bool journal,bool editing,bool cinematic) {
 if(editing)return true;
 if(cinematic)return id==Control::Interact;
 if(journal)return id==Control::Journal||id==Control::Save||id==Control::Load||id==Control::Settings;
 return id!=Control::Save&&id!=Control::Load&&id!=Control::Move;
}
inline ControlPoint ClampControl(ControlPoint p,float radius,float aspect) {
 if(!std::isfinite(p.x)||!std::isfinite(p.y))p={.5f,.5f};
 aspect=std::isfinite(aspect)?std::clamp(aspect,1.0f,3.0f):1.8f;
 radius=std::isfinite(radius)?std::clamp(radius,.025f,.15f):.052f;
 return {std::clamp(p.x,radius/aspect+.01f,1-radius/aspect-.01f),std::clamp(p.y,radius+.01f,1-radius-.01f)};
}
inline bool ControlHit(ControlPoint p,ControlPoint center,float radius,float aspect) {
 if(!std::isfinite(p.x)||!std::isfinite(p.y)||!std::isfinite(radius)||radius<=0||!std::isfinite(aspect)||aspect<=0)return false;
 const float dx=(p.x-center.x)*aspect,dy=p.y-center.y;return dx*dx+dy*dy<=radius*radius;
}
struct Climate { float daylight=0,rain=0,fog=0,cloud=0; };
class WorldClock {
public:
 double seconds=17.0*3600;
 std::uint32_t seed=731;
 bool Restore(double value,std::uint32_t weatherSeed) {
  if(!std::isfinite(value)||value<0||value>315360000)return false;
  seconds=value;seed=weatherSeed;return true;
 }
 void Step(double realSeconds,bool paused) {
  if(paused||!std::isfinite(realSeconds)||realSeconds<=0)return;
  seconds=std::min(315360000.0,seconds+std::min(realSeconds,1.0)*24.0); // one real hour per full game day
 }
 float Hour() const { return static_cast<float>(std::fmod(seconds,86400.0)/3600.0); }
 static float Weather(std::uint32_t period,std::uint32_t weatherSeed) {
  if(period<5)return period%2 ? .25f:0; // authored dry arrival, later deterministic variability
  std::uint32_t x=period*747796405u+weatherSeed*2891336453u;x=(x^(x>>16))*2246822519u;x^=x>>13;
  const auto n=x%100;return n<40?0:n<70?.3f:n<94?.7f:1.0f;
 }
 Climate Sample() const {
  constexpr double periodSeconds=14400;const auto period=static_cast<std::uint32_t>(seconds/periodSeconds);
  const float fade=static_cast<float>(std::clamp(std::fmod(seconds,periodSeconds)/900.0,0.0,1.0));
  const float previous=Weather(period?period-1:0,seed),current=Weather(period,seed);
  const float cloud=previous+(current-previous)*fade;
  const float daylight=std::max(0.0f,std::sin((Hour()-6)*3.14159265358979323846f/12));
  return {daylight,std::clamp((cloud-.4f)/.6f,0.0f,1.0f),.08f+cloud*.48f,cloud};
 }
};
}
