#pragma once
#include <string>
namespace survival {
inline bool IsRightHandBone(const std::string& name){
 std::string s;for(unsigned char c:name){if(c>='A'&&c<='Z')c=static_cast<unsigned char>(c-'A'+'a');if((c>='a'&&c<='z')||(c>='0'&&c<='9'))s.push_back(static_cast<char>(c));}
 const auto ends=[&](const char* suffix){const std::string t(suffix);return s.size()>=t.size()&&s.compare(s.size()-t.size(),t.size(),t)==0;};
 return s=="handr"||ends("bip01rhand")||ends("righthand");
}
}
