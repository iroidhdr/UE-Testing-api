# Unreal Engine Integration Guide

This guide explains how to connect your Unreal Engine game to the AI Companion API.

## ✅ Prerequisites

1. **Unreal Engine 5.0+** (Works with 4.27 too)
2. **HTTP Module** (Built-in) or **VaRest Plugin** (Easier for Blueprints)
3. **API Server Running** (`python server.py`)

---

## 🗺️ Action Mapping Table (5.2 Update)

Map the API `type` (string) to your UE Enum (`EActionType`).

| **Interaction** | | |
| `"interact"` | `Interact` | Use object (door/switch) |
| `"pick_up"` | `PickUp` | Pick up item |
| `"use_item_on"` | `UseItem` | Use inventory item |
| `"throw_equipment"` | `Throw` | Throw grenade/utility |
| **Other** | | |
| `"cancel"` | `Cancel` | Stop current action |
| `"unknown"` | `None` | Action ignored |

---

## 🔷 Option A: Blueprint (Using VaRest Plugin)

This is the easiest way to test without writing C++.

### 1. Send Request

1. Add **"Construct Json Object"**.
2. Set String Field: `text` = "suppress that area".
3. Call **"Call URL"** on the Json Object.
   - **Method**: `POST`
   - **URL**: `http://localhost:5000/api/command`
   - **Content Type**: `application/json`

### 2. Handle Response

1. On **"Completed"**:
2. Get **Response Object**.
3. Call **"Get Array Field"** (`actions`).
4. Get Element 0 **(As Object)**.
5. **CRITICAL:** Check `status` (Boolean).
   - **True**: Action Succeeded.
   - **False**: Action Failed (Check `reason` string).
6. Switch on `action_type_executed` to trigger game logic.

---

## 💻 Option B: C++ (Native HTTP)

For production, you should use C++.

### 1. Define Structs

In a header file (`AICommandTypes.h`):

```cpp
#pragma once
#include "CoreMinimal.h"
#include "AICommandTypes.generated.h"

USTRUCT()
struct FAIAction
{
    GENERATED_BODY()

    UPROPERTY()
    FString action_type_executed; // "follow", "suppress", etc.

    UPROPERTY()
    FString spatial_direction; // "Front", "Left", "Right", "Back"

    UPROPERTY()
    bool status; // true/false

    UPROPERTY()
    FString reason; // e.g. "already_following"

    UPROPERTY()
    FString response_id; // "RESP_FOLLOW_ACCEPT"
};

USTRUCT()
struct FAICommandResponse
{
    GENERATED_BODY()

    UPROPERTY()
    bool success;

    UPROPERTY()
    FString dialogue;

    UPROPERTY()
    TArray<FAIAction> actions;
};
```

### 2. Parse Response

In your `OnCommandResponse` function:

```cpp
void AMyAIController::OnCommandResponse(FHttpRequestPtr Request, FHttpResponsePtr Response, bool bWasSuccessful)
{
    if (!bWasSuccessful || !Response.IsValid()) return;

    // Parse JSON
    FAICommandResponse ApiResponse;
    if (FJsonObjectConverter::JsonObjectStringToUStruct(Response->GetContentAsString(), &ApiResponse))
    {
        // 1. Show Dialogue
        ShowDialogue(ApiResponse.dialogue);

        // 2. Execute Action (if valid)
        if (ApiResponse.actions.Num() > 0)
        {
            FAIAction& Action = ApiResponse.actions[0];

            if (Action.status)
            {
                // Execute Game Logic
                if (Action.action_type_executed == "suppress") SuppressArea();
                else if (Action.action_type_executed == "follow") StartFollowing();
            }
            else
            {
                // Handle Failure (Optional)
                UE_LOG(LogTemp, Warning, TEXT("Action Failed: %s"), *Action.reason);
            }
        }
    }
}
```

---

## 📝 Example JSON Response

```json
{
  "success": true,
  "dialogue": "Laying down suppressing fire!",
  "response_id": "RESP_SUPPRESS_ACCEPT",
  "command_id": "cmd_001",
  "action_type_executed": "suppress",
  "spatial_direction": "Front",
  "action_status": true,
  "action_reason": null,
  "processing_time_ms": 1250
}
```
