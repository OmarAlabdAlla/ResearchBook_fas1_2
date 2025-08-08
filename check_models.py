#!/usr/bin/env python3

import requests
import json

def check_available_models():
    """Check available models via /v1/models endpoint"""
    
    url = "https://anast.ita.chalmers.se:4000/v1/models"
    api_key = "sk-u_7AVwCgIBRZF9IXwzPqtA"
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    try:
        print("🔍 Checking available models...")
        response = requests.get(url, headers=headers, timeout=30, verify=False)
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Successfully retrieved models!")
            
            if 'data' in result:
                models = result['data']
                print(f"📋 Found {len(models)} available models:")
                
                for model in models:
                    model_id = model.get('id', 'unknown')
                    model_object = model.get('object', 'unknown')
                    print(f"   • {model_id} ({model_object})")
                
                # Try first available model
                if models:
                    test_model_name = models[0]['id']
                    print(f"\n🧪 Testing with first available model: {test_model_name}")
                    return test_with_model(test_model_name)
            else:
                print("⚠️ Unexpected response format:")
                print(json.dumps(result, indent=2))
        
        else:
            print(f"❌ Failed to get models: {response.status_code}")
            print(f"Error: {response.text}")
            
    except Exception as e:
        print(f"❌ Error checking models: {e}")
        
    return False

def test_with_model(model_name):
    """Test chat completion with specific model"""
    
    url = "https://anast.ita.chalmers.se:4000/v1/chat/completions"
    api_key = "sk-u_7AVwCgIBRZF9IXwzPqtA"
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": model_name,
        "messages": [
            {
                "role": "user", 
                "content": "Hello! This is a test message. Please respond with 'API test successful' to confirm the connection works."
            }
        ],
        "max_tokens": 100,
        "temperature": 0.7
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=30, verify=False)
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Chat completion successful!")
            
            if 'choices' in result and len(result['choices']) > 0:
                message_content = result['choices'][0]['message']['content']
                print(f"🤖 AI Response: {message_content}")
                
                if 'usage' in result:
                    usage = result['usage']
                    print(f"📊 Token Usage: {usage}")
                
                return True
            else:
                print("⚠️ Unexpected response format")
                print(json.dumps(result, indent=2))
        
        else:
            print(f"❌ Chat completion failed: {response.status_code}")
            print(f"Error: {response.text}")
            
    except Exception as e:
        print(f"❌ Error in chat completion: {e}")
        
    return False

if __name__ == "__main__":
    check_available_models()