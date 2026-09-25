#pragma once
#include "CoreMinimal.h"
#include "GameFramework/Character.h"
#include "Core/Vitals.h"
#include "Core/Combat.h"
#include "SurvivalCharacter.generated.h"
class USpringArmComponent;
class UCameraComponent;
class ASurvivalInteraction;
class UAnimSequence;
class ACameraActor;
class UStaticMeshComponent;
class UAudioComponent;
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
    UFUNCTION(BlueprintCallable,Category="Actions") void ToggleSprint();
    UFUNCTION(BlueprintCallable,Category="Actions") void Save();
    UFUNCTION(BlueprintCallable,Category="Actions") void Load();
    UFUNCTION(BlueprintPure,Category="Actions") ASurvivalInteraction* GetFocusedInteraction() const;
    UPROPERTY(EditAnywhere,BlueprintReadWrite,Category="Appearance") FName AvatarRole=TEXT("Arsen");
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
    void BeginStory(FName Id,AActor* Subject);
    void AdvanceStory();
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
    bool bHumanAvatar=false;
    float FootstepDelay=0;
    FName CurrentStory;
    void ConfigureHuman();
    void UpdateHuman();
    void RefreshWeapon();
    void Shoot();
    void SpeakStoryLine();
    survival::Vitals Stats;
    bool bSprintRequested=false;
    float AttackCooldown=0;
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
