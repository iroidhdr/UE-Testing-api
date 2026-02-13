# Unreal Engine Integration Guide

This guide explains how to connect your Unreal Engine game to the AI Companion API.

## ✅ Prerequisites

1. **Unreal Engine 5.0+** (Works with 4.27 too)
2. **HTTP Module** (Built-in) or **VaRest Plugin** (Easier for Blueprints)
3. **API Server Running** (`python server.py`)

---

## 🗺️ Action Mapping Table

Map the API `type` (string) to your UE Enum (`EActionType`).

| API JSON `type` | UE Enum (`EActionType`)           | Description                  |
| --------------- | --------------------------------- | ---------------------------- |
| `"follow"`      | **`Follow`**                      | Character follows the player |
| `"stop_follow"` | **`HoldPosition`** (or `None`)    | Character stops moving       |
| `"wait"`        | **`HoldPosition`**                | Character holds ground       |
| `"attack"`      | **`Engage`**                      | Character attacks target     |
| `"defend"`      | **`TakeCover`** / **`Overwatch`** | Character defends area       |
| `"assist"`      | **`Regroup`** (or `Follow`)       | Character assists player     |
| `"unknown"`     | **`None`**                        | Action ignored               |

---

## 🔷 Option A: Blueprint (Using VaRest Plugin)

This is the easiest way to test without writing C++.

### 1. Send Request

1. Add **"Construct Json Object"**.
2. Set String Field: `text` = "follow me".
3. Set String Field: `companion_id` = "companion_01".
4. Call **"Call URL"** on the Json Object.
   - **Method**: `POST`
   - **URL**: `http://localhost:5000/api/command`
   - **Content Type**: `application/json`

### 2. Handle Response

1. On the **"Completed"** pin of `Call URL`:
2. Get the **Response Object**.
3. Call **"Get Array Field"** with field name `actions`.
4. Call **"As Object"** on the first element (index 0).
5. Call **"Get String Field"** with field name `type`.

### 3. Switch & Execute

1. Add a **"Switch on String"** node.
2. Add pins: `follow`, `attack`, `wait`, etc.
3. Connect the `type` string to the Switch.
4. From each pin, call your Character's function (e.g., `SetCurrentState(EActionType::Follow)`).

---

## 💻 Option B: C++ (Native HTTP)

For production, you should use C++.

### 1. Add Modules

In `YourProject.Build.cs`:

```csharp
PublicDependencyModuleNames.AddRange(new string[] { "Core", "CoreUObject", "Engine", "InputCore", "HTTP", "Json", "JsonUtilities" });
```

### 2. Define Structs

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
    FString type; // "follow", "attack", etc.

    UPROPERTY()
    FString action_id;
};

USTRUCT()
struct FAICommandResponse
{
    GENERATED_BODY()

    UPROPERTY()
    bool success;

    UPROPERTY()
    TArray<FAIAction> actions;
};
```

### 3. Send Request Function

In your generic AI Controller or Game Instance:

```cpp
#include "HttpModule.h"
#include "Interfaces/IHttpRequest.h"
#include "Interfaces/IHttpResponse.h"
#include "JsonObjectConverter.h"

void AMyAIController::SendCommand(FString CommandText)
{
    // Create Request
    TSharedRef<IHttpRequest, ESPMode::ThreadSafe> Request = FHttpModule::Get().CreateRequest();
    Request->SetURL("http://localhost:5000/api/command");
    Request->SetVerb("POST");
    Request->SetHeader("Content-Type", "application/json");
    Request->SetHeader("User-Agent", "MyCustomApp/1.0"); // Critical: Add Header to bypass ngrok/firewall blocks.

    // Create JSON Body
    FString JsonString;
    TSharedPtr<FJsonObject> JsonObject = MakeShareable(new FJsonObject);
    JsonObject->SetStringField("text", CommandText);
    JsonObject->SetStringField("companion_id", "companion_01");
    TSharedRef<TJsonWriter<>> Writer = TJsonWriterFactory<>::Create(&JsonString);
    FJsonSerializer::Serialize(JsonObject.ToSharedRef(), Writer);

    Request->SetContentAsString(JsonString);

    // Bind Callback
    Request->OnProcessRequestComplete().BindUObject(this, &AMyAIController::OnCommandResponse);
    Request->ProcessRequest();
}

void AMyAIController::OnCommandResponse(FHttpRequestPtr Request, FHttpResponsePtr Response, bool bWasSuccessful)
{
    if (!bWasSuccessful || !Response.IsValid()) return;

    // Parse JSON
    FAICommandResponse ApiResponse;
    if (FJsonObjectConverter::JsonObjectStringToUStruct(Response->GetContentAsString(), &ApiResponse))
    {
        if (ApiResponse.actions.Num() > 0)
        {
            FString ActionType = ApiResponse.actions[0].type;

            // Map to Enum
            if (ActionType == "follow") SetState(EActionType::Follow);
            else if (ActionType == "attack") SetState(EActionType::Engage);
            else if (ActionType == "wait") SetState(EActionType::HoldPosition);

            UE_LOG(LogTemp, Log, TEXT("AI Action: %s"), *ActionType);
        }
    }
}
```

---

## 📝 Example JSON Response

```json
{
  "success": true,
  "actions": [
    {
      "type": "attack",
      "target": { "descriptors": ["enemy"] }
    }
  ]
}
```
