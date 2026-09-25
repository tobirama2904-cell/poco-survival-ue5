#pragma once
#include <algorithm>
#include <cmath>
namespace survival {
struct CombatSnapshot { int loaded=0,spent=0,bottlesUsed=0; bool pistol=false; };
class Combat {
public:
    static constexpr int Magazine=8;
    CombatSnapshot state;
    float cooldown=0,reloading=0;
    static bool Valid(const CombatSnapshot& s,int rounds,int bottles,bool ownsPistol) {
        return rounds>=0 && rounds<=1024 && bottles>=0 && bottles<=128 && s.loaded>=0 && s.loaded<=Magazine && s.spent>=0 && s.spent<=rounds && s.loaded<=rounds-s.spent && s.bottlesUsed>=0 && s.bottlesUsed<=bottles && (!s.pistol || ownsPistol);
    }
    int Reserve(int rounds) const { return std::max(0,rounds-state.spent-state.loaded); }
    bool Restore(const CombatSnapshot& s,int rounds,int bottles,bool ownsPistol) {
        if (!Valid(s,rounds,bottles,ownsPistol)) return false;
        state=s;cooldown=0;reloading=0;return true;
    }
    bool Reload(int rounds) {
        if (!state.pistol || reloading>0 || state.loaded==Magazine || Reserve(rounds)==0) return false;
        reloading=1.6f;return true;
    }
    void Step(float seconds,int rounds) {
        if (!std::isfinite(seconds) || seconds<=0) return;
        seconds=std::min(seconds,1.0f);cooldown=std::max(0.0f,cooldown-seconds);
        if (reloading>0) { reloading=std::max(0.0f,reloading-seconds);if (reloading==0) state.loaded+=std::min(Magazine-state.loaded,Reserve(rounds)); }
    }
    bool Fire() {
        if (!state.pistol || reloading>0 || cooldown>0 || state.loaded<=0) return false;
        --state.loaded;++state.spent;cooldown=.32f;return true;
    }
    bool Throw(int bottles) { if (state.bottlesUsed>=bottles || bottles<0 || bottles>128) return false;++state.bottlesUsed;return true; }
    void Select(bool pistol) { state.pistol=pistol;reloading=0; }
};
}
