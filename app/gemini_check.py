
import os
from dotenv import load_dotenv
from google import genai
from google.genai import errors

# --------------------------------------------------
# 1. Load environment variables
# --------------------------------------------------

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    print("ERROR: GEMINI_API_KEY not found.")
    print("Please check your .env file.")
    raise SystemExit(1)

# --------------------------------------------------
# 2. Initialize Gemini client
# --------------------------------------------------

try:
    client = genai.Client(api_key=api_key)
    print("Gemini client initialized successfully.")

except Exception as error:
    print("Client initialization failed:", error)
    raise SystemExit(1)

# --------------------------------------------------
# 3. Fetch available models
# --------------------------------------------------

print("\nFetching available Gemini models...\n")

try:
    available_models = []

    for model in client.models.list():
        supported_actions = model.supported_actions or []

        if "generateContent" in supported_actions:
            model_name = model.name

            if model_name:
                available_models.append(model_name)

    if not available_models:
        print("No models supporting generateContent were found.")
        raise SystemExit(1)

except errors.APIError as error:
    print("Unable to retrieve models.")
    print("API Error:", error)
    raise SystemExit(1)

except Exception as error:
    print("Unexpected error while listing models:", error)
    raise SystemExit(1)

# --------------------------------------------------
# 4. Display available models
# --------------------------------------------------

print("Models supporting generateContent:")

for index, model_name in enumerate(available_models, start=1):
    print(f"{index}. {model_name}")

# --------------------------------------------------
# 5. Test available models
# --------------------------------------------------

print("\nTesting Gemini model connectivity...\n")

successful_model = None

for model_name in available_models:

    print(f"Testing: {model_name}")

    try:
        response = client.models.generate_content(
            model=model_name,
            contents="Explain what an embedded system is in two sentences."
        )

        if response.text:
            print("\nSUCCESS: Gemini API is working!")
            print("Model:", model_name)
            print("\nResponse:")
            print(response.text)

            successful_model = model_name
            break

        else:
            print("Model returned an empty response.")

    except errors.APIError as error:
        print("Model request failed:", error)

        if error.code == 429:
            print("Reason: API quota or rate limit exceeded.")

        elif error.code == 503:
            print("Reason: Model temporarily unavailable.")

        elif error.code == 404:
            print("Reason: Model not found or unsupported.")

        print("-" * 60)

    except Exception as error:
        print("Unexpected error:", error)
        print("-" * 60)

# --------------------------------------------------
# 6. Final result
# --------------------------------------------------

print("\n" + "=" * 60)

if successful_model:
    print("GEMINI CONNECTION VERIFIED")
    print("Working model:", successful_model)
    print("\nUse this model name in app/chatbot.py.")

else:
    print("NO MODEL RESPONDED SUCCESSFULLY.")
    print("Check your Google AI Studio quota and model availability.")

print("=" * 60)
