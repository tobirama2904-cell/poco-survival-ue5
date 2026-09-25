#include "SurvivalCharacter.h"
#include "SurvivalArrow.h"
#include "Core/AmericanStory.h"
#include "Engine/DamageEvents.h"
#include "Misc/PackageName.h"
#include "SurvivalControlSettings.h"
#include "SurvivalPlayerController.h"
#include "Components/SpotLightComponent.h"
#include "Camera/CameraActor.h"
#include "Core/CityContent.h"
#include "SurvivalGameInstance.h"
#include "SurvivalInteraction.h"
#include "Camera/CameraComponent.h"
#include "GameFramework/SpringArmComponent.h"
#include "GameFramework/CharacterMovementComponent.h"
#include "GameFramework/DamageType.h"
#include "GameFramework/GameModeBase.h"
#include "GameFramework/PlayerController.h"
#include "Components/CapsuleComponent.h"
#include "Components/InputComponent.h"
#include "Components/SkeletalMeshComponent.h"
#include "Animation/AnimInstance.h"
#include "Animation/AnimSequence.h"
#include "Engine/SkeletalMesh.h"
#include "Engine/World.h"
#include "Kismet/GameplayStatics.h"
#include "UObject/ConstructorHelpers.h"
#include "TimerManager.h"
#include "SurvivalInfected.h"
#include "SurvivalBottle.h"
#include "Components/StaticMeshComponent.h"
#include "Components/AudioComponent.h"
#include "Engine/StaticMesh.h"
#include "EngineUtils.h"
#include "Sound/SoundBase.h"
ASurvivalCharacter::ASurvivalCharacter()
{
    PrimaryActorTick.bCanEverTick=true;
    WeaponMesh=CreateDefaultSubobject<UStaticMeshComponent>(TEXT("HeldWeapon"));
    WeaponMesh->SetupAttachment(GetMesh(),TEXT("Bip01_R_Hand"));WeaponMesh->SetCollisionEnabled(ECollisionEnabled::NoCollision);
    GetCapsuleComponent()->InitCapsuleSize(40.0f,96.0f);GetCapsuleComponent()->SetCollisionResponseToChannel(ECC_Visibility,ECR_Block);
    bUseControllerRotationYaw=false;
    auto* Move=GetCharacterMovement();
    Move->bOrientRotationToMovement=true; Move->RotationRate=FRotator(0,540,0);
    Move->MaxWalkSpeed=340; Move->JumpZVelocity=470; Move->AirControl=0.2f;
    Move->GetNavAgentPropertiesRef().bCanCrouch=true;
    Move->MaxWalkSpeedCrouched=170;
    CameraArm=CreateDefaultSubobject<USpringArmComponent>(TEXT("CameraArm"));
    CameraArm->SetupAttachment(GetRootComponent()); CameraArm->TargetArmLength=330;
    CameraArm->SocketOffset=FVector(0,48,65); CameraArm->bUsePawnControlRotation=true;
    CameraArm->bEnableCameraLag=true; CameraArm->CameraLagSpeed=12;
    Camera=CreateDefaultSubobject<UCameraComponent>(TEXT("Camera"));
    Camera->SetupAttachment(CameraArm,USpringArmComponent::SocketName);Camera->FieldOfView=80;
    Flashlight=CreateDefaultSubobject<USpotLightComponent>(TEXT("Flashlight"));Flashlight->SetupAttachment(Camera);Flashlight->SetIntensity(5500);Flashlight->SetAttenuationRadius(1500);Flashlight->SetInnerConeAngle(16);Flashlight->SetOuterConeAngle(32);Flashlight->SetCastShadows(false);Flashlight->SetVisibility(false);
    GetMesh()->SetRelativeLocationAndRotation(FVector(0,0,-96),FRotator(0,-90,0));
    static ConstructorHelpers::FObjectFinder<USkeletalMesh> MeshAsset(TEXT("/Game/Characters/Mannequins/Meshes/SKM_Manny_Simple.SKM_Manny_Simple"));
    if (MeshAsset.Succeeded()) GetMesh()->SetSkeletalMesh(MeshAsset.Object);
    static ConstructorHelpers::FClassFinder<UAnimInstance> Animation(TEXT("/Game/Characters/Mannequins/Anims/Unarmed/ABP_Unarmed"));
    if (Animation.Succeeded()) GetMesh()->SetAnimInstanceClass(Animation.Class);
    GetMesh()->bEnableUpdateRateOptimizations=true;
    GetMesh()->VisibilityBasedAnimTickOption=EVisibilityBasedAnimTickOption::OnlyTickPoseWhenRendered;
}
void ASurvivalCharacter::BeginPlay()
{
    Super::BeginPlay();ConfigureHuman();
    AttackAnimation=LoadObject<UAnimSequence>(nullptr,TEXT("/Game/Characters/Mannequins/Anims/Unarmed/Attack/MM_Attack_01.MM_Attack_01"));
    if (IsPlayerControlled()) if (auto* Game=Cast<USurvivalGameInstance>(GetGameInstance())) Game->ApplyLoadedPlayerState(this);
    StatusMessage=TEXT("Беллуэзер, Орегон • Дэниел Рид. Радио у депо.");
}
void ASurvivalCharacter::PossessedBy(AController* NewController)
{
    Super::PossessedBy(NewController);
    if (IsPlayerControlled()) if (auto* Game=Cast<USurvivalGameInstance>(GetGameInstance())) Game->ApplyLoadedPlayerState(this);
}
void ASurvivalCharacter::Tick(float Delta)
{
    Super::Tick(Delta);
    if(bEditingControls&&bMouseSettingsDrag)if(auto* PC=Cast<APlayerController>(Controller)){float X,Y;if(PC->GetMousePosition(X,Y))TouchMoved(ETouchIndex::Touch10,FVector(X,Y,0));}
    if(!bEditingControls&&!IsCinematicLocked()&&IsAlive()){Bow.Step(Delta);const float Bleed=Trauma.Step(Delta);if(Bleed>0)Stats.Damage(Bleed);}
    AttackCooldown=FMath::Max(0.0f,AttackCooldown-Delta);
    if (IsPlayerControlled()) Equipment.Step(Delta,EarnedRounds());
    if (bHumanAvatar) UpdateHuman();
    FootstepDelay-=Delta;
    if (IsAlive() && !IsCinematicLocked() && (IsPlayerControlled() || FVector::DistSquared(GetActorLocation(),UGameplayStatics::GetPlayerPawn(this,0)?UGameplayStatics::GetPlayerPawn(this,0)->GetActorLocation():GetActorLocation())<FMath::Square(900.f)) && GetCharacterMovement()->IsMovingOnGround() && GetVelocity().SizeSquared2D()>10000 && FootstepDelay<=0) {
        FootstepDelay=bIsCrouched?.65f:GetVelocity().Size2D()>400?.28f:.44f;
        if (auto* Sound=LoadObject<USoundBase>(nullptr,TEXT("/Game/Story/Audio/Footstep.Footstep"))) UGameplayStatics::PlaySoundAtLocation(this,Sound,GetActorLocation(),bIsCrouched?.08f:.2f,1.f,0.f,Cast<USurvivalGameInstance>(GetGameInstance())?Cast<USurvivalGameInstance>(GetGameInstance())->SpatialSound():nullptr);
    }
    const bool Sprint=Trauma.CanSprint() && bSprintRequested && GetVelocity().SizeSquared2D()>400 && !bIsCrouched && !GetCharacterMovement()->IsFalling();
    Stats.Step(Delta,Sprint);
    GetCharacterMovement()->MaxWalkSpeed=(bSprintRequested && Stats.CanSprint() && Trauma.CanSprint() && !bIsCrouched ? 580 : 340)*Trauma.WalkScale();
    if(auto* G=Cast<USurvivalGameInstance>(GetGameInstance()))if(G->FilmDecision==1){const FVector P=GetActorLocation();if(P.X>-22000&&P.X<-8000&&P.Y>5000&&P.Y<17000)GetCharacterMovement()->MaxWalkSpeed*=.6f;}
    Camera->FieldOfView=FMath::FInterpTo(Camera->FieldOfView,bAiming||Bow.drawing ? 62.0f:Sprint && Stats.CanSprint() ? 86.0f:80.0f,Delta,5);
    if (!Stats.Alive()) GetCharacterMovement()->DisableMovement();
}
void ASurvivalCharacter::Forward(float Value)
{
    if (Controller && Stats.Alive() && !IsCinematicLocked() && !bJournalOpen && !bEditingControls) AddMovementInput(FRotationMatrix(FRotator(0,Controller->GetControlRotation().Yaw,0)).GetUnitAxis(EAxis::X),Value);
}
void ASurvivalCharacter::Right(float Value)
{
    if (Controller && Stats.Alive() && !IsCinematicLocked() && !bJournalOpen && !bEditingControls) AddMovementInput(FRotationMatrix(FRotator(0,Controller->GetControlRotation().Yaw,0)).GetUnitAxis(EAxis::Y),Value);
}
void ASurvivalCharacter::Turn(float Value) { if(!bEditingControls)AddControllerYawInput(Value); }
void ASurvivalCharacter::Look(float Value) { if(!bEditingControls)AddControllerPitchInput(Value); }
void ASurvivalCharacter::SprintOn() { if(!bEditingControls && !IsCinematicLocked())bSprintRequested=true; }
void ASurvivalCharacter::SprintOff() { bSprintRequested=false; }
void ASurvivalCharacter::ToggleSprint() { if(!bEditingControls && !IsCinematicLocked())bSprintRequested=!bSprintRequested; }
void ASurvivalCharacter::ToggleCrouch() { if(bEditingControls || IsCinematicLocked())return;if (bIsCrouched) UnCrouch(); else Crouch(); }
void ASurvivalCharacter::JumpPressed() { if (!bEditingControls && !IsCinematicLocked() && CanJump() && Stats.Spend(14)) Jump(); }
void ASurvivalCharacter::SetupPlayerInputComponent(UInputComponent* Input)
{
    Super::SetupPlayerInputComponent(Input);
    Input->BindAxis(TEXT("MoveForward"),this,&ASurvivalCharacter::Forward);
    Input->BindAxis(TEXT("MoveRight"),this,&ASurvivalCharacter::Right);
    Input->BindAxis(TEXT("Turn"),this,&ASurvivalCharacter::Turn);
    Input->BindAxis(TEXT("LookUp"),this,&ASurvivalCharacter::Look);
    Input->BindAction(TEXT("Sprint"),IE_Pressed,this,&ASurvivalCharacter::SprintOn);
    Input->BindAction(TEXT("Sprint"),IE_Released,this,&ASurvivalCharacter::SprintOff);
    Input->BindAction(TEXT("Crouch"),IE_Pressed,this,&ASurvivalCharacter::ToggleCrouch);
    Input->BindAction(TEXT("Jump"),IE_Pressed,this,&ASurvivalCharacter::JumpPressed);
    Input->BindAction(TEXT("Jump"),IE_Released,this,&ACharacter::StopJumping);
    Input->BindAction(TEXT("Interact"),IE_Pressed,this,&ASurvivalCharacter::Interact);
    Input->BindAction(TEXT("Attack"),IE_Pressed,this,&ASurvivalCharacter::Attack);
    Input->BindKey(EKeys::F10,IE_Pressed,this,&ASurvivalCharacter::ToggleControlEditor);
    Input->BindKey(EKeys::F,IE_Pressed,this,&ASurvivalCharacter::ToggleFlashlight);
    Input->BindAction(TEXT("Attack"),IE_Released,this,&ASurvivalCharacter::ReleaseAttack);
    Input->BindKey(EKeys::RightMouseButton,IE_Pressed,this,&ASurvivalCharacter::ToggleAim);
    Input->BindKey(EKeys::H,IE_Pressed,this,&ASurvivalCharacter::UseBandage);
    Input->BindKey(EKeys::R,IE_Pressed,this,&ASurvivalCharacter::ReloadWeapon);
    Input->BindKey(EKeys::Q,IE_Pressed,this,&ASurvivalCharacter::SwitchWeapon);
    Input->BindKey(EKeys::G,IE_Pressed,this,&ASurvivalCharacter::ThrowBottle);
    Input->BindKey(EKeys::Tab,IE_Pressed,this,&ASurvivalCharacter::ToggleJournal);
    Input->BindAction(TEXT("Save"),IE_Pressed,this,&ASurvivalCharacter::Save);
    Input->BindAction(TEXT("Load"),IE_Pressed,this,&ASurvivalCharacter::Load);
    Input->BindTouch(IE_Pressed,this,&ASurvivalCharacter::TouchPressed);
    Input->BindTouch(IE_Released,this,&ASurvivalCharacter::TouchReleased);
    Input->BindTouch(IE_Repeat,this,&ASurvivalCharacter::TouchMoved);
}
ASurvivalInteraction* ASurvivalCharacter::GetFocusedInteraction() const
{
    FVector Origin;FRotator View;
    if (auto* PC=Cast<APlayerController>(Controller)) PC->GetPlayerViewPoint(Origin,View); else return nullptr;
    FCollisionQueryParams Params(SCENE_QUERY_STAT(InteractionFocus),false,this);FHitResult Hit;
    GetWorld()->LineTraceSingleByChannel(Hit,Origin,Origin+View.Vector()*850,ECC_Visibility,Params);
    return Cast<ASurvivalInteraction>(Hit.GetActor());
}
void ASurvivalCharacter::Interact()
{
    if (bEditingControls) return;
    if (bStoryActive) { AdvanceStory();return; }
    if (!Stats.Alive()) return;
    bJournalOpen=false;
    auto* Target=GetFocusedInteraction();
    if (!Target) { StatusMessage=TEXT("Посмотрите на предмет поближе."); return; }
    FString Error;
    if (Target->Interact(this,Error)) { StatusMessage=TEXT("Готово. Изменения сохранены."); Save(); }
    else StatusMessage=TEXT("Пока недоступно: ")+Error;
}
void ASurvivalCharacter::Attack()
{
    if(bEditingControls||bJournalOpen){MouseSettingsPressed();return;}
    if(bBowEquipped){if(IsAlive()&&!IsCinematicLocked()&&Trauma.CanShoot())if(auto* G=Cast<USurvivalGameInstance>(GetGameInstance()))Bow.Begin(G->FieldInventory.Get(survival::Supply::Arrows)>0);return;}
    if (IsPlayerControlled() && Equipment.state.pistol) { Shoot();return; }
    if (IsCinematicLocked() || bEditingControls || bJournalOpen || AttackCooldown>0 || !Stats.Spend(18)) return;
    AttackCooldown=0.75f;
    if (IsPlayerControlled() && Controller) SetActorRotation(FRotator(0,Controller->GetControlRotation().Yaw,0));
    if (!bHumanAvatar) if (auto* Anim=GetMesh()->GetAnimInstance()) if (AttackAnimation) Anim->PlaySlotAnimationAsDynamicMontage(AttackAnimation,TEXT("DefaultSlot"),0.06f,0.12f);
    FTimerHandle HitTimer;GetWorldTimerManager().SetTimer(HitTimer,this,&ASurvivalCharacter::DeliverMelee,0.18f,false);
}
void ASurvivalCharacter::DeliverMelee()
{
    if (!Stats.Alive() || IsCinematicLocked() || bEditingControls) return;
    const FVector Start=GetActorLocation()+FVector(0,0,30);
    const FVector End=Start+GetActorForwardVector()*170;
    TArray<FHitResult> Hits;FCollisionQueryParams Params(SCENE_QUERY_STAT(Melee),false,this);
    GetWorld()->SweepMultiByChannel(Hits,Start,End,FQuat::Identity,ECC_Pawn,FCollisionShape::MakeSphere(45),Params);
    TSet<AActor*> Damaged;
    for (const FHitResult& Hit:Hits)
    {
        auto* Other=Cast<ASurvivalCharacter>(Hit.GetActor());
        if (!Other || Other==this || Damaged.Contains(Other) || (IsPlayerControlled() ? !Cast<ASurvivalInfected>(Other) : !Other->IsPlayerControlled())) continue;
        FHitResult Obstruction;
        if (GetWorld()->LineTraceSingleByChannel(Obstruction,Start,Other->GetActorLocation()+FVector(0,0,30),ECC_Visibility,Params) && Obstruction.GetActor()!=Other) continue;
        float Damage=25;
        if (IsPlayerControlled()) if (auto* G=Cast<USurvivalGameInstance>(GetGameInstance())) if (G->HasWorldFlag(TEXT("has_pipe"))) Damage=42;
        Damaged.Add(Other);UGameplayStatics::ApplyDamage(Other,Damage,Controller,this,UDamageType::StaticClass());
    }
}
float ASurvivalCharacter::TakeDamage(float Amount,const FDamageEvent& Event,AController* Instigator,AActor* Causer)
{
    if (IsCinematicLocked() || bEditingControls) return 0;
    survival::WoundZone Zone=survival::WoundZone::Torso;
    if(Event.IsOfType(FPointDamageEvent::ClassID)){
        const auto& Hit=static_cast<const FPointDamageEvent&>(Event).HitInfo;const FVector Local=GetActorTransform().InverseTransformPosition(Hit.ImpactPoint);
        const FString Bone=Hit.BoneName.ToString().ToLower();Zone=Bone.Contains(TEXT("head"))||Local.Z>55?survival::WoundZone::Head:Local.Z<-30?survival::WoundZone::Leg:FMath::Abs(Local.Y)>27?survival::WoundZone::Arm:survival::WoundZone::Torso;
    }
    const float Applied=Stats.Damage(Trauma.Hit(Amount,Zone));
    if (Applied>0) Super::TakeDamage(Applied,Event,Instigator,Causer);
    if (Applied>0 && !Stats.Alive()) { GetCharacterMovement()->DisableMovement();
        if (!bHumanAvatar) if (auto* Death=LoadObject<UAnimSequence>(nullptr,TEXT("/Game/Characters/Mannequins/Anims/Death/MM_Death_Front_01.MM_Death_Front_01"))) GetMesh()->PlayAnimation(Death,false);
        StatusMessage=TEXT("Вы погибли. F9 / Загрузить — вернуться к сохранению."); }
    return Applied;
}
bool ASurvivalCharacter::RestoreVitals(float Health,float Stamina)
{
    if (!Stats.Restore(Health,Stamina)) return false;
    if (bHumanAvatar) { GetMesh()->SetRelativeLocationAndRotation(Stats.Alive()?FVector(0,0,-96):FVector(0,0,-75),Stats.Alive()?FRotator(0,-90,0):FRotator(0,-90,85)); }
    if (!IsPlayerControlled()) GetCapsuleComponent()->SetCollisionEnabled(Stats.Alive()?ECollisionEnabled::QueryAndPhysics:ECollisionEnabled::NoCollision);
    GetWorldTimerManager().ClearAllTimersForObject(this);AttackCooldown=0;
    if (Stats.Alive()) {
        GetCharacterMovement()->SetMovementMode(MOVE_Walking);
        if (!bHumanAvatar) GetMesh()->SetAnimationMode(EAnimationMode::AnimationBlueprint);
    }
    return true;
}
void ASurvivalCharacter::Save() { if (auto* Game=Cast<USurvivalGameInstance>(GetGameInstance())) if (!Game->SaveProgress()) StatusMessage=TEXT("Не удалось сохранить прогресс."); }
void ASurvivalCharacter::Load() { Bow.Cancel();bAiming=false;EndStory();bJournalOpen=false; if (auto* Game=Cast<USurvivalGameInstance>(GetGameInstance())) if (Game->LoadProgress()) { Game->ApplyLoadedPlayerState(this);StatusMessage=TEXT("Прогресс восстановлен."); } }
void ASurvivalCharacter::TouchPressed(ETouchIndex::Type Finger,FVector Position)
{
    auto* PC=Cast<APlayerController>(Controller);if (!PC) return;
    int32 W=0,H=0;PC->GetViewportSize(W,H);if (!W || !H) return;
    const FVector2D P(Position.X/W,Position.Y/H);const float Aspect=static_cast<float>(W)/H;auto* Settings=USurvivalControlSettings::Get();
    if(bJournalOpen){
        const int32 Hit=Settings->Hit(P,Aspect,false);if(Hit==static_cast<int32>(survival::Control::Journal)){ToggleJournal();return;}
        if(P.X>=.12f&&P.X<=.88f&&P.Y>=.79f&&P.Y<.86f){Settings->bEnglishStory=!Settings->bEnglishStory;Settings->Store();return;}
        if(P.X>=.12f&&P.X<=.88f&&P.Y>=.53f&&P.Y<.78f)FieldAction(FMath::Clamp(FMath::FloorToInt((P.Y-.53f)/.05f),0,4));return;
    }
    if(bEditingControls) {
        if(P.X>=.28f&&P.X<=.67f&&P.Y>=.30f&&P.Y<=.70f) {
            const int32 Row=FMath::Clamp(FMath::FloorToInt((P.Y-.31f)/.06f),0,5);const float Sign=P.X>.52f?1.f:-1.f;
            if(Row==0)Settings->Sensitivity+=Sign*.1f;
            else if(Row==1)Settings->ButtonScale+=Sign*.05f;
            else if(Row==2)Settings->Opacity+=Sign*.05f;
            else if(Row==3)Settings->MirrorLayout();
            else if(Row==4){if(Sign<0)Settings->bInvertY=!Settings->bInvertY;else Settings->bPerformanceMode=!Settings->bPerformanceMode;}
            else if(Sign<0)Settings->ResetLayout();else { ToggleControlEditor();return; }
            Settings->Normalize();Settings->Store();return;
        }
        ControlDragIndex=Settings->Hit(P,Aspect,true);if(ControlDragIndex!=INDEX_NONE)ControlDragFinger=static_cast<int32>(Finger);return;
    }
    const int32 Hit=Settings->Hit(P,Aspect,false);
    if(Hit!=INDEX_NONE) { switch(static_cast<survival::Control>(Hit)) {
      case survival::Control::Interact:Interact();break;case survival::Control::Attack:AttackFinger=static_cast<int32>(Finger);Attack();break;
      case survival::Control::Sprint:ToggleSprint();break;case survival::Control::Jump:JumpFinger=static_cast<int32>(Finger);JumpPressed();break;
      case survival::Control::Crouch:ToggleCrouch();break;case survival::Control::Reload:ReloadWeapon();break;
      case survival::Control::Throw:ThrowBottle();break;case survival::Control::Weapon:SwitchWeapon();break;
      case survival::Control::Journal:ToggleJournal();break;case survival::Control::Save:Save();break;
      case survival::Control::Load:Load();break;case survival::Control::Settings:ToggleControlEditor();break;
      case survival::Control::Flashlight:ToggleFlashlight();break;default:break;
    }return; }
    const FVector2D Stick=Settings->Position(survival::Control::Move,Aspect);
    if(!survival::ControlHit({static_cast<float>(P.X),static_cast<float>(P.Y)},{static_cast<float>(Stick.X),static_cast<float>(Stick.Y)},.18f*Settings->ButtonScale,Aspect)&&LookFinger<0){LookFinger=static_cast<int32>(Finger);LastTouch=Position;}

}
void ASurvivalCharacter::TouchReleased(ETouchIndex::Type Finger,FVector Position) {
    if(AttackFinger==static_cast<int32>(Finger)){AttackFinger=-1;ReleaseAttack();}
    if(ControlDragFinger==static_cast<int32>(Finger)){ControlDragFinger=-1;ControlDragIndex=-1;USurvivalControlSettings::Get()->Store();}
    if (LookFinger==static_cast<int32>(Finger)) LookFinger=-1;
    if (JumpFinger==static_cast<int32>(Finger)) { StopJumping();JumpFinger=-1; }
}
void ASurvivalCharacter::TouchMoved(ETouchIndex::Type Finger,FVector Position)
{
    if(bEditingControls) {
        if(ControlDragFinger==static_cast<int32>(Finger)&&ControlDragIndex>=0)if(auto* PC=Cast<APlayerController>(Controller)){int32 W,H;PC->GetViewportSize(W,H);if(W>0&&H>0)USurvivalControlSettings::Get()->Move(ControlDragIndex,FVector2D(Position.X/W,Position.Y/H),static_cast<float>(W)/H);}return;
    }
    if (LookFinger!=static_cast<int32>(Finger)) return;
    const FVector Delta=Position-LastTouch;LastTouch=Position;
    const auto* S=USurvivalControlSettings::Get();AddControllerYawInput(Delta.X*0.09f*S->Sensitivity);AddControllerPitchInput(Delta.Y*0.09f*S->Sensitivity*(S->bInvertY?-1:1));
}

void ASurvivalCharacter::FellOutOfWorld(const UDamageType& DamageType)
{
    // A development district edge must not leave the player without a pawn,
    // input or recovery controls. Non-player actors retain normal cleanup.
    if (IsPlayerControlled()) if (auto* Mode=GetWorld()->GetAuthGameMode())
        if (auto* Start=Mode->FindPlayerStart(Controller))
            if (TeleportTo(Start->GetActorLocation()+FVector(0,0,20),Start->GetActorRotation(),false,false)) {
                RestoreVitals(100,100);Load();StatusMessage=TEXT("Возврат к безопасной точке.");return;
            }
    Super::FellOutOfWorld(DamageType);
}

void ASurvivalCharacter::ToggleJournal() { if (!bStoryActive && !bEditingControls){bJournalOpen=!bJournalOpen;Bow.Cancel();if(auto* PC=Cast<APlayerController>(Controller)){PC->bShowMouseCursor=bJournalOpen;if(bJournalOpen){FInputModeGameAndUI Mode;Mode.SetHideCursorDuringCapture(false);PC->SetInputMode(Mode);}else PC->SetInputMode(FInputModeGameOnly());}} }
void ASurvivalCharacter::BeginStory(FName Id,AActor* Subject,bool Cinematic)
{
    const auto* Site=survival::FindCitySite(TCHAR_TO_UTF8(*Id.ToString()));
    if (!Site || Site->lines.empty()) return;
    EndStory();bJournalOpen=false;StoryLines.Reset();StoryLine=0;
    StorySpeaker=UTF8_TO_TCHAR(Site->speaker.c_str());
    for (const auto& Line:Site->lines) StoryLines.Add(UTF8_TO_TCHAR(Line.c_str()));
    bStoryActive=true;bStoryLocksMovement=Cinematic;CurrentStory=Id;SpeakStoryLine();
    if(!Cinematic)return;
    if (auto* PC=Cast<APlayerController>(Controller)) {
        PC->SetIgnoreMoveInput(true);PC->SetIgnoreLookInput(true);
        if (Subject) {
            TArray<AActor*> Speakers;UGameplayStatics::GetAllActorsWithTag(this,FName(UTF8_TO_TCHAR(Site->speaker.c_str())),Speakers);
            AActor* FocusActor=Subject;for (auto* Actor:Speakers) if (FVector::DistSquared(Actor->GetActorLocation(),Subject->GetActorLocation())<FMath::Square(2500.f)) { FocusActor=Actor;break; }
            const FVector Focus=FocusActor->GetActorLocation()+FVector(0,0,100);
            FVector View=Focus+FVector(-260,-220,100);
            FHitResult Hit;FCollisionQueryParams Params(SCENE_QUERY_STAT(StoryCamera),false,Subject);Params.AddIgnoredActor(this);
            if (GetWorld()->LineTraceSingleByChannel(Hit,Focus,View,ECC_Visibility,Params)) View=Hit.Location+(Focus-Hit.Location).GetSafeNormal()*25;
            StoryCamera=GetWorld()->SpawnActor<ACameraActor>(View,(Focus-View).Rotation());
            if (StoryCamera) PC->SetViewTargetWithBlend(StoryCamera,0.6f);
        }
    }
}
void ASurvivalCharacter::AdvanceStory()
{
    if (!bStoryActive) return;
    if (++StoryLine>=StoryLines.Num()) {const int32 Completed=ActiveFilm;EndStory();if(Completed>=0)if(auto* G=Cast<USurvivalGameInstance>(GetGameInstance()))if(G->FilmProgress==Completed){++G->FilmProgress;Save();}}else SpeakStoryLine();
}
void ASurvivalCharacter::EndStory()
{
    if (!bStoryActive) return;
    bStoryActive=false;GetWorldTimerManager().ClearTimer(FilmLineTimer);ActiveFilm=-1;
    if (StoryAudio) { StoryAudio->OnAudioFinished.RemoveAll(this);StoryAudio->Stop();StoryAudio=nullptr; }
    if (bStoryLocksMovement) if (auto* PC=Cast<APlayerController>(Controller)) { PC->SetIgnoreMoveInput(false);PC->SetIgnoreLookInput(false);PC->SetViewTarget(this); }
    if (StoryCamera) { StoryCamera->Destroy();StoryCamera=nullptr; }
}

void ASurvivalCharacter::ConfigureHuman()
{
    const FString BodyRole=AvatarRole==TEXT("Daniel")?TEXT("Arsen"):AvatarRole.ToString();
    const FString Base=TEXT("/Game/Story/Characters/")+BodyRole+TEXT("/");
    auto* Body=LoadObject<USkeletalMesh>(nullptr,*(Base+TEXT("Body.Body")));
    if (!Body) return;
    GetMesh()->SetSkeletalMesh(Body);GetMesh()->SetAnimationMode(EAnimationMode::AnimationSingleNode);bHumanAvatar=true;
    for (const TCHAR* Name:{TEXT("Idle"),TEXT("Walk"),TEXT("Run"),TEXT("Crouch")}) {
        const FString Clip=Base+Name+TEXT(".")+Name;
        if (auto* Anim=LoadObject<UAnimSequence>(nullptr,*Clip)) HumanAnimations.Add(FName(Name),Anim);
    }
    UpdateHuman();RefreshWeapon();
}
void ASurvivalCharacter::UpdateHuman()
{
    if (!IsAlive()) { GetMesh()->bPauseAnims=true;GetMesh()->SetRelativeLocationAndRotation(FVector(0,0,-75),FRotator(0,-90,85));if (!IsPlayerControlled()) GetCapsuleComponent()->SetCollisionEnabled(ECollisionEnabled::NoCollision);return; }GetMesh()->bPauseAnims=false;
    const float Speed=GetVelocity().Size2D();const FName Key=bIsCrouched?TEXT("Crouch"):Speed>390?TEXT("Run"):Speed>15?TEXT("Walk"):TEXT("Idle");
    if (auto* Anim=HumanAnimations.Find(Key)) if (PlayingHumanAnimation!=*Anim) { PlayingHumanAnimation=*Anim;GetMesh()->PlayAnimation(*Anim,true); }
    GetMesh()->SetPlayRate(Key==TEXT("Walk")?FMath::Clamp(Speed/140,.6f,2.4f):Key==TEXT("Run")?FMath::Clamp(Speed/390,.8f,1.5f):1.0f);
}
int32 ASurvivalCharacter::EarnedRounds() const { auto* G=Cast<USurvivalGameInstance>(GetGameInstance());return G?G->GetItemCount(TEXT("ammo_pack"))*8+G->FieldInventory.Get(survival::Supply::Rounds):0; }
int32 ASurvivalCharacter::EarnedBottles() const { auto* G=Cast<USurvivalGameInstance>(GetGameInstance());return G?G->GetItemCount(TEXT("bottle_pack")):0; }
bool ASurvivalCharacter::RestoreCombat(const survival::CombatSnapshot& State)
{
    auto* G=Cast<USurvivalGameInstance>(GetGameInstance());
    const bool Good=Equipment.Restore(State,EarnedRounds(),EarnedBottles(),G && G->HasWorldFlag(TEXT("has_pistol")));if (Good) RefreshWeapon();return Good;
}
void ASurvivalCharacter::RefreshWeapon()
{
    const TCHAR* Path=bBowEquipped?TEXT("/Game/Story/Props/Bow.Bow"):Equipment.state.pistol?TEXT("/Game/Story/Props/Pistol.Pistol"):TEXT("/Game/Story/Props/Pipe.Pipe");
    WeaponMesh->SetStaticMesh(LoadObject<UStaticMesh>(nullptr,Path));
    auto* G=Cast<USurvivalGameInstance>(GetGameInstance());WeaponMesh->SetVisibility(IsPlayerControlled() && (bBowEquipped || Equipment.state.pistol || (G && G->HasWorldFlag(TEXT("has_pipe")))));
    WeaponMesh->AttachToComponent(GetMesh(),FAttachmentTransformRules::SnapToTargetNotIncludingScale,GetMesh()->DoesSocketExist(TEXT("Bip01_R_Hand"))?TEXT("Bip01_R_Hand"):TEXT("hand_r"));
    WeaponMesh->SetRelativeRotation(bBowEquipped?FRotator(0,0,0):FRotator(0,90,0));
}
void ASurvivalCharacter::SwitchWeapon()
{
    if (!IsAlive() || IsCinematicLocked() || bEditingControls || bJournalOpen) return;
    auto* G=Cast<USurvivalGameInstance>(GetGameInstance());if(!G)return;Bow.Cancel();
    const bool OwnsBow=G->FieldInventory.Get(survival::Supply::Bow)>0,OwnsPistol=G->HasWorldFlag(TEXT("has_pistol"));
    if(bBowEquipped){bBowEquipped=false;Equipment.Select(false);}else if(Equipment.state.pistol){Equipment.Select(false);bBowEquipped=OwnsBow;}else if(OwnsPistol)Equipment.Select(true);else bBowEquipped=OwnsBow;
    RefreshWeapon();StatusMessage=bBowEquipped?TEXT("Лук: удерживай атаку, отпусти для выстрела."):Equipment.state.pistol?TEXT("Пистолет • R — перезарядить"):TEXT("Ближний бой");
}
void ASurvivalCharacter::ReloadWeapon()
{
    if (!IsAlive() || IsCinematicLocked() || bEditingControls || bJournalOpen) return;
    if (Equipment.Reload(EarnedRounds())) StatusMessage=TEXT("Перезарядка...");else StatusMessage=TEXT("Нет запасных патронов или магазин полный.");
}
void ASurvivalCharacter::Shoot()
{
    if (!IsAlive() || IsCinematicLocked() || bEditingControls || bJournalOpen || !Trauma.CanShoot()) return;
    if (!Equipment.Fire()) { if (Equipment.state.loaded==0 && Equipment.reloading==0) ReloadWeapon();return; }
    FVector Start;FRotator Direction;if (auto* PC=Cast<APlayerController>(Controller)) PC->GetPlayerViewPoint(Start,Direction);else return;
    FCollisionQueryParams Params(SCENE_QUERY_STAT(PistolAim),false,this);FHitResult Aim,Hit;
    FVector End=Start+Direction.Vector()*8000;
    if (GetWorld()->LineTraceSingleByChannel(Aim,Start,End,ECC_Visibility,Params)) End=Aim.ImpactPoint;
    const FVector Muzzle=GetActorLocation()+FVector(0,0,40)+Direction.Vector()*40;
    if (GetWorld()->LineTraceSingleByChannel(Hit,Muzzle,End+Direction.Vector()*4,ECC_Visibility,Params)) if (auto* Enemy=Cast<ASurvivalInfected>(Hit.GetActor())) UGameplayStatics::ApplyPointDamage(Enemy,45,Direction.Vector(),Hit,Controller,this,UDamageType::StaticClass());
    for (TActorIterator<ASurvivalInfected> It(GetWorld());It;++It) It->HearNoise(GetActorLocation(),4500);
    if (auto* Sound=LoadObject<USoundBase>(nullptr,TEXT("/Game/Story/Audio/Shot.Shot"))) UGameplayStatics::PlaySoundAtLocation(this,Sound,GetActorLocation(),.7f,1.f,0.f,Cast<USurvivalGameInstance>(GetGameInstance())?Cast<USurvivalGameInstance>(GetGameInstance())->SpatialSound():nullptr);
    AddControllerPitchInput(-.8f);StatusMessage=TEXT("Выстрел. Заражённые слышат тебя.");
}
void ASurvivalCharacter::ThrowBottle()
{
    if (!IsAlive() || IsCinematicLocked() || bEditingControls || bJournalOpen || !Equipment.Throw(EarnedBottles())) return;
    const FVector Direction=Controller?Controller->GetControlRotation().Vector():GetActorForwardVector();
    auto* Bottle=GetWorld()->SpawnActor<ASurvivalBottle>(GetActorLocation()+FVector(0,0,65)+Direction*85,Direction.Rotation());
    if (!Bottle) { --Equipment.state.bottlesUsed;return; }Bottle->Launch(Direction*1200+FVector(0,0,420));StatusMessage=TEXT("Бутылка отвлечёт тех, кто ещё не заметил тебя.");
}
void ASurvivalCharacter::SpeakStoryLine()
{
    GetWorldTimerManager().ClearTimer(FilmLineTimer);
    if (StoryAudio) { StoryAudio->OnAudioFinished.RemoveAll(this);StoryAudio->Stop();StoryAudio=nullptr; }
    if (!StoryLines.IsValidIndex(StoryLine)) return;
    FString& Line=StoryLines[StoryLine];int32 Colon;
    if (Line.FindChar(TEXT(':'),Colon) && Colon>0 && Colon<18) { StorySpeaker=Line.Left(Colon);Line=Line.Mid(Colon+1).TrimStartAndEnd(); }
    if(ActiveFilm>=0){
        const int32 ClipLine=ActiveFilm==14?StoryLine-1:StoryLine;const auto& Scene=survival::FilmScenes()[ActiveFilm];const FString Name=FString(UTF8_TO_TCHAR(Scene.id.c_str()))+TEXT("_")+FString::FromInt(ClipLine);const FString Package=TEXT("/Game/Story/FilmVoices/")+Name;
        if(ClipLine>=0&&FPackageName::DoesPackageExist(Package))if(auto* Wave=LoadObject<USoundBase>(nullptr,*(Package+TEXT(".")+Name))){StoryAudio=UGameplayStatics::SpawnSound2D(this,Wave);if(StoryAudio){StoryAudio->OnAudioFinished.AddDynamic(this,&ASurvivalCharacter::AdvanceStory);return;}}
        GetWorldTimerManager().SetTimer(FilmLineTimer,this,&ASurvivalCharacter::AdvanceStory,FMath::Clamp(StoryLines[StoryLine].Len()*.065f,3.0f,11.0f),false);return;
    }
    const FString Name=CurrentStory.ToString()+TEXT("_")+FString::FromInt(StoryLine);
    if (auto* Wave=LoadObject<USoundBase>(nullptr,*(TEXT("/Game/Story/Voices/")+Name+TEXT(".")+Name))) { StoryAudio=UGameplayStatics::SpawnSound2D(this,Wave);if(StoryAudio)StoryAudio->OnAudioFinished.AddDynamic(this,&ASurvivalCharacter::AdvanceStory); }
}

void ASurvivalCharacter::ToggleControlEditor()
{
 if(IsCinematicLocked())return;bEditingControls=!bEditingControls;bJournalOpen=false;LookFinger=-1;ControlDragFinger=-1;ControlDragIndex=-1;bSprintRequested=false;
 if(auto* PC=Cast<ASurvivalPlayerController>(Controller)){PC->bShowMouseCursor=bEditingControls;if(bEditingControls){FInputModeGameAndUI Mode;Mode.SetHideCursorDuringCapture(false);Mode.SetLockMouseToViewportBehavior(EMouseLockMode::DoNotLock);PC->SetInputMode(Mode);GetCharacterMovement()->StopMovementImmediately();}else PC->SetInputMode(FInputModeGameOnly());PC->RefreshTouchLayout(!bEditingControls);}
 if(!bEditingControls)USurvivalControlSettings::Get()->Store();
}
void ASurvivalCharacter::ToggleFlashlight() { if(IsAlive()&&!bEditingControls)Flashlight->SetVisibility(!Flashlight->IsVisible()); }
void ASurvivalCharacter::MouseSettingsPressed() { if(!bEditingControls&&!bJournalOpen)return;if(auto* PC=Cast<APlayerController>(Controller)){float X,Y;if(PC->GetMousePosition(X,Y)){bMouseSettingsDrag=true;TouchPressed(ETouchIndex::Touch10,FVector(X,Y,0));}} }
void ASurvivalCharacter::MouseSettingsReleased() { if(bMouseSettingsDrag){bMouseSettingsDrag=false;TouchReleased(ETouchIndex::Touch10,FVector::ZeroVector);} }

void ASurvivalCharacter::ToggleAim(){if(!bEditingControls&&!IsCinematicLocked())bAiming=!bAiming;}
void ASurvivalCharacter::ReleaseAttack(){
 MouseSettingsReleased();const float Power=Bow.Release();if(Power<=0||!bBowEquipped||!IsAlive()||bEditingControls||IsCinematicLocked()||!Trauma.CanShoot())return;
 auto* G=Cast<USurvivalGameInstance>(GetGameInstance());if(!G||G->FieldInventory.Get(survival::Supply::Arrows)<=0)return;
 FVector Eye;FRotator View;if(auto* PC=Cast<APlayerController>(Controller))PC->GetPlayerViewPoint(Eye,View);else return;
 FHitResult Hit;FCollisionQueryParams Params(SCENE_QUERY_STAT(BowAim),false,this);FVector End=Eye+View.Vector()*15000;
 if(GetWorld()->LineTraceSingleByChannel(Hit,Eye,End,ECC_Visibility,Params))End=Hit.ImpactPoint;
 const FVector Start=GetActorLocation()+FVector(0,0,50)+View.Vector()*48;FActorSpawnParameters Spawn;Spawn.Owner=this;Spawn.Instigator=this;Spawn.SpawnCollisionHandlingOverride=ESpawnActorCollisionHandlingMethod::AdjustIfPossibleButDontSpawnIfColliding;
 auto* Arrow=GetWorld()->SpawnActor<ASurvivalArrow>(Start,(End-Start).Rotation(),Spawn);if(!Arrow)return;
 G->FieldInventory.Spend(survival::Supply::Arrows);Arrow->Launch(End-Start,Power,Controller);
 for(TActorIterator<ASurvivalInfected> It(GetWorld());It;++It)It->HearNoise(GetActorLocation(),350);
 if(auto* Sound=LoadObject<USoundBase>(nullptr,TEXT("/Game/Story/Audio/Bow.Bow")))UGameplayStatics::PlaySoundAtLocation(this,Sound,Start,.35f,1.f,0.f,G->SpatialSound());
}
void ASurvivalCharacter::UseBandage(){FieldAction(3);}
void ASurvivalCharacter::FieldAction(int32 Action){
 if(!IsAlive()||IsCinematicLocked()||bEditingControls)return;auto* G=Cast<USurvivalGameInstance>(GetGameInstance());if(!G)return;bool OK=false;
 if(Action<3&&Action>=0)OK=G->FieldInventory.Craft(Action);
 if(Action==3&&(Trauma.bleeding>0||Stats.health<100)&&G->FieldInventory.Spend(survival::Supply::Bandage)){Trauma.Bandage();Stats.health=FMath::Min(100.f,Stats.health+22);OK=true;}
 if(Action==4&&(Trauma.leg>0||Trauma.arm>0)&&G->FieldInventory.Spend(survival::Supply::Splint)){Trauma.Splint();OK=true;}
 StatusMessage=OK?TEXT("Готово. Ресурсы использованы."):TEXT("Нет материалов или лечение не требуется.");if(OK)Save();
}

void ASurvivalCharacter::BeginFilm(int32 Index,AActor* Subject){
 const auto& Scenes=survival::FilmScenes();if(Index<0||Index>=static_cast<int32>(Scenes.size()))return;
 EndStory();Bow.Cancel();const auto& Scene=Scenes[Index];ActiveFilm=Index;bStoryActive=true;bStoryLocksMovement=Scene.cinematic;bJournalOpen=false;StoryLine=0;StorySpeaker=TEXT("");StoryLines.Reset();
 for(const auto& Line:USurvivalControlSettings::Get()->bEnglishStory?Scene.en:Scene.ru)StoryLines.Add(UTF8_TO_TCHAR(Line.c_str()));
 if(Index==14)if(auto* G=Cast<USurvivalGameInstance>(GetGameInstance()))StoryLines.Insert(USurvivalControlSettings::Get()->bEnglishStory?(G->FilmDecision==1?TEXT("Water enters the lower quarter. Homes must be abandoned; the tunnel is open."):TEXT("The gate holds. Homes stay dry; Hart dismantles his crossing and loses its supplies.")):(G->FilmDecision==1?TEXT("В канале появилась вода. Низкие дома придётся оставить; тоннель к переправе открыт."):TEXT("Шлюз удержан. Дома остались сухими; Харт разбирает переправу на понтон и теряет запасы.")),0);
 if(bStoryLocksMovement)if(auto* PC=Cast<APlayerController>(Controller)){
  PC->SetIgnoreMoveInput(true);PC->SetIgnoreLookInput(true);GetCharacterMovement()->StopMovementImmediately();const FVector Focus=(Subject?Subject->GetActorLocation():GetActorLocation())+FVector(0,0,60);
  FVector View=Focus+GetActorForwardVector()*280+GetActorRightVector()*220+FVector(0,0,50);FHitResult Hit;FCollisionQueryParams Params(SCENE_QUERY_STAT(FilmCamera),false,this);if(Subject)Params.AddIgnoredActor(Subject);
  if(GetWorld()->LineTraceSingleByChannel(Hit,Focus,View,ECC_Visibility,Params))View=Hit.Location+(Focus-Hit.Location).GetSafeNormal()*25;
  StoryCamera=GetWorld()->SpawnActor<ACameraActor>(View,(Focus-View).Rotation());if(StoryCamera)PC->SetViewTargetWithBlend(StoryCamera,.7f);
 }SpeakStoryLine();
}
