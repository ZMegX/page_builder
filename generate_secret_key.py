"""
Generate a new Django SECRET_KEY
Run this script to generate a new secret key for your .env file
"""
from django.core.management.utils import get_random_secret_key

if __name__ == "__main__":
    new_key = get_random_secret_key()
    print("\n" + "="*70)
    print("🔑 NEW DJANGO SECRET KEY GENERATED")
    print("="*70)
    print("\nCopy this line to your .env file:")
    print(f"\nDJANGO_SECRET_KEY={new_key}")
    print("\n" + "="*70)
    print("⚠️  IMPORTANT:")
    print("1. Add this to your .env file")
    print("2. Never commit the .env file to Git")
    print("3. Add the same key to your Render environment variables")
    print("="*70 + "\n")
