#include "SurvivalHUD.h"
#include "SurvivalWorldDirector.h"
#include "SurvivalControlSettings.h"
#include "GameFramework/PlayerController.h"
#include "SurvivalGameInstance.h"
#include "Core/CityContent.h"
#include "Engine/Texture2D.h"
#include "EngineUtils.h"
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
    DrawText(TEXT("НУЛЕВАЯ ОТМЕТКА  /  НИЖНИЙ БЕРЕГ"),FColor(228,229,220),24*S,12*S,GEngine->GetSmallFont(),1.2f*S);
    if(auto* G=Cast<USurvivalGameInstance>(GetGameInstance()))DrawText(FString::Printf(TEXT("%02d:%02d  •  %s"),FMath::FloorToInt(G->WorldHour()),FMath::FloorToInt(FMath::Frac(G->WorldHour())*60),*ASurvivalWorldDirector::Chapter(G)),FColor(167,179,184),24*S,36*S,GEngine->GetSmallFont(),S);
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
    auto* Controls=USurvivalControlSettings::Get();
    for(int32 I=0;I<static_cast<int32>(survival::Control::Count);++I) {
        const auto Id=static_cast<survival::Control>(I);if(Id==survival::Control::Move&&!Player->bEditingControls)continue;
        const auto P=Controls->Position(Id,W/H);const float R=Controls->Radius(Id)*H;
        DrawRect(FLinearColor(.025f,.045f,.055f,Controls->Opacity),P.X*W-R,P.Y*H-R,R*2,R*2);
        const TCHAR* Label=Id==survival::Control::Attack&&Player->CombatState().pistol?TEXT("Выстрел"):USurvivalControlSettings::Label(Id);
        DrawText(Label,FColor(231,229,212),P.X*W-R+4*S,P.Y*H-9*S,GEngine->GetSmallFont(),.9f*S);
    }
    DrawText(FString::Printf(TEXT("%s  %d / %d  •  Бутылки %d"),Player->IsReloading()?TEXT("Перезарядка"):Player->CombatState().pistol?TEXT("Пистолет"):TEXT("Ближний бой"),Player->CombatState().loaded,Player->EarnedRounds()-Player->CombatState().spent-Player->CombatState().loaded,Player->EarnedBottles()-Player->CombatState().bottlesUsed),FColor(231,207,151),W*.30f,H-90*S,GEngine->GetSmallFont(),S);
    if(Player->bEditingControls) {
        DrawRect(FLinearColor(.015,.025,.03,.96),W*.28f,H*.27f,W*.39f,H*.44f);
        DrawText(TEXT("Перетаскивай кнопки • F10 / Готово"),FColor(240,211,159),W*.295f,H*.275f,GEngine->GetSmallFont(),S);
        const TArray<FString> Rows={FString::Printf(TEXT("Чувствительность %.1f      − / +"),Controls->Sensitivity),FString::Printf(TEXT("Размер кнопок %.2f       − / +"),Controls->ButtonScale),FString::Printf(TEXT("Прозрачность %.2f        − / +"),Controls->Opacity),Controls->bLeftHanded?TEXT("Зеркально: левша — изменить"):TEXT("Зеркально: правша — изменить"),FString::Printf(TEXT("Y: %s    |    Качество: %s"),Controls->bInvertY?TEXT("обр."):TEXT("прям."),Controls->bPerformanceMode?TEXT("скорость"):TEXT("баланс")),TEXT("Сбросить                 Готово")};
        for(int32 I=0;I<Rows.Num();++I){DrawRect(FLinearColor(.12,.16,.17,.7),W*.29f,H*(.31f+I*.06f),W*.36f,H*.052f);DrawText(Rows[I],FColor::White,W*.30f,H*(.323f+I*.06f),GEngine->GetSmallFont(),.9f*S);}return;
    }
    auto Wrap=[&](const FString& Text,float X,float Y,float Width,float Scale,FColor Color) {
        TArray<FString> Words;Text.ParseIntoArray(Words,TEXT(" "),true);FString Line;
        for (const auto& Word:Words) {
            const FString Trial=Line.IsEmpty()?Word:Line+TEXT(" ")+Word;float TW=0,TH=0;
            GetTextSize(Trial,TW,TH,GEngine->GetSmallFont(),Scale);
            if (TW>Width && !Line.IsEmpty()) { DrawText(Line,Color,X,Y,GEngine->GetSmallFont(),Scale);Y+=24*S;Line=Word; } else Line=Trial;
        }
        if (!Line.IsEmpty()) { DrawText(Line,Color,X,Y,GEngine->GetSmallFont(),Scale);Y+=24*S; }return Y;
    };
    if (auto* Game=Cast<USurvivalGameInstance>(GetGameInstance())) {
        auto Objectives=Game->GetObjectives();TArray<FSurvivalObjectiveView> Available;
        for (const auto& O:Objectives) { if (O.bAvailable) Available.Add(O); }
        auto Position=[&](FName Id) {
            for (TActorIterator<ASurvivalInteraction> It(GetWorld());It;++It) if (It->ActionId==Id) return It->GetActorLocation();
            const auto* Site=survival::FindCitySite(TCHAR_TO_UTF8(*Id.ToString()));
            return Site?FVector(Site->x*100,Site->y*100,Site->z*100):Player->GetActorLocation();
        };
        Available.Sort([&](const auto& A,const auto& B) {
            const auto* SA=survival::FindCitySite(TCHAR_TO_UTF8(*A.Id.ToString()));const auto* SB=survival::FindCitySite(TCHAR_TO_UTF8(*B.Id.ToString()));
            if (SA && SB && SA->optional!=SB->optional) return !SA->optional;
            return FVector::DistSquared(Position(A.Id),Player->GetActorLocation())<FVector::DistSquared(Position(B.Id),Player->GetActorLocation());
        });
        if (!Player->bStoryActive && !Player->bJournalOpen && Available.Num()) {
            const auto& O=Available[0];const FVector Delta=Position(O.Id)-Player->GetActorLocation();
            DrawRect(FLinearColor(.02,.035,.04,.8),20*S,85*S,440*S,76*S);
            Wrap(ASurvivalWorldDirector::Intention(Game),34*S,94*S,400*S,S,FColor(230,210,156));
            DrawText(FString::Printf(TEXT("Ближайшая подсказка: %.0f м • заметки доступны"),Delta.Size2D()/100),FColor(176,194,192),34*S,135*S,GEngine->GetSmallFont(),S);
            FVector2D Screen;if (GetOwningPlayerController() && GetOwningPlayerController()->ProjectWorldLocationToScreen(Position(O.Id)+FVector(0,0,150),Screen)) {
                if (Screen.X>0 && Screen.X<W && Screen.Y>70*S && Screen.Y<H-100*S) DrawText(TEXT("◇"),FColor(255,208,109),Screen.X,Screen.Y,GEngine->GetSmallFont(),1.5f*S);
            }
        }
        if (auto* Focus=Player->GetFocusedInteraction()) {
            for (const auto& O:Objectives) if (O.Id==Focus->ActionId && !Player->bStoryActive) {
                Wrap(O.Title.ToString()+(O.bCompleted?TEXT(" — завершено"):O.bAvailable?TEXT(" — E / Действие"):TEXT(" — Арсен ещё не знает, как это использовать")),W*.30f,H*.60f,W*.36f,S,FColor(240,220,178));break;
            }
        }
        if (Player->bJournalOpen) {
            DrawRect(FLinearColor(.025,.045,.05,.97),W*.08f,H*.17f,W*.84f,H*.63f);
            DrawText(TEXT("ЗАМЕТКИ АРСЕНА • куда можно пойти"),FColor(238,217,175),W*.11f,H*.20f,GEngine->GetSmallFont(),1.25f*S);
            float Y=H*.27f;int32 I=0;
            for (const auto& O:Available) { if (I++>=10) break;
                const auto* Site=survival::FindCitySite(TCHAR_TO_UTF8(*O.Id.ToString()));
                Y=Wrap(FString(Site && Site->optional?TEXT("+ "):TEXT("• "))+O.Title.ToString()+FString::Printf(TEXT("  [%.0f м]"),FVector::Dist2D(Position(O.Id),Player->GetActorLocation())/100),W*.11f,Y,W*.74f,S,FColor(215,223,217));
            }
            const FString Inventory=FString::Printf(TEXT("Груз %.1f / 24 кг • Аптечки: %d • Ткань: %d • Спирт: %d • Детали: %d"),Game->GetCarriedWeightKg(),Game->GetItemCount(TEXT("medkit")),Game->GetItemCount(TEXT("cloth")),Game->GetItemCount(TEXT("alcohol")),Game->GetItemCount(TEXT("scrap")));
            Wrap(Inventory,W*.11f,H*.73f,W*.75f,S,FColor(231,201,143));
        }
    }
    if (Player->bStoryActive && Player->StoryLines.IsValidIndex(Player->StoryLine)) {
        if(!Player->IsCinematicLocked()) {
            DrawRect(FLinearColor(.015,.025,.03,.88),W*.28f,H*.68f,W*.40f,H*.20f);
            DrawText(Player->StorySpeaker,FColor(239,199,122),W*.295f,H*.69f,GEngine->GetSmallFont(),S);
            Wrap(Player->StoryLines[Player->StoryLine],W*.295f,H*.73f,W*.36f,S,FColor(235,237,231));
        } else {
        DrawRect(FLinearColor(0,0,0,1),0,0,W,H*.09f);
        DrawRect(FLinearColor(.015,.025,.03,.96),W*.08f,H*.64f,W*.74f,H*.30f);
        float X=W*.11f;
        const int32 Face=Player->StorySpeaker==TEXT("Лейла")?0:Player->StorySpeaker==TEXT("Наргис")?1:Player->StorySpeaker==TEXT("Тимур")?2:-1;
        if (Face>=0) {
            if (!Portraits) Portraits=LoadObject<UTexture2D>(nullptr,TEXT("/Game/Story/portraits.portraits"));
            if (Portraits) { DrawTexture(Portraits,X,H*.675f,110*S,150*S,Face/3.0f,0,1.0f/3.0f,1);X+=130*S; }
        }
        DrawText(Player->StorySpeaker,FColor(239,199,122),X,H*.67f,GEngine->GetSmallFont(),1.2f*S);
        Wrap(Player->StoryLines[Player->StoryLine],X,H*.72f,W*.76f-X,1.15f*S,FColor(235,237,231));
        DrawText(FString::Printf(TEXT("%d / %d     E / Действие — дальше"),Player->StoryLine+1,Player->StoryLines.Num()),FColor(166,185,184),X,H*.89f,GEngine->GetSmallFont(),S);
        }
    }
    DrawText(TEXT("В разработке • персонажи: Microsoft / MIT"),FColor(125,140,141),20*S,H-17*S,GEngine->GetSmallFont(),.8f*S);
}
