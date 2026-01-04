# Bot Response Configuration - Frontend Integration Guide

## ✅ Backend Complete!

The backend now supports configurable bot response settings:

### New Fields Added to Service Model:
- **max_response_tokens** (Integer, 100-1000, default: 300)
- **response_temperature** (Float, 0.0-1.0, default: 0.7)  
- **response_timeout** (Integer, 10-120 seconds, default: 30)

### API Endpoints Updated:
- ✅ `GET /api/bot/config` - Returns config including new fields
- ✅ `PUT /api/bot/config` - Accepts new fields for update
- ✅ Chat endpoints use service settings automatically

---

## 🎨 Frontend Integration

### 1. Add to Bot Configuration Form

In your bot configuration component, add these form fields:

```jsx
// Response Configuration Section
<div className="space-y-4">
  <h3 className="text-lg font-semibold">Response Configuration</h3>
  
  {/* Max Response Tokens */}
  <div>
    <label className="block text-sm font-medium mb-2">
      Max Response Length
      <span className="text-gray-500 ml-2">(100-1000 tokens)</span>
    </label>
    <input
      type="range"
      min="100"
      max="1000"
      step="50"
      value={config.max_response_tokens || 300}
      onChange={(e) => setConfig({
        ...config,
        max_response_tokens: parseInt(e.target.value)
      })}
      className="w-full"
    />
    <div className="flex justify-between text-xs text-gray-500 mt-1">
      <span>Short (100)</span>
      <span className="font-semibold">{config.max_response_tokens || 300}</span>
      <span>Long (1000)</span>
    </div>
    <p className="text-xs text-gray-600 mt-1">
      Lower = Faster responses, Higher = More detailed answers
    </p>
  </div>

  {/* Response Temperature */}
  <div>
    <label className="block text-sm font-medium mb-2">
      Response Creativity
      <span className="text-gray-500 ml-2">(0.0-1.0)</span>
    </label>
    <input
      type="range"
      min="0"
      max="1"
      step="0.1"
      value={config.response_temperature || 0.7}
      onChange={(e) => setConfig({
        ...config,
        response_temperature: parseFloat(e.target.value)
      })}
      className="w-full"
    />
    <div className="flex justify-between text-xs text-gray-500 mt-1">
      <span>Precise (0.0)</span>
      <span className="font-semibold">{config.response_temperature || 0.7}</span>
      <span>Creative (1.0)</span>
    </div>
    <p className="text-xs text-gray-600 mt-1">
      Lower = More consistent, Higher = More varied responses
    </p>
  </div>

  {/* Response Timeout */}
  <div>
    <label className="block text-sm font-medium mb-2">
      Response Timeout
      <span className="text-gray-500 ml-2">(10-120 seconds)</span>
    </label>
    <select
      value={config.response_timeout || 30}
      onChange={(e) => setConfig({
        ...config,
        response_timeout: parseInt(e.target.value)
      })}
      className="w-full px-3 py-2 border rounded"
    >
      <option value="10">10 seconds (Very Fast)</option>
      <option value="20">20 seconds (Fast)</option>
      <option value="30">30 seconds (Normal)</option>
      <option value="45">45 seconds (Slow)</option>
      <option value="60">60 seconds (Very Slow)</option>
      <option value="90">90 seconds (Maximum)</option>
      <option value="120">120 seconds (Ultra Long)</option>
    </select>
    <p className="text-xs text-gray-600 mt-1">
      Maximum wait time before giving up on response
    </p>
  </div>
</div>
```

### 2. Update API Calls

When saving configuration:

```javascript
const updateBotConfig = async (configData) => {
  const response = await fetch('/api/bot/config', {
    method: 'PUT',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`
    },
    body: JSON.stringify({
      // ... existing fields
      max_response_tokens: configData.max_response_tokens,
      response_temperature: configData.response_temperature,
      response_timeout: configData.response_timeout
    })
  });
  
  return await response.json();
};
```

### 3. Display Current Settings

Show current settings in config view:

```jsx
<div className="bg-blue-50 p-4 rounded-lg">
  <h4 className="font-semibold mb-2">Current Response Settings</h4>
  <div className="space-y-1 text-sm">
    <p>• Max Length: <strong>{config.max_response_tokens || 300} tokens</strong></p>
    <p>• Creativity: <strong>{config.response_temperature || 0.7}</strong></p>
    <p>• Timeout: <strong>{config.response_timeout || 30} seconds</strong></p>
  </div>
</div>
```

---

## 📋 Default Values

If not set, the system uses these defaults:
- **max_response_tokens**: 300 (moderate length)
- **response_temperature**: 0.7 (balanced)
- **response_timeout**: 30 seconds

---

## 🎯 Recommended Settings

### For Quick Support (Fast responses):
- Tokens: 100-200
- Temperature: 0.3-0.5
- Timeout: 10-20 seconds

### For Detailed Explanations:
- Tokens: 500-800
- Temperature: 0.7-0.9
- Timeout: 45-60 seconds

### Balanced (Recommended):
- Tokens: 300
- Temperature: 0.7
- Timeout: 30 seconds

---

## ✅ Testing

1. Update bot config with new settings
2. Send a chat message
3. Backend logs will show:
   ```
   [Ollama] Processing with max_tokens=500, temperature=0.8
   ```
4. Response will respect the configured limits

---

## 🔧 Backend API Response

GET `/api/bot/config` now returns:

```json
{
  "config": {
    "bot_name": "...",
    "welcome_message": "...",
    "max_response_tokens": 300,
    "response_temperature": 0.7,
    "response_timeout": 30,
    ...
  }
}
```

PUT `/api/bot/config` accepts these fields and validates:
- `max_response_tokens`: Clamped to 100-1000
- `response_temperature`: Clamped to 0.0-1.0
- `response_timeout`: Clamped to 10-120 seconds

---

**Backend is ready! Just add the UI fields in your frontend bot configuration page.** 🚀
