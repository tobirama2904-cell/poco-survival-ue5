#include "SurvivalHUD.h"
#include "SurvivalCharacter.h"
#include "SurvivalInteraction.h"
#include "Engine/Canvas.h"
#include "Engine/Engine.h"
void ASurvivalHUD::DrawHUD()
{
    Super::DrawHUD();if (!Canvas) return;
    auto* Player=Cast<ASurvivalCharacter>(GetOwningPawn());if (!Player) return;
    const float W=Canvas->ClipX,H=Canvas->ClipY,S=H/720.0f;
    DrawRect(FLinearColor(0.02f,0.03f,0.04f,0.75f),0,0,W,64*S);
    DrawText(TEXT("НУЛЕВАЯ ОТМЕТКА  /  ТЕХНИЧЕСКАЯ СЦЕНА"),FColor(228,229,220),24*S,12*S,GEngine->GetSmallFont(),1.2f*S);
    DrawText(TEXT("Манекен и интерфейс временные. Не готовая игра."),FColor(167,179,184),24*S,36*S,GEngine->GetSmallFont(),S);
    const float BarX=24*S,BarY=H-65*S;
    DrawRect(FLinearColor(0.03f,0.04f,0.05f,0.85f),BarX-8*S,BarY-10*S,256*S,57*S);
    DrawRect(FLinearColor(0.12f,0.15f,0.15f,1),BarX,BarY,230*S,10*S);
    DrawRect(FLinearColor(0.63f,0.82f,0.61f,1),BarX,BarY,230*S*Player->GetHealth()/100,10*S);
    DrawRect(FLinearColor(0.12f,0.15f,0.15f,1),BarX,BarY+20*S,230*S,6*S);
    DrawRect(FLinearColor(0.88f,0.73f,0.40f,1),BarX,BarY+20*S,230*S*Player->GetStamina()/100,6*S);
    DrawText(Player->StatusMessage,FColor::White,W*0.30f,H-55*S,GEngine->GetSmallFont(),S);
    DrawLine(W/2-5*S,H/2,W/2+5*S,H/2,FLinearColor::White,1);
    DrawLine(W/2,H/2-5*S,W/2,H/2+5*S,FLinearColor::White,1);
    if (Player->GetFocusedInteraction()) DrawText(TEXT("E / ДЕЙСТВИЕ"),FColor(233,197,128),W/2-50*S,H/2+24*S,GEngine->GetSmallFont(),S);
    auto Button=[&](const TCHAR* Label,float X,float Y){DrawRect(FLinearColor(0.04f,0.06f,0.08f,0.75f),W*X-44*S,H*Y-28*S,88*S,56*S);DrawText(Label,FColor::White,W*X-35*S,H*Y-9*S,GEngine->GetSmallFont(),S);};
    Button(TEXT("Действие"),0.91f,0.80f);Button(TEXT("Удар"),0.91f,0.59f);Button(TEXT("Бег"),0.75f,0.80f);Button(TEXT("Загрузить"),0.91f,0.08f);
    Button(TEXT("Прыжок"),0.75f,0.59f);Button(TEXT("Тише"),0.75f,0.39f);Button(TEXT("Сохранить"),0.75f,0.08f);
}
