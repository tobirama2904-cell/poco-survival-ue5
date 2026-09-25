#pragma once
#include <string>
#include <vector>
namespace survival {
struct FilmScene {std::string id,title;float x,y,z;bool cinematic;int gate;std::vector<std::string> ru,en;};
const std::vector<FilmScene>& FilmScenes();
}
