#pragma once
#include <cstdint>
namespace survival {
// Earlier builds defaulted FormatVersion to the current version. UE omits
// default-valued tagged properties. Recover a compatible legacy layout, not a
// fictitious exact producer revision; new writes always serialize explicit 8.
inline int ResolveSaveFormat(int taggedVersion,int fieldCount,std::int64_t generation){
 if(taggedVersion!=0)return taggedVersion;
 if(fieldCount==9)return 8;
 if(fieldCount!=0)return 0;
 return generation>0?5:1;
}
}
