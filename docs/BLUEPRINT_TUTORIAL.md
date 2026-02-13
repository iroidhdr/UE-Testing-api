# 📘 Unreal Engine Blueprint Integration Tutorial

This guide shows you **exactly** how to connect your API to Unreal Engine using Blueprints.

## 🛠️ Prerequisite: Install "VaRest" Plugin

Unreal's built-in HTTP nodes are basic. For JSON, the **VaRest** plugin is the standard (and free).

1. Open **Epic Games Launcher**.
2. Go to **Marketplace** → Search for **"VaRest"**.
3. Install it to your Engine version.
4. Open your UE Project → **Edit** → **Plugins**.
5. Enable **VaRest** → Restart Editor.

---

## 🚀 Step 1: Create the API Function

Create a new **Custom Event** in your Character Blueprint (e.g., `BP_AICharacter`).

1. **Right-click** in Event Graph → `Add Custom Event`.
2. Name it: **`SendAICommand`**.
3. Add an **Input** of type `String` named **`CommandText`**.

---

## 📡 Step 2: Construct & Send JSON

Now build the request logic connected to your event.

1. **Construct Json Object** (VaRest)
   - node: `Construct Json Object` (Promote return value to a local variable if needed, or just link it).

2. **Set Text Field**
   - Drag from the Json Object → `Set String Field`.
   - **Field Name**: `"text"`
   - **Value**: Plug in your `CommandText` input pin.

3. **Set Companion ID**
   - Drag from Json Object → `Set String Field`.
   - **Field Name**: `"companion_id"`
   - **Value**: `"companion_01"`.

4. **Send Request**
   - Drag from Json Object → `Call URL`.
   - **Method**: `POST`
   - **URL**: `http://localhost:5000/api/command` (OR your remote ngrok URL)
   - **Content Type**: `application/json`
   - **Header**: Add Header `User-Agent` = `MyCustomApp/1.0` (Critical for ngrok/firewall bypass).

---

## 📥 Step 3: Handle the Response

The `Call URL` node has a **"Completed"** execution pin. This runs when the API replies.

1. **Get Response Object**
   - The `Call URL` node gives you a `Request` and `Response`. Use the `Response` (VaRest Request JSON Object).

2. **Get Actions Array**
   - Drag from Response → `Get Array Field`.
   - **Field Name**: `"actions"` (Matches our API JSON).

3. **Get First Action**
   - Drag from Array → `Get` (Index `0`).
   - Drag from Item → `As Json Object` (Casts the array item to a JSON object).

4. **Get Action Type**
   - Drag from that Action Object → `Get String Field`.
   - **Field Name**: `"type"` (This contains "follow", "attack", etc.).

---

## 🎮 Step 4: Execute Logic (The Switch)

Now you have the string (e.g., "attack"). You need to tell your character what to do.

1. **Switch on String**
   - Drag from the String output → `Switch on String`.
   - **Uncheck** "Has Default Pin" (optional).
   - Click **Add Pin** for each command:
     - `follow`
     - `stop_follow`
     - `wait`
     - `attack`
     - `defend`

2. **Connect to Logic**
   - **`follow` Pin** → Call your `StartFollowing` function.
   - **`attack` Pin** → Call `EquipWeapon` & `MoveToTarget`.
   - **`wait` Pin** → Call `StopMovement`.

---

## 🧪 How to Test It

1. In your **Level Blueprint** or a **UMG Widget**:
2. Add a `keyboard T` event.
3. Get your AI Character reference.
4. Call **`SendAICommand`**.
5. Input: `"follow me"`.
6. **Play Game** → Press **T**.
7. Watch your Server Terminal — it should show the request!
8. Watch your AI Character — after ~6 seconds, it should move!

---

## 🔍 Visual Summary of Nodes

```
[CustomEvent: SendAICommand]
      ↓
[Construct Json Object]
      ↓
[SetStringField: "text" = Input]
      ↓
[SetStringField: "companion_id" = "01"]
      ↓
[Call URL "http://localhost:5000..."]
      ↓ (Completed)
[Get Response] → [Get Array Field "actions"]
                        ↓
                 [Get Index 0] → [As Json Object]
                                        ↓
                                 [Get String Field "type"]
                                        ↓
                                 [Switch on String]
                                  ├── "follow" → [AI MoveTo]
                                  ├── "attack" → [AttackTarget]
                                  └── "wait"   → [StopMove]
```
