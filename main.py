from pathlib import Path
import google.generativeai as genai
from flask import Flask, render_template, request, jsonify
import os
import random
import string
from dotenv import load_dotenv
load_dotenv()

api_key = os.environ.get('API_KEY')

app = Flask(__name__,template_folder='templates')

@app.route('/')
def index():
    return render_template('newui.html')

@app.route('/api/image-to-html', methods=['POST'])
def image_to_html():
    if 'image' not in request.files:
        return jsonify({'error': 'No image provided'}), 400

    file = request.files['image']

    if file.filename == '':
        return jsonify({'error': 'No selected image'}), 400


    filename = generate_random_filename()

    
    file_path = os.path.join('uploads', filename)
    file.save(file_path)

    
    demo_output = generate_web_page_code(file_path)

    return jsonify({'html': demo_output})

def generate_random_filename():
    letters_and_digits = string.ascii_letters + string.digits
    return ''.join(random.choice(letters_and_digits) for _ in range(10)) + '.jpg'

def generate_demo_output():
    
    return '<div class="demo-output">Generated HTML and CSS</div>'




def generate_web_page_code(image_path):
    # Configure API key
    genai.configure(api_key=api_key)

    # Set up the model
    generation_config = {
        "temperature": 0.9,
        "top_p": 1,
        "top_k": 32,
        "max_output_tokens": 4096,
    }

    safety_settings = [
        {
            "category": "HARM_CATEGORY_HARASSMENT",
            "threshold": "BLOCK_MEDIUM_AND_ABOVE"
        },
        {
            "category": "HARM_CATEGORY_HATE_SPEECH",
            "threshold": "BLOCK_MEDIUM_AND_ABOVE"
        },
        {
            "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
            "threshold": "BLOCK_MEDIUM_AND_ABOVE"
        },
        {
            "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
            "threshold": "BLOCK_MEDIUM_AND_ABOVE"
        },
    ]

    model = genai.GenerativeModel(model_name="gemini-pro-vision",
                                  generation_config=generation_config,
                                  safety_settings=safety_settings)

    
    if not (img := Path(image_path)).exists():
        raise FileNotFoundError(f"Could not find image: {img}")

    image_parts = [
        {
            "mime_type": "image/png",
            "data": img.read_bytes()
        },
    ]
    prompt_parts = [
        "You are an expert Tailwind developer\nYou take screenshots of a reference web page from the user, and then build single page apps \nusing Tailwind, HTML and JS.\nYou might also be given a screenshot(The second image) of a web page that you have already built, and asked to\nupdate it to look more like the reference image(The first image).\n\n- Make sure the app looks exactly like the screenshot.\n- Pay close attention to background color, text color, font size, font family, \npadding, margin, border, etc. Match the colors and sizes exactly.\n- Use the exact text from the screenshot.\n- Do not add comments in the code such as \"<!-- Add other navigation links as needed -->\" and \"<!-- ... other news items ... -->\" in place of writing the full code. WRITE THE FULL CODE.\n- Repeat elements as needed to match the screenshot. For example, if there are 15 items, the code should have 15 items. DO NOT LEAVE comments like \"<!-- Repeat for each news item -->\" or bad things will happen.\n- For images, use placeholder images from https://placehold.co and include a detailed description of the image in the alt text so that an image generation AI can generate the image later.\n\nIn terms of libraries,\n\n- Use this script to include Tailwind: <script src=\"https://cdn.tailwindcss.com\"></script>\n- You can use Google Fonts\n- Font Awesome for icons: <link rel=\"stylesheet\" href=\"https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.3/css/all.min.css\"></link>\n\nReturn only the full code in <html></html> tags.\nDo not include markdown \"```\" or \"```html\" at the start or end.\n\n",
        image_parts[0],
        "\nGenerate code for a web page that looks exactly like this.\n ",
    ]

    response = model.generate_content(prompt_parts)
    result = "\n".join(part.text for part in response.parts)
    return f'{result}'

if __name__ == '__main__':
    
    os.makedirs('uploads', exist_ok=True)

    app.run(debug=True)
