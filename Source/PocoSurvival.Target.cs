using UnrealBuildTool;
using System.Collections.Generic;
public class PocoSurvivalTarget : TargetRules
{
    public PocoSurvivalTarget(TargetInfo Target) : base(Target)
    {
        Type = TargetType.Game;
        ExtraModuleNames.Add("PocoSurvival");
    }
}
