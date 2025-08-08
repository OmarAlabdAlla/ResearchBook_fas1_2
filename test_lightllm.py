#!/usr/bin/env python3

import requests
import json

def test_lightllm_api():
    """Test LightLLM API credentials and functionality"""
    
    # API configuration
    url = "https://anast.ita.chalmers.se:4000/v1/chat/completions"
    api_key = "sk-u_7AVwCgIBRZF9IXwzPqtA"
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    # Test payload - simple chat completion
    payload = {
        "model": "gpt-3.5-turbo",  # Common model name, might need adjustment
        "messages": [
            {
                "role": "user", 
                "content": "Hello! Can you help me test this API connection? Please respond with a brief confirmation."
            }
        ],
        "max_tokens": 100,
        "temperature": 0.7
    }
    
    try:
        print("🔍 Testing LightLLM API connection...")
        print(f"   URL: {url}")
        print(f"   Using API key: {api_key[:10]}...")
        
        response = requests.post(url, headers=headers, json=payload, timeout=30, verify=False)
        
        print(f"   Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ API Connection Successful!")
            
            # Extract response content
            if 'choices' in result and len(result['choices']) > 0:
                message_content = result['choices'][0]['message']['content']
                print(f"   Response: {message_content}")
                
                # Show usage info if available
                if 'usage' in result:
                    usage = result['usage']
                    print(f"   Token Usage: {usage}")
                
                return True, result
            else:
                print("⚠️ Unexpected response format:")
                print(json.dumps(result, indent=2))
                return False, result
                
        else:
            print(f"❌ API Request Failed: {response.status_code}")
            print(f"   Error: {response.text}")
            
            # Try to parse error response
            try:
                error_data = response.json()
                print("   Error details:")
                print(json.dumps(error_data, indent=2))
            except:
                pass
            
            return False, response.text
            
    except requests.exceptions.SSLError as e:
        print(f"❌ SSL Error: {e}")
        print("   Retrying without SSL verification...")
        
        # Retry without SSL verification
        try:
            response = requests.post(url, headers=headers, json=payload, timeout=30, verify=False)
            print(f"   Status Code: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print("✅ API Connection Successful (no SSL verification)!")
                message_content = result['choices'][0]['message']['content']
                print(f"   Response: {message_content}")
                return True, result
            else:
                print(f"❌ Still failed: {response.status_code}")
                return False, response.text
                
        except Exception as retry_e:
            print(f"❌ Retry also failed: {retry_e}")
            return False, str(retry_e)
            
    except requests.exceptions.Timeout:
        print("❌ Request timed out (30s)")
        return False, "Timeout"
        
    except requests.exceptions.ConnectionError as e:
        print(f"❌ Connection Error: {e}")
        return False, str(e)
        
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False, str(e)

def test_different_models():
    """Test with different model names in case the default doesn't work"""
    
    url = "https://anast.ita.chalmers.se:4000/v1/chat/completions"
    api_key = "sk-u_7AVwCgIBRZF9IXwzPqtA"
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    # Try different common model names
    models_to_try = [
        "gpt-4",
        "gpt-3.5-turbo", 
        "llama-2",
        "vicuna",
        "claude",
        "mistral",
        "default"
    ]
    
    for model in models_to_try:
        payload = {
            "model": model,
            "messages": [{"role": "user", "content": "Test message"}],
            "max_tokens": 50
        }
        
        try:
            response = requests.post(url, headers=headers, json=payload, timeout=10, verify=False)
            if response.status_code == 200:
                print(f"✅ Model '{model}' works!")
                return model
            else:
                print(f"❌ Model '{model}' failed: {response.status_code}")
        except Exception as e:
            print(f"❌ Model '{model}' error: {e}")
    
    return None

if __name__ == "__main__":
    # Test main API
    success, result = test_lightllm_api()
    
    if not success:
        print("\n🔄 Trying different model names...")
        working_model = test_different_models()
        
        if working_model:
            print(f"\n✅ Found working model: {working_model}")
        else:
            print("\n❌ No working models found")
    
    print("\n📋 API Test Summary:")
    print("   Endpoint:", "https://anast.ita.chalmers.se:4000/v1/chat/completions")
    print("   Key format appears valid:", "sk-u_7AVwCgIBRZF9IXwzPqtA"[:10] + "...")
    print("   Success:", "✅" if success else "❌")