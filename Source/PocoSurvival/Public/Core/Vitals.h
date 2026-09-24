#pragma once
#include <algorithm>
#include <cmath>
namespace survival {
class Vitals {
public:
    float health=100.0f, stamina=100.0f;
    float recoveryDelay=0.0f;
    bool exhausted=false;
    bool Alive() const { return health>0.0f; }
    bool CanSprint() const { return Alive() && !exhausted && stamina>0.0f; }
    bool Spend(float amount) {
        if (!Alive() || !std::isfinite(amount) || amount<0 || stamina<amount) return false;
        stamina-=amount; recoveryDelay=1.4f;
        if (stamina<=0.0f) exhausted=true;
        return true;
    }
    void Step(float seconds,bool sprinting) {
        if (!Alive() || !std::isfinite(seconds) || seconds<=0) return;
        seconds=std::min(seconds,1.0f);
        if (sprinting && CanSprint()) {
            stamina=std::max(0.0f,stamina-20.0f*seconds); recoveryDelay=1.4f;
            if (stamina<=0) exhausted=true;
        } else {
            const float eligible=std::max(0.0f,seconds-recoveryDelay);
            recoveryDelay=std::max(0.0f,recoveryDelay-seconds);
            stamina=std::min(100.0f,stamina+16.0f*eligible);
            if (stamina>=30.0f) exhausted=false;
        }
    }
    float Damage(float amount) {
        if (!std::isfinite(amount) || amount<=0 || !Alive()) return 0;
        const float actual=std::min(health,amount); health-=actual; return actual;
    }
    bool Restore(float h,float s) {
        if (!std::isfinite(h) || !std::isfinite(s) || h<0 || h>100 || s<0 || s>100) return false;
        health=h;stamina=s;recoveryDelay=0;exhausted=s<30;return true;
    }
};
}
