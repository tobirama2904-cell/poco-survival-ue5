#pragma once
#include "CoreMinimal.h"
#include "GameFramework/Character.h"
#include "Core/Vitals.h"
#include "SurvivalCharacter.generated.h"
class USpringArmComponent;
class UCameraComponent;
class ASurvivalInteraction;
class UAnimSequence;
UCLASS()
class POCOSURVIVAL_API ASurvivalCharacter : public ACharacter
{
    GENERATED_BODY()
public:
    ASurvivalCharacter();
    virtual void BeginPlay() override;
    virtual void PossessedBy(AController* NewController) override;
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
private:
    survival::Vitals Stats;
    bool bSprintRequested=false;
    float AttackCooldown=0;
    int32 LookFinger=-1;
    FVector LastTouch=FVector::ZeroVector;
    UPROPERTY() TObjectPtr<UAnimSequence> AttackAnimation;
    void Forward(float Value); void Right(float Value); void Turn(float Value); void Look(float Value);
    void SprintOn(); void SprintOff(); void JumpPressed(); void ToggleCrouch();
    void TouchPressed(ETouchIndex::Type Finger,FVector Position);
    void TouchReleased(ETouchIndex::Type Finger,FVector Position);
    void TouchMoved(ETouchIndex::Type Finger,FVector Position);
    void DeliverMelee();
};
