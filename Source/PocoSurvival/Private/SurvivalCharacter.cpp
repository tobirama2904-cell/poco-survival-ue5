#include "SurvivalCharacter.h"
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
ASurvivalCharacter::ASurvivalCharacter()
{
    PrimaryActorTick.bCanEverTick=true;
    GetCapsuleComponent()->InitCapsuleSize(40.0f,96.0f);
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
    Super::BeginPlay();
    AttackAnimation=LoadObject<UAnimSequence>(nullptr,TEXT("/Game/Characters/Mannequins/Anims/Unarmed/Attack/MM_Attack_01.MM_Attack_01"));
    if (IsPlayerControlled()) if (auto* Game=Cast<USurvivalGameInstance>(GetGameInstance())) Game->ApplyLoadedPlayerState(this);
    StatusMessage=TEXT("Найдите катушку в мастерской и топливо у ворот.");
}
void ASurvivalCharacter::PossessedBy(AController* NewController)
{
    Super::PossessedBy(NewController);
    if (IsPlayerControlled()) if (auto* Game=Cast<USurvivalGameInstance>(GetGameInstance())) Game->ApplyLoadedPlayerState(this);
}
void ASurvivalCharacter::Tick(float Delta)
{
    Super::Tick(Delta);
    AttackCooldown=FMath::Max(0.0f,AttackCooldown-Delta);
    const bool Sprint=bSprintRequested && GetVelocity().SizeSquared2D()>400 && !bIsCrouched && !GetCharacterMovement()->IsFalling();
    Stats.Step(Delta,Sprint);
    GetCharacterMovement()->MaxWalkSpeed=bSprintRequested && Stats.CanSprint() && !bIsCrouched ? 580 : 340;
    Camera->FieldOfView=FMath::FInterpTo(Camera->FieldOfView,Sprint && Stats.CanSprint() ? 86.0f:80.0f,Delta,5);
    if (!Stats.Alive()) GetCharacterMovement()->DisableMovement();
}
void ASurvivalCharacter::Forward(float Value)
{
    if (Controller && Stats.Alive()) AddMovementInput(FRotationMatrix(FRotator(0,Controller->GetControlRotation().Yaw,0)).GetUnitAxis(EAxis::X),Value);
}
void ASurvivalCharacter::Right(float Value)
{
    if (Controller && Stats.Alive()) AddMovementInput(FRotationMatrix(FRotator(0,Controller->GetControlRotation().Yaw,0)).GetUnitAxis(EAxis::Y),Value);
}
void ASurvivalCharacter::Turn(float Value) { AddControllerYawInput(Value); }
void ASurvivalCharacter::Look(float Value) { AddControllerPitchInput(Value); }
void ASurvivalCharacter::SprintOn() { bSprintRequested=true; }
void ASurvivalCharacter::SprintOff() { bSprintRequested=false; }
void ASurvivalCharacter::ToggleSprint() { bSprintRequested=!bSprintRequested; }
void ASurvivalCharacter::ToggleCrouch() { if (bIsCrouched) UnCrouch(); else Crouch(); }
void ASurvivalCharacter::JumpPressed() { if (CanJump() && Stats.Spend(14)) Jump(); }
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
    if (!Stats.Alive()) return;
    auto* Target=GetFocusedInteraction();
    if (!Target) { StatusMessage=TEXT("Посмотрите на предмет поближе."); return; }
    FString Error;
    if (Target->Interact(this,Error)) { StatusMessage=TEXT("Готово. Изменения сохранены."); Save(); }
    else StatusMessage=TEXT("Пока недоступно: ")+Error;
}
void ASurvivalCharacter::Attack()
{
    if (AttackCooldown>0 || !Stats.Spend(18)) return;
    AttackCooldown=0.75f;
    if (IsPlayerControlled() && Controller) SetActorRotation(FRotator(0,Controller->GetControlRotation().Yaw,0));
    if (auto* Anim=GetMesh()->GetAnimInstance()) if (AttackAnimation) Anim->PlaySlotAnimationAsDynamicMontage(AttackAnimation,TEXT("DefaultSlot"),0.06f,0.12f);
    FTimerHandle HitTimer;GetWorldTimerManager().SetTimer(HitTimer,this,&ASurvivalCharacter::DeliverMelee,0.18f,false);
}
void ASurvivalCharacter::DeliverMelee()
{
    if (!Stats.Alive()) return;
    const FVector Start=GetActorLocation()+FVector(0,0,30);
    const FVector End=Start+GetActorForwardVector()*170;
    TArray<FHitResult> Hits;FCollisionQueryParams Params(SCENE_QUERY_STAT(Melee),false,this);
    GetWorld()->SweepMultiByChannel(Hits,Start,End,FQuat::Identity,ECC_Pawn,FCollisionShape::MakeSphere(45),Params);
    TSet<AActor*> Damaged;
    for (const FHitResult& Hit:Hits)
    {
        auto* Other=Cast<ASurvivalCharacter>(Hit.GetActor());
        if (!Other || Other==this || Damaged.Contains(Other)) continue;
        FHitResult Obstruction;
        if (GetWorld()->LineTraceSingleByChannel(Obstruction,Start,Other->GetActorLocation()+FVector(0,0,30),ECC_Visibility,Params) && Obstruction.GetActor()!=Other) continue;
        Damaged.Add(Other);UGameplayStatics::ApplyDamage(Other,25,Controller,this,UDamageType::StaticClass());
    }
}
float ASurvivalCharacter::TakeDamage(float Amount,const FDamageEvent& Event,AController* Instigator,AActor* Causer)
{
    const float Applied=Stats.Damage(Amount);
    if (Applied>0) Super::TakeDamage(Applied,Event,Instigator,Causer);
    if (Applied>0 && !Stats.Alive()) { GetCharacterMovement()->DisableMovement();
        if (auto* Death=LoadObject<UAnimSequence>(nullptr,TEXT("/Game/Characters/Mannequins/Anims/Death/MM_Death_Front_01.MM_Death_Front_01"))) GetMesh()->PlayAnimation(Death,false);
        StatusMessage=TEXT("Вы погибли. F9 / Загрузить — вернуться к сохранению."); }
    return Applied;
}
bool ASurvivalCharacter::RestoreVitals(float Health,float Stamina)
{
    if (!Stats.Restore(Health,Stamina)) return false;
    GetWorldTimerManager().ClearAllTimersForObject(this);AttackCooldown=0;
    if (Stats.Alive()) {
        GetCharacterMovement()->SetMovementMode(MOVE_Walking);
        GetMesh()->SetAnimationMode(EAnimationMode::AnimationBlueprint);
    }
    return true;
}
void ASurvivalCharacter::Save() { if (auto* Game=Cast<USurvivalGameInstance>(GetGameInstance())) if (!Game->SaveProgress()) StatusMessage=TEXT("Не удалось сохранить прогресс."); }
void ASurvivalCharacter::Load() { if (auto* Game=Cast<USurvivalGameInstance>(GetGameInstance())) if (Game->LoadProgress()) { Game->ApplyLoadedPlayerState(this);StatusMessage=TEXT("Прогресс восстановлен."); } }
void ASurvivalCharacter::TouchPressed(ETouchIndex::Type Finger,FVector Position)
{
    auto* PC=Cast<APlayerController>(Controller);if (!PC) return;
    int32 W=0,H=0;PC->GetViewportSize(W,H);if (!W || !H) return;
    const FVector2D P(Position.X/W,Position.Y/H);
    if (P.X>0.83f && P.Y>0.70f && P.Y<0.90f) { Interact();return; }
    if (P.X>0.83f && P.Y>0.45f && P.Y<=0.70f) { Attack();return; }
    if (P.X>0.66f && P.X<0.83f && P.Y>0.70f) { ToggleSprint();return; }
    if (P.X>0.66f && P.X<0.83f && P.Y>0.48f && P.Y<0.70f) { JumpFinger=static_cast<int32>(Finger);JumpPressed();return; }
    if (P.X>0.66f && P.X<0.83f && P.Y>0.30f && P.Y<0.48f) { ToggleCrouch();return; }
    if (P.X>0.66f && P.X<0.83f && P.Y<0.13f) { Save();return; }
    if (P.X>0.83f && P.Y<0.13f) { Load();return; }
    if (P.X>0.35f && LookFinger<0) { LookFinger=static_cast<int32>(Finger);LastTouch=Position; }
}
void ASurvivalCharacter::TouchReleased(ETouchIndex::Type Finger,FVector Position) {
    if (LookFinger==static_cast<int32>(Finger)) LookFinger=-1;
    if (JumpFinger==static_cast<int32>(Finger)) { StopJumping();JumpFinger=-1; }
}
void ASurvivalCharacter::TouchMoved(ETouchIndex::Type Finger,FVector Position)
{
    if (LookFinger!=static_cast<int32>(Finger)) return;
    const FVector Delta=Position-LastTouch;LastTouch=Position;
    AddControllerYawInput(Delta.X*0.09f);AddControllerPitchInput(Delta.Y*0.09f);
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
