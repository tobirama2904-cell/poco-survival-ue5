#pragma once
#include <string>
#include <vector>
namespace survival {
struct FilmScene {std::string id,title;float x,y,z;bool cinematic;int gate;std::vector<std::string> ru,en;std::string intentRu,intentEn,focus;unsigned requiredEvents=0;int escort=0;};
const std::vector<FilmScene>& FilmScenes();
}
