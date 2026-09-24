using UnrealBuildTool;
using System.Collections.Generic;
public class PocoSurvivalEditorTarget : TargetRules
{
    public PocoSurvivalEditorTarget(TargetInfo Target) : base(Target)
    {
        Type = TargetType.Editor;
        ExtraModuleNames.Add("PocoSurvival");
    }
}
