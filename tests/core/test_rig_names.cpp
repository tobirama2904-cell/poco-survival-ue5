#include "Core/RigNames.h"
#include <cassert>
#include <iostream>
int main(){
 for(const char* s:{"Bip01 R Hand","Bip01_R_Hand","Bip01-R-Hand","Arsen:Bip01 R Hand","hand_r","mixamorig:RightHand"})assert(survival::IsRightHandBone(s));
 for(const char* s:{"Bip01 L Hand","Bip01 R Hand Finger0","RightHandIndex1","head","hand_l",""})assert(!survival::IsRightHandBone(s));
 std::cout<<"RIG_NAME_TEST_PASS namespaced_right_hand_no_fingers_or_left_hand\n";
}
