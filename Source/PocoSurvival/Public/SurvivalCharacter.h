#pragma once
#include "CoreMinimal.h"
#include "GameFramework/Character.h"
#include "Core/Vitals.h"
#include "Core/Combat.h"
#include "Core/MeleeAction.h"
#include "Core/FieldSurvival.h"
#include "SurvivalCharacter.generated.h"
class USpringArmComponent;
class UCameraComponent;
class ASurvivalInteraction;
class UAnimSequence;
class ACameraActor;
class UStaticMeshComponent;
class UAudioComponent;
class USpotLightComponent;
UCLASS()
class POCOSURVIVAL_API ASurvivalCharacter : public ACharacter
{
    GENERATED_BODY()
public:
    ASurvivalCharacter();
    virtual void BeginPlay() override;
    virtual void PossessedBy(AController* NewController) override;
    virtual void FellOutOfWorld(const UDamageType& DamageType) override;
    virtual void Tick(float DeltaSeconds) override;
    virtual void SetupPlayerInputComponent(UInputComponent* Input) override;
    virtual float TakeDamage(float Amount,const FDamageEvent& Event,AController* Instigator,AActor* Causer) override;
    UPROPERTY(VisibleAnywhere,BlueprintReadOnly,Category="View") TObjectPtr<USpringArmComponent> CameraArm;
    UPROPERTY(VisibleAnywhere,BlueprintReadOnly,Category="View") TObjectPtr<UCameraComponent> Camera;
    UPROPERTY(BlueprintReadOnly,Category="UI") FString StatusMessage;
    UFUNCTION(BlueprintPure,Category="Vitals") float GetHealth() const { return Stats.health; }
    UFUNCTION(BlueprintPure,Category="Vitals") float GetStamina() const { return Stats.stamina; }
    UFUNCTION(BlueprintPure,Category="Vitals") bool IsAlive() const { return Stats.Alive(); }
    UFUNCTION(BlueprintCallable,Category="Vitals") bool RestoreVitals(float Health,float Stamina);
    UFUNCTION(BlueprintCallable,Category="Actions") void Interact();
    UFUNCTION(BlueprintCallable,Category="Actions") void Attack();
    bool IsMeleeActive() const { return Melee.active; }
    void CancelMelee() { Melee.Cancel();bMeleeImpactFrame=false;if(bHumanAvatar)UpdateHuman(); }
    bool HasMeleeMotion() const;
    bool IsMeleePosePlaying() const;
    uint32 MeleeImpactEvents=0;
    FName RightHandBone() const;
    UFUNCTION(BlueprintCallable,Category="Actions") void ToggleSprint();
    UFUNCTION(BlueprintCallable,Category="Actions") void Save();
    UFUNCTION(BlueprintCallable,Category="Actions") void Load();
    UFUNCTION(BlueprintPure,Category="Actions") ASurvivalInteraction* GetFocusedInteraction() const;
    UPROPERTY(EditAnywhere,BlueprintReadWrite,Category="Appearance") FName AvatarRole=TEXT("Daniel");
    UFUNCTION(BlueprintPure,Category="Appearance") bool HasHumanAvatar() const { return bHumanAvatar; }
    UFUNCTION(BlueprintCallable,Category="Combat") void ReloadWeapon();
    UFUNCTION(BlueprintCallable,Category="Combat") void SwitchWeapon();
    UFUNCTION(BlueprintCallable,Category="Combat") void ThrowBottle();
    int32 EarnedRounds() const;
    int32 EarnedBottles() const;
    const survival::CombatSnapshot& CombatState() const { return Equipment.state; }
    bool RestoreCombat(const survival::CombatSnapshot& State);
    bool IsReloading() const { return Equipment.reloading>0; }
    void SyncEquipment() { RefreshWeapon(); }
    const survival::Trauma& Wounds() const { return Trauma; }
    bool RestoreWounds(const survival::Trauma& T) { if(!T.Valid())return false;Trauma=T;return true; }
    bool bBowEquipped=false,bAiming=false;
    void ReleaseAttack();
    void UseBandage();
    void ToggleAim();
    void FieldAction(int32 Action);
    void BeginFilm(int32 Index,AActor* Subject);
    void BeginCountyStory(int32 Arc,int32 Beat);
    void BeginJourneyConversation(int32 Id);
    void CompanionCommand(int32 Action);
    bool ApplySupportResult(float Health,const survival::Trauma& Wounds);
    bool bCompanionPanel=false;
    float LastImpactTime=-1000;
    bool IsJourneyConversation() const { return ActiveJourney>=0; }
    void PauseBanter(bool Pause);
    bool IsBanterPaused() const { return bBanterPaused; }
    bool bConversing=false;
    void ToggleControlEditor();
    void ToggleFlashlight();
    bool bEditingControls=false;
    bool IsCinematicLocked() const { return bStoryActive && bStoryLocksMovement; }
    void BeginStory(FName Id,AActor* Subject,bool Cinematic=true);
    UFUNCTION() void AdvanceStory();
    void EndStory();
    void ToggleJournal();
    bool bJournalOpen=false;
    bool bStoryActive=false;
    FString StorySpeaker;
    TArray<FString> StoryLines;
    int32 StoryLine=0;
private:
    UPROPERTY() TObjectPtr<ACameraActor> StoryCamera;
    UPROPERTY() TObjectPtr<UAudioComponent> StoryAudio;
    UPROPERTY() TObjectPtr<UStaticMeshComponent> WeaponMesh;
    UPROPERTY() TMap<FName,TObjectPtr<UAnimSequence>> HumanAnimations;
    UPROPERTY() TObjectPtr<UAnimSequence> PlayingHumanAnimation;
    survival::Combat Equipment;
    survival::Trauma Trauma;
    survival::BowDraw Bow;
    int32 AttackFinger=-1;
    FTimerHandle FilmLineTimer;
    int32 ActiveFilm=-1,ActiveJourney=-1;
    bool bCountyStory=false,bBanterPaused=false;
    bool bHumanAvatar=false;
    float FootstepDelay=0;
    FName CurrentStory;
    UPROPERTY() TObjectPtr<USpotLightComponent> Flashlight;
    bool bStoryLocksMovement=true;
    bool bMouseSettingsDrag=false;
    int32 ControlDragFinger=-1,ControlDragIndex=-1;
    void MouseSettingsPressed();
    void MouseSettingsReleased();
    void ConfigureHuman();
    void UpdateHuman();
    void RefreshWeapon();
    void Shoot();
    void SpeakStoryLine();
    survival::Vitals Stats;
    bool bSprintRequested=false;
    float AttackCooldown=0;
    survival::MeleeAction Melee;
    bool bMeleeCrouched=false,bMeleeImpactFrame=false;
    int32 LookFinger=-1;
    int32 JumpFinger=-1;
    FVector LastTouch=FVector::ZeroVector;
    UPROPERTY() TObjectPtr<UAnimSequence> AttackAnimation;
    void Forward(float Value); void Right(float Value); void Turn(float Value); void Look(float Value);
    void SprintOn(); void SprintOff(); void JumpPressed(); void ToggleCrouch();
    void TouchPressed(ETouchIndex::Type Finger,FVector Position);
    void TouchReleased(ETouchIndex::Type Finger,FVector Position);
    void TouchMoved(ETouchIndex::Type Finger,FVector Position);
    void DeliverMelee();
};
