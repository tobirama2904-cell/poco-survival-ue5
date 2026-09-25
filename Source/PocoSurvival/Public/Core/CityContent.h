#pragma once
#include "Core/SurvivalCore.h"
namespace survival {
struct StorySite {
    std::string id,district,title,kind,speaker;
    float x,y,z;
    bool optional;
    std::vector<std::string> lines;
};
World MakeCityCampaign();
const std::vector<StorySite>& CitySites();
const StorySite* FindCitySite(const std::string& id);
}
