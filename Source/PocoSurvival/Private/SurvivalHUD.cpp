#include "SurvivalHUD.h"
#include "SurvivalWorldDirector.h"
#include "Core/AmericanStory.h"
#include "SurvivalControlSettings.h"
#include "GameFramework/PlayerController.h"
#include "SurvivalGameInstance.h"
#include "Core/CityContent.h"
#include "Engine/Texture2D.h"
#include "EngineUtils.h"
#include "SurvivalCharacter.h"
#include "SurvivalCompanion.h"
#include "SurvivalInteraction.h"
#include "Engine/Canvas.h"
#include "Engine/Engine.h"
namespace {
void Ring(AHUD* H,float X,float Y,float R,FLinearColor Color,float Width=1.4f)
{
 for(int32 I=0;I<36;++I){const float A=I*2*PI/36,B=(I+1)*2*PI/36;H->DrawLine(X+FMath::Cos(A)*R,Y+FMath::Sin(A)*R,X+FMath::Cos(B)*R,Y+FMath::Sin(B)*R,Color,Width);}
}
void Glyph(AHUD* H,survival::Control Id,float X,float Y,float R,FLinearColor Color)
{
 auto L=[&](float A,float B,float C,float D){H->DrawLine(X+A*R,Y+B*R,X+C*R,Y+D*R,FLinearColor(0,0,0,.55),3);H->DrawLine(X+A*R,Y+B*R,X+C*R,Y+D*R,Color,1.6f);};
 using survival::Control;
 if(Id==Control::Interact){L(-.45,.3,-.45,-.25);L(-.45,-.25,-.2,-.1);L(-.2,-.1,-.2,-.65);L(-.2,-.65,.05,-.65);L(.05,-.65,.05,-.08);L(.05,-.08,.5,-.08);L(.5,-.08,.4,.6);L(.4,.6,-.2,.6);L(-.2,.6,-.45,.3);}
 else if(Id==Control::Attack){Ring(H,X,Y,R*.45f,Color);L(-.8,0,-.25,0);L(.25,0,.8,0);L(0,-.8,0,-.25);L(0,.25,0,.8);}
 else if(Id==Control::Jump||Id==Control::Load||Id==Control::Save){const float Sign=Id==Control::Save?1:-1;L(0,-.55*Sign,0,.5*Sign);L(-.4,.1*Sign,0,.5*Sign);L(.4,.1*Sign,0,.5*Sign);L(-.6,.75,.6,.75);}
 else if(Id==Control::Crouch||Id==Control::Sprint){Ring(H,X+R*.08f,Y-R*.55f,R*.18f,Color);L(0,-.27,-.2,.18);L(-.2,.18,.35,.28);L(.35,.28,.6,.65);L(-.2,.18,-.55,.62);L(-.05,-.18,.4,-.04);L(.4,-.04,.55,-.26);if(Id==Control::Sprint){L(-.7,-.35,-.3,-.35);L(-.8,-.05,-.45,-.05);}}
 else if(Id==Control::Journal){L(-.65,-.65,-.65,.65);L(-.65,-.65,.55,-.65);L(.55,-.65,.55,.65);L(.55,.65,-.65,.65);L(-.4,-.65,-.4,.65);L(-.18,-.3,.3,-.3);L(-.18,.05,.3,.05);}
 else if(Id==Control::Settings){Ring(H,X,Y,R*.43f,Color);Ring(H,X,Y,R*.12f,Color);for(int32 I=0;I<8;++I){const float A=I*PI/4;L(FMath::Cos(A)*.43f,FMath::Sin(A)*.43f,FMath::Cos(A)*.72f,FMath::Sin(A)*.72f);}}
 else if(Id==Control::Flashlight){L(-.5,.5,.0,.0);L(-.5,.5,-.2,.75);L(-.2,.75,.3,.2);L(0,0,.3,.2);L(0,0,.15,-.3);L(.15,-.3,.6,.1);L(.6,.1,.3,.2);L(.4,-.5,.55,-.65);L(.7,-.25,.9,-.3);}
 else if(Id==Control::Throw){L(-.2,-.7,.2,-.7);L(-.2,-.7,-.2,-.3);L(.2,-.7,.2,-.3);L(-.2,-.3,-.45,-.05);L(.2,-.3,.45,-.05);L(-.45,-.05,-.45,.65);L(.45,-.05,.45,.65);L(-.45,.65,.45,.65);}
 else if(Id==Control::Reload){Ring(H,X,Y,R*.55f,Color);L(.35,-.55,.65,-.4);L(.65,-.4,.75,-.75);L(-.35,.55,-.65,.4);L(-.65,.4,-.75,.75);}
 else if(Id==Control::Weapon){L(-.65,-.4,.65,-.4);L(.65,-.4,.65,-.05);L(.65,-.05,-.05,-.05);L(-.05,-.05,-.2,.55);L(-.2,.55,-.55,.55);L(-.55,.55,-.4,-.05);L(-.4,-.05,-.65,-.05);L(-.65,-.05,-.65,-.4);}
 else {L(-.65,0,.65,0);L(0,-.65,0,.65);}
}
}
void ASurvivalHUD::DrawHUD()
{
    Super::DrawHUD();if (!Canvas) return;
    auto* Player=Cast<ASurvivalCharacter>(GetOwningPawn());if (!Player) return;
    const float W=Canvas->ClipX,H=Canvas->ClipY,S=H/720.0f;
    const bool Cinema=Player->IsCinematicLocked();
    if(!Cinema){
    DrawText(TEXT("НИЗКАЯ ВОДА"),FColor(225,227,216),28*S,22*S,GEngine->GetSmallFont(),1.15f*S);
    if(auto* G=Cast<USurvivalGameInstance>(GetGameInstance()))DrawText(FString::Printf(TEXT("%02d:%02d  •  %s"),FMath::FloorToInt(G->WorldHour()),FMath::FloorToInt(FMath::Frac(G->WorldHour())*60),*ASurvivalWorldDirector::Chapter(G)),FColor(167,179,184),28*S,44*S,GEngine->GetSmallFont(),S);
    const float BarX=28*S,BarY=H-43*S;
    DrawRect(FLinearColor(0.03f,0.04f,0.05f,0.85f),BarX-8*S,BarY-10*S,174*S,38*S);
    DrawRect(FLinearColor(0.12f,0.15f,0.15f,1),BarX,BarY,158*S,5*S);
    DrawRect(FLinearColor(0.63f,0.82f,0.61f,1),BarX,BarY,158*S*Player->GetHealth()/100,5*S);
    DrawRect(FLinearColor(0.12f,0.15f,0.15f,1),BarX,BarY+12*S,158*S,3*S);
    DrawRect(FLinearColor(0.88f,0.73f,0.40f,1),BarX,BarY+12*S,158*S*Player->GetStamina()/100,3*S);
    DrawText(Player->StatusMessage,FColor::White,W*0.30f,H-55*S,GEngine->GetSmallFont(),S);
    if(Player->bBowEquipped||Player->CombatState().pistol){
    DrawLine(W/2-4*S,H/2,W/2+4*S,H/2,FLinearColor(.9,.9,.85,.7),1);
    DrawLine(W/2,H/2-4*S,W/2,H/2+4*S,FLinearColor(.9,.9,.85,.7),1);}
    if (Player->GetFocusedInteraction()) DrawText(TEXT("E / ДЕЙСТВИЕ"),FColor(233,197,128),W/2-50*S,H/2+24*S,GEngine->GetSmallFont(),S);
    if(auto* G=Cast<USurvivalGameInstance>(GetGameInstance()))if(Player->bBowEquipped)DrawText(FString::Printf(TEXT("ЛУК • %d стрел"),G->FieldInventory.Get(survival::Supply::Arrows)),FColor(229,206,147),W*.30f,H-116*S,GEngine->GetSmallFont(),S);
    if(Player->Wounds().bleeding>0)DrawText(TEXT("КРОВОТЕЧЕНИЕ • H / рюкзак"),FColor(238,117,98),W*.35f,H*.17f,GEngine->GetSmallFont(),S);
    }
    auto* Controls=USurvivalControlSettings::Get();
    for(int32 I=0;I<static_cast<int32>(survival::Control::Count);++I) {
        const auto Id=static_cast<survival::Control>(I);
        if(!survival::ControlVisible(Id,Player->bJournalOpen,Player->bEditingControls,Cinema))continue;
        const auto P=Controls->Position(Id,W/H);const float R=Controls->Radius(Id)*H;
        const bool Context=Id==survival::Control::Interact&&Player->GetFocusedInteraction();
        const FLinearColor Ink=Context?FLinearColor(.96,.77,.40,.95):FLinearColor(.91,.94,.90,Controls->Opacity+.15f);
        Ring(this,P.X*W,P.Y*H,R,FLinearColor(0,0,0,.30),3.5f*S);
        Ring(this,P.X*W,P.Y*H,R,Ink,1.3f*S);
        Glyph(this,Id,P.X*W,P.Y*H,R*.65f,Ink);
        if(Player->bEditingControls||Context||Id==survival::Control::Save||Id==survival::Control::Load)
            DrawText(USurvivalControlSettings::Label(Id),FColor(232,224,200),P.X*W-R,P.Y*H+R+3*S,GEngine->GetSmallFont(),.9f*S);
    }
    if(!Cinema&&!Player->bJournalOpen)DrawText(FString::Printf(TEXT("%s  %d / %d"),Player->IsReloading()?TEXT("Перезарядка"):Player->bBowEquipped?TEXT("Лук"):Player->CombatState().pistol?TEXT("Пистолет"):TEXT("Ближний бой"),Player->CombatState().loaded,FMath::Max(0,Player->EarnedRounds()-Player->CombatState().spent-Player->CombatState().loaded)),FColor(223,219,197),W*.43f,H-36*S,GEngine->GetSmallFont(),S);
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
        const auto& MainScenes=survival::FilmScenes();const bool MainActive=Game->FilmProgress>=0&&Game->FilmProgress<static_cast<int32>(MainScenes.size());
        auto Objectives=Game->GetObjectives();TArray<FSurvivalObjectiveView> Available;
        for (const auto& O:Objectives) { if (O.bAvailable) Available.Add(O); }
        auto Position=[&](FName Id) {
            for (TActorIterator<ASurvivalInteraction> It(GetWorld());It;++It) if (It->ActionId==Id) return It->GetActorLocation();
            const auto* Site=survival::FindCitySite(TCHAR_TO_UTF8(*Id.ToString()));
            return Site?FVector(Site->x*100,Site->y*100,Site->z*100):Player->GetActorLocation();
        };
        if(!MainActive)Available.Sort([&](const auto& A,const auto& B) {
            const auto* SA=survival::FindCitySite(TCHAR_TO_UTF8(*A.Id.ToString()));const auto* SB=survival::FindCitySite(TCHAR_TO_UTF8(*B.Id.ToString()));
            if (SA && SB && SA->optional!=SB->optional) return !SA->optional;
            return FVector::DistSquared(Position(A.Id),Player->GetActorLocation())<FVector::DistSquared(Position(B.Id),Player->GetActorLocation());
        });
        if (!Player->bStoryActive && !Player->bJournalOpen && (MainActive||Available.Num())) {
            FVector Destination=MainActive?Player->GetActorLocation():Position(Available[0].Id);if(MainActive){const auto& Scene=MainScenes[Game->FilmProgress];Destination=FVector(Scene.x*100,Scene.y*100,Scene.z*100+100);}
            const FVector Delta=Destination-Player->GetActorLocation();
            DrawRect(FLinearColor(.02,.035,.04,.38),20*S,80*S,400*S,70*S);
            Wrap(ASurvivalWorldDirector::Intention(Game),34*S,94*S,360*S,S,FColor(230,210,156));
            DrawText(FString::Printf(TEXT("%.0f м  ·  Подробности в рюкзаке"),Delta.Size2D()/100),FColor(176,194,192),34*S,135*S,GEngine->GetSmallFont(),S);
            FVector2D Screen;if (GetOwningPlayerController() && GetOwningPlayerController()->ProjectWorldLocationToScreen(Destination+FVector(0,0,150),Screen)) {
                if (Screen.X>0 && Screen.X<W && Screen.Y>70*S && Screen.Y<H-100*S) DrawText(TEXT("◇"),FColor(255,208,109),Screen.X,Screen.Y,GEngine->GetSmallFont(),1.5f*S);
            }
        }
        if (auto* Focus=Player->GetFocusedInteraction()) {
            const FString Id=Focus->ActionId.ToString();if(Id.StartsWith(TEXT("__"))){const TCHAR* Label=Id.StartsWith(TEXT("__cache_"))?TEXT("Обыскать контейнер"):Id.StartsWith(TEXT("__door_"))?TEXT("Открыть / закрыть дверь"):Id==TEXT("__gate_open")?TEXT("Открыть канал: затопить нижний берег, открыть тоннель"):TEXT("Удержать шлюз: сохранить дома, отдать запасы переправы");if(Id.StartsWith(TEXT("__main_"))){const int32 I=FCString::Atoi(*Id.Mid(7));const TCHAR* Ru[]={TEXT("Восстановить приёмник: дерево + деталь"),TEXT("Забрать комплект для Рут"),TEXT("Помочь Рут"),TEXT("Освободить фиксатор"),TEXT("Включить свет у убежища"),TEXT("Забрать запасной комплект приёмника")};const TCHAR* En[]={TEXT("Repair receiver: wood + scrap"),TEXT("Take Ruth's medical pack"),TEXT("Help Ruth"),TEXT("Release the latch"),TEXT("Switch on the shelter light"),TEXT("Take receiver repair kit")};if(I>=0&&I<6)Wrap(Controls->bEnglishStory?En[I]:Ru[I],W*.28f,H*.53f,W*.43f,S,FColor(240,220,178));}else if(Id.StartsWith(TEXT("__county_"))){TArray<FString> Parts;Id.Mid(9).ParseIntoArray(Parts,TEXT("_"));if(Parts.Num()==2){const int32 A=FCString::Atoi(*Parts[0]),B=FCString::Atoi(*Parts[1]);if(A>=0&&A<survival::CountyState::Count&&B>=0&&B<4){const auto& Arc=survival::CountyArcs()[A];const FString Prompt=B==0?TEXT("Прочитать запись"):B==1?TEXT("Восстановить: дерево + деталь"):UTF8_TO_TCHAR((Controls->bEnglishStory?Arc.choicesEn[B-2]:Arc.choices[B-2]).c_str());Wrap(Prompt,W*.28f,H*.53f,W*.43f,S,FColor(240,220,178));}}}else Wrap(Label,W*.28f,H*.53f,W*.43f,S,FColor(240,220,178));}
            for (const auto& O:Objectives) if (O.Id==Focus->ActionId && !Player->bStoryActive) {
                Wrap(O.Title.ToString()+(O.bCompleted?TEXT(" — завершено"):O.bAvailable?TEXT(" — E / Действие"):TEXT(" — пока недоступно")),W*.30f,H*.60f,W*.36f,S,FColor(240,220,178));break;
            }
        }
        if (Player->bJournalOpen) {
            DrawRect(FLinearColor(.025,.045,.05,.97),W*.08f,H*.17f,W*.84f,H*.63f);
            const auto& K=Game->FieldInventory;using survival::Supply;
            DrawRect(FLinearColor(.18,.24,.23,1),W*.65f,H*.18f,W*.23f,H*.06f);
            DrawText(Player->bCompanionPanel?(Controls->bEnglishStory?TEXT("Backpack"):TEXT("Рюкзак")):(Controls->bEnglishStory?TEXT("Companion"):TEXT("Напарник")),FColor::White,W*.67f,H*.195f,GEngine->GetSmallFont(),S);
            Wrap(ASurvivalWorldDirector::Intention(Game),W*.12f,H*.247f,W*.74f,.8f*S,FColor(185,203,195));
            DrawText(TEXT("РЮКЗАК • ДЭНИЕЛ РИД"),FColor(238,217,175),W*.11f,H*.20f,GEngine->GetSmallFont(),1.25f*S);
            if(Player->bCompanionPanel){
                bool Ready=false;for(TActorIterator<ASurvivalCompanion> Friend(GetWorld());Friend;++Friend)if(!Friend->RuthRole&&Friend->IsAvailable()){Ready=true;break;}
                DrawText(Ready?(Controls->bEnglishStory?TEXT("Mara Ellis"):TEXT("Мара Эллис")):(Controls->bEnglishStory?TEXT("Mara is not accompanying you yet"):TEXT("Мара ещё не сопровождает тебя")),FColor(223,207,179),W*.12f,H*.29f,GEngine->GetSmallFont(),S);
                DrawRect(FLinearColor(.15,.22,.20,.9),W*.12f,H*.36f,W*.76f,H*.09f);
                DrawText(Game->bMaraHolding?(Controls->bEnglishStory?TEXT("Come with me"):TEXT("Идём со мной")):(Controls->bEnglishStory?TEXT("Crouch and wait here"):TEXT("Пригнись и жди здесь")),Ready?FColor::White:FColor(130,130,130),W*.14f,H*.39f,GEngine->GetSmallFont(),S);
                DrawRect(FLinearColor(.15,.22,.20,.9),W*.12f,H*.49f,W*.76f,H*.09f);
                DrawText(Controls->bEnglishStory?TEXT("Help me bandage — 1 dressing"):TEXT("Помоги перевязаться — 1 бинт"),Ready?FColor::White:FColor(130,130,130),W*.14f,H*.52f,GEngine->GetSmallFont(),S);
                Wrap(Controls->bEnglishStory?TEXT("Needs a clear, safe place. Stand still near Mara. Interrupted help consumes no dressing. A waiting companion can be recalled here."):TEXT("Нужно безопасное место и свободный путь. Стой рядом с Марой. При прерывании бинт не тратится. Ожидающую Мару можно позвать отсюда."),W*.12f,H*.63f,W*.73f,.9f*S,FColor(183,200,191));
            }else{
            Wrap(FString::Printf(TEXT("Ткань %d   Спирт %d   Дерево %d   Детали %d"),K.Get(Supply::Cloth),K.Get(Supply::Alcohol),K.Get(Supply::Wood),K.Get(Supply::Scrap)),W*.12f,H*.29f,W*.74f,S,FColor::White);
            Wrap(FString::Printf(TEXT("Стрелы %d   Бинты %d   Шины %d   Груз %.1f кг"),K.Get(Supply::Arrows),K.Get(Supply::Bandage),K.Get(Supply::Splint),K.Weight()/1000.f+Game->GetCarriedWeightKg()),W*.12f,H*.36f,W*.74f,S,FColor::White);
            Wrap(FString::Printf(TEXT("Кровопотеря %.1f/с • Рука %.0f%% • Нога %.0f%%"),Player->Wounds().bleeding,Player->Wounds().arm*100,Player->Wounds().leg*100),W*.12f,H*.43f,W*.74f,S,FColor(224,153,139));
            if(Game->MainStory.spareRecovered&&!Game->MainStory.Has(1))DrawText(Controls->bEnglishStory?TEXT("Receiver repair kit • protected story item"):TEXT("Запасной комплект приёмника • сюжетный предмет"),FColor(223,207,179),W*.12f,H*.49f,GEngine->GetSmallFont(),.9f*S);
            if(Game->MainStory.Has(2)&&!Game->MainStory.Has(4))DrawText(Controls->bEnglishStory?TEXT("Ruth's medical pack • protected story item"):TEXT("Комплект для Рут • хранится отдельно от обычных бинтов"),FColor(223,207,179),W*.12f,H*.49f,GEngine->GetSmallFont(),.9f*S);
            const TCHAR* Recipes[]={TEXT("Перевязка: ткань + спирт"),TEXT("Шина: ткань + 2 дерева"),TEXT("3 стрелы: дерево + деталь"),TEXT("Использовать перевязку [H]"),TEXT("Наложить шину")};
            for(int32 I=0;I<5;++I){DrawRect(FLinearColor(.15,.18,.17,.8),W*.12f,H*(.53f+I*.05f),W*.76f,H*.044f);DrawText(Recipes[I],FColor(237,229,203),W*.14f,H*(.54f+I*.05f),GEngine->GetSmallFont(),S);}
            }
            DrawText(Controls->bEnglishStory?TEXT("Story subtitles: English — нажать для русского"):TEXT("Субтитры истории: русский — press for English"),FColor(223,207,179),W*.14f,H*.81f,GEngine->GetSmallFont(),S);

        }
    }
    if (Player->bStoryActive && !Player->IsBanterPaused() && !Player->bJournalOpen && Player->StoryLines.IsValidIndex(Player->StoryLine)) {
        if(!Player->IsCinematicLocked()) {
            DrawRect(FLinearColor(.015,.025,.03,.88),W*.28f,H*.68f,W*.40f,H*.20f);
            DrawText(Player->StorySpeaker,FColor(239,199,122),W*.295f,H*.69f,GEngine->GetSmallFont(),S);
            Wrap(Player->StoryLines[Player->StoryLine],W*.295f,H*.73f,W*.36f,S,FColor(235,237,231));
        } else {
        DrawRect(FLinearColor(0,0,0,1),0,0,W,H*.065f);
        DrawRect(FLinearColor(0,0,0,1),0,H*.935f,W,H*.065f);
        DrawRect(FLinearColor(.01,.018,.02,.65),W*.18f,H*.75f,W*.64f,H*.17f);
        DrawText(Player->StorySpeaker,FColor(239,209,156),W*.20f,H*.765f,GEngine->GetSmallFont(),S);
        Wrap(Player->StoryLines[Player->StoryLine],W*.20f,H*.807f,W*.60f,1.13f*S,FColor(240,239,233));
        }
    }
    if(Player->bJournalOpen)DrawText(TEXT("Персонажи: Microsoft Rocketbox / MIT · Окружение: Poly Haven / CC0"),FColor(150,164,161),W*.11f,H*.87f,GEngine->GetSmallFont(),.8f*S);
}
